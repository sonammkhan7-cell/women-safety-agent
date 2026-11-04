import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.journey import Journey, JourneyStatus
from app.models.user import User, VerificationStatus
from app.models.companion import CompanionRequest, CompanionGroup, RequestStatus, GroupStatus
from app.utils.geo import (
    haversine_distance, calculate_route_overlap, decode_polyline
)
from app.services.maps_service import find_public_meeting_points

logger = logging.getLogger(__name__)

async def find_companion_matches(
    db: Session,
    journey: Journey,
    max_time_diff_minutes: int = 45,
    max_destination_distance_meters: float = 2500.0,
    min_overlap_pct: float = 15.0
) -> List[Dict[str, Any]]:
    """
    Deterministic rule-based matching engine for finding verified women travelling along similar routes.
    Privacy rules enforced:
    - Excludes journeys of unverified users (only verified women eligible).
    - Excludes requesting user's own journeys.
    - Never returns raw exact starting or destination street addresses.
    - Masks exact GPS waypoints into approximate corridor bounds.
    """
    if not journey.route_data:
        return []

    try:
        my_route = json.loads(journey.route_data)
        my_pts = decode_polyline(my_route.get("polyline", ""))
    except Exception as e:
        logger.error(f"Failed to decode my journey polyline: {e}")
        return []

    if not my_pts:
        return []

    # Query candidate journeys:
    # 1. Status in (PLANNED, IN_PROGRESS)
    # 2. is_public_for_matching is True
    # 3. Not user's own journey
    # 4. User is VERIFIED
    now = datetime.now(timezone.utc)
    candidates_query = db.query(Journey).join(User, Journey.user_id == User.id).filter(
        Journey.id != journey.id,
        Journey.user_id != journey.user_id,
        Journey.status.in_([JourneyStatus.PLANNED, JourneyStatus.IN_PROGRESS]),
        Journey.is_public_for_matching == True,
        User.verification_status == VerificationStatus.VERIFIED
    ).all()

    matches = []

    my_dep = journey.departure_time
    if my_dep.tzinfo is None:
        my_dep = my_dep.replace(tzinfo=timezone.utc)

    for other in candidates_query:
        if not other.route_data:
            continue

        other_dep = other.departure_time
        if other_dep.tzinfo is None:
            other_dep = other_dep.replace(tzinfo=timezone.utc)

        # 1. Departure time difference
        time_diff_minutes = abs(int((my_dep - other_dep).total_seconds() / 60))
        if time_diff_minutes > max_time_diff_minutes:
            continue

        # 2. Destination proximity (are we going to roughly the same area?)
        dest_distance = haversine_distance(
            journey.destination_lat, journey.destination_lng,
            other.destination_lat, other.destination_lng
        )
        if dest_distance > max_destination_distance_meters:
            continue

        # 3. Decode candidate's route
        try:
            other_route = json.loads(other.route_data)
            other_pts = decode_polyline(other_route.get("polyline", ""))
        except Exception:
            continue

        if not other_pts:
            continue

        # 4. Route overlap percentage
        overlap_pct, shared_pts = calculate_route_overlap(my_pts, other_pts, corridor_threshold_meters=300.0)
        if overlap_pct < min_overlap_pct:
            continue

        # 5. Travel mode compatibility
        mode_compatible = (journey.travel_mode == other.travel_mode)
        mode_score = 100.0 if mode_compatible else 50.0

        # Calculate composite compatibility score (0 to 100%)
        # Weights: Overlap (40%), Time proximity (30%), Destination proximity (20%), Mode (10%)
        time_score = max(0.0, 100.0 - (time_diff_minutes * (100.0 / max_time_diff_minutes)))
        dest_score = max(0.0, 100.0 - (dest_distance / max_destination_distance_meters * 100.0))
        
        composite_score = round(
            (0.40 * overlap_pct) +
            (0.30 * time_score) +
            (0.20 * dest_score) +
            (0.10 * mode_score),
            1
        )

        # Suggest public meeting point along the beginning of the shared route
        mid_idx = min(len(shared_pts) - 1, max(0, int(len(shared_pts) * 0.2)))
        meet_lat, meet_lng = shared_pts[mid_idx] if shared_pts else (journey.origin_lat, journey.origin_lng)
        
        meeting_points = await find_public_meeting_points(meet_lat, meet_lng, radius=1000)
        chosen_meeting = meeting_points[0] if meeting_points else {
            "name": "Well-Lit Public Transit Hub",
            "lat": meet_lat,
            "lng": meet_lng,
            "place_type": "transit_station"
        }

        # Privacy-safe coarse shared corridor (sample at coarse intervals, round to 3 decimals ~ 110m precision)
        approx_shared = [
            {"lat": round(p[0], 3), "lng": round(p[1], 3)}
            for i, p in enumerate(shared_pts) if i % 2 == 0
        ]

        # Privacy: Mask user's full name to Initial (e.g. "Maya K. (Verified)")
        name_parts = other.user.name.split()
        masked_name = f"{name_parts[0]} {name_parts[1][0]}." if len(name_parts) > 1 else f"{name_parts[0]}."

        matches.append({
            "journey_id": other.id,
            "user_id": other.user_id,
            "user_display_name": masked_name,
            "is_verified": other.user.verification_status == VerificationStatus.VERIFIED,
            "travel_mode": other.travel_mode,
            "departure_time": other.departure_time,
            "departure_time_diff_minutes": time_diff_minutes,
            "compatibility_score": composite_score,
            "route_overlap_percentage": overlap_pct,
            "approx_shared_route": approx_shared,
            "suggested_meeting_point": chosen_meeting,
            "destination_proximity_meters": round(dest_distance, 1)
        })

    # Sort descending by compatibility score
    matches.sort(key=lambda m: m["compatibility_score"], reverse=True)
    return matches

def create_companion_request(
    db: Session,
    sender: User,
    receiver_journey_id: int,
    initial_message: Optional[str] = None
) -> CompanionRequest:
    """Creates a mutual request from sender's active/planned journey to receiver's journey."""
    receiver_journey = db.query(Journey).filter(Journey.id == receiver_journey_id).first()
    if not receiver_journey:
        raise ValueError("Target journey not found.")

    if receiver_journey.user_id == sender.id:
        raise ValueError("Cannot match with your own journey.")

    # Find sender's active or planned journey
    sender_journey = db.query(Journey).filter(
        Journey.user_id == sender.id,
        Journey.status.in_([JourneyStatus.PLANNED, JourneyStatus.IN_PROGRESS])
    ).order_by(Journey.created_at.desc()).first()

    if not sender_journey:
        raise ValueError("You must have an active or planned journey to send a companion request.")

    # Check for existing request
    existing = db.query(CompanionRequest).filter(
        CompanionRequest.sender_id == sender.id,
        CompanionRequest.receiver_id == receiver_journey.user_id,
        CompanionRequest.status.in_([RequestStatus.PENDING, RequestStatus.ACCEPTED])
    ).first()

    if existing:
        return existing

    request = CompanionRequest(
        sender_id=sender.id,
        receiver_id=receiver_journey.user_id,
        sender_journey_id=sender_journey.id,
        receiver_journey_id=receiver_journey.id,
        status=RequestStatus.PENDING,
        initial_message=initial_message,
        meeting_suggestion="Central Metro Station Concourse"
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

def update_request_status(
    db: Session,
    request_id: int,
    user: User,
    new_status: RequestStatus
) -> CompanionRequest:
    """Updates companion request status. Creates CompanionGroup upon mutual ACCEPTED."""
    req = db.query(CompanionRequest).filter(CompanionRequest.id == request_id).first()
    if not req:
        raise ValueError("Companion request not found.")

    # Authorization check
    if new_status in [RequestStatus.ACCEPTED, RequestStatus.REJECTED]:
        if req.receiver_id != user.id:
            raise ValueError("Only the recipient can accept or reject this request.")
    elif new_status == RequestStatus.CANCELLED:
        if req.sender_id != user.id and req.receiver_id != user.id:
            raise ValueError("Not authorized to cancel this connection.")

    req.status = new_status
    
    # If accepted, initialize the CompanionGroup
    if new_status == RequestStatus.ACCEPTED:
        existing_group = db.query(CompanionGroup).filter(CompanionGroup.request_id == req.id).first()
        if not existing_group:
            group = CompanionGroup(
                request_id=req.id,
                user_ids_json=json.dumps([req.sender_id, req.receiver_id]),
                journey_ids_json=json.dumps([req.sender_journey_id, req.receiver_journey_id]),
                meeting_point_name="Central Safe Meeting Station",
                meeting_point_lat=req.sender_journey.origin_lat,
                meeting_point_lng=req.sender_journey.origin_lng,
                status=GroupStatus.ACTIVE
            )
            db.add(group)
    elif new_status in [RequestStatus.CANCELLED, RequestStatus.REJECTED]:
        # Disband group if existed
        group = db.query(CompanionGroup).filter(CompanionGroup.request_id == req.id).first()
        if group:
            group.status = GroupStatus.DISBANDED

    db.commit()
    db.refresh(req)
    return req

