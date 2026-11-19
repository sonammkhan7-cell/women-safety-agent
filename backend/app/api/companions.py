import json
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, VerificationStatus
from app.models.journey import Journey, JourneyStatus, TravelMode
from app.models.companion import CompanionRequest, CompanionGroup, CompanionMessage, RequestStatus, GroupStatus
from app.schemas.companion import (
    CompanionCandidate, CompanionRequestCreate, CompanionRequestUpdate, CompanionRequestResponse,
    CompanionGroupResponse, CompanionMessageCreate, CompanionMessageResponse, JourneyScheduleBrowseItem
)
from app.services.auth_service import get_current_user, get_current_verified_user
from app.services.matching_service import (
    find_companion_matches, create_companion_request, update_request_status
)

router = APIRouter(prefix="/companions", tags=["Companion Matching"])

@router.get("/browse", response_model=List[JourneyScheduleBrowseItem])
def browse_scheduled_journeys(
    travel_mode: Optional[TravelMode] = None,
    destination: Optional[str] = None,
    journey_date: Optional[str] = None,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Browse upcoming scheduled journeys created by other verified women.
    Excludes the user's own journeys and applies optional filters.
    """
    query = db.query(Journey).join(User, Journey.user_id == User.id).filter(
        Journey.user_id != current_user.id,
        Journey.status.in_([JourneyStatus.PLANNED, JourneyStatus.IN_PROGRESS]),
        Journey.is_public_for_matching == True,
        User.verification_status == VerificationStatus.VERIFIED
    )

    if travel_mode:
        query = query.filter(Journey.travel_mode == travel_mode)
    if destination:
        query = query.filter(Journey.destination_name.ilike(f"%{destination.strip()}%"))

    journeys = query.order_by(Journey.departure_time.asc()).limit(30).all()

    results = []
    for j in journeys:
        # Date filter in python if requested
        if journey_date:
            try:
                target_d = datetime.strptime(journey_date, "%Y-%m-%d").date()
                if j.departure_time.date() != target_d:
                    continue
            except ValueError:
                pass

        name_parts = j.user.name.split()
        masked_name = f"{name_parts[0]} {name_parts[1][0]}." if len(name_parts) > 1 else f"{name_parts[0]}."

        results.append(JourneyScheduleBrowseItem(
            journey_id=j.id,
            user_id=j.user_id,
            user_display_name=masked_name,
            is_verified=True,
            origin_name=j.origin_name,
            destination_name=j.destination_name,
            travel_mode=j.travel_mode,
            departure_time=j.departure_time,
            status=j.status.value,
            origin_lat=j.origin_lat,
            origin_lng=j.origin_lng,
            destination_lat=j.destination_lat,
            destination_lng=j.destination_lng
        ))
    return results

@router.get("/matches/{journey_id}", response_model=List[CompanionCandidate])
async def get_matches(
    journey_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    journey = db.query(Journey).filter(Journey.id == journey_id, Journey.user_id == current_user.id).first()
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found.")

    matches = await find_companion_matches(db, journey)
    return matches

@router.post("/requests", response_model=CompanionRequestResponse, status_code=status.HTTP_201_CREATED)
def send_request(
    req_in: CompanionRequestCreate,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    try:
        req = create_companion_request(
            db=db,
            sender=current_user,
            receiver_journey_id=req_in.receiver_journey_id,
            initial_message=req_in.initial_message
        )
        return req
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/requests", response_model=List[CompanionRequestResponse])
def get_my_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    requests = db.query(CompanionRequest).filter(
        (CompanionRequest.sender_id == current_user.id) | (CompanionRequest.receiver_id == current_user.id)
    ).order_by(CompanionRequest.created_at.desc()).all()

    # Hydrate names
    res = []
    for r in requests:
        item = CompanionRequestResponse.model_validate(r)
        item.sender_name = r.sender.name if r.sender else "User"
        item.receiver_name = r.receiver.name if r.receiver else "User"
        res.append(item)
    return res

@router.patch("/requests/{request_id}", response_model=CompanionRequestResponse)
def update_status_endpoint(
    request_id: int,
    body: CompanionRequestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        req = update_request_status(db, request_id, current_user, body.status)
        item = CompanionRequestResponse.model_validate(req)
        item.sender_name = req.sender.name
        item.receiver_name = req.receiver.name
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/groups/{group_id}", response_model=CompanionGroupResponse)
def get_group_details(
    group_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    group = db.query(CompanionGroup).filter(CompanionGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Companion group not found.")

    user_ids = json.loads(group.user_ids_json)
    if current_user.id not in user_ids:
        raise HTTPException(status_code=403, detail="Unauthorized to view this companion group.")

    journey_ids = json.loads(group.journey_ids_json)

    return CompanionGroupResponse(
        id=group.id,
        request_id=group.request_id,
        user_ids=user_ids,
        journey_ids=journey_ids,
        meeting_point_name=group.meeting_point_name,
        meeting_point_lat=group.meeting_point_lat,
        meeting_point_lng=group.meeting_point_lng,
        meeting_time=group.meeting_time,
        status=group.status,
        created_at=group.created_at,
        updated_at=group.updated_at
    )

@router.get("/groups", response_model=List[CompanionGroupResponse])
def get_my_companion_groups(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    groups = db.query(CompanionGroup).filter(CompanionGroup.status == GroupStatus.ACTIVE).all()
    my_groups = []
    for g in groups:
        try:
            u_ids = json.loads(g.user_ids_json)
            if current_user.id in u_ids:
                j_ids = json.loads(g.journey_ids_json)
                my_groups.append(CompanionGroupResponse(
                    id=g.id,
                    request_id=g.request_id,
                    user_ids=u_ids,
                    journey_ids=j_ids,
                    meeting_point_name=g.meeting_point_name,
                    meeting_point_lat=g.meeting_point_lat,
                    meeting_point_lng=g.meeting_point_lng,
                    meeting_time=g.meeting_time,
                    status=g.status,
                    created_at=g.created_at,
                    updated_at=g.updated_at
                ))
        except Exception:
            continue
    return my_groups

@router.get("/groups/{group_id}/messages", response_model=List[CompanionMessageResponse])
def get_group_messages(
    group_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    group = db.query(CompanionGroup).filter(CompanionGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Companion group not found.")

    user_ids = json.loads(group.user_ids_json)
    if current_user.id not in user_ids:
        raise HTTPException(status_code=403, detail="Unauthorized to view messages for this group.")

    messages = db.query(CompanionMessage).filter(
        CompanionMessage.group_id == group_id
    ).order_by(CompanionMessage.created_at.asc()).all()

    res = []
    for m in messages:
        res.append(CompanionMessageResponse(
            id=m.id,
            group_id=m.group_id,
            sender_id=m.sender_id,
            sender_name=m.sender.name if m.sender else "Companion",
            message=m.message,
            created_at=m.created_at
        ))
    return res

@router.post("/groups/{group_id}/messages", response_model=CompanionMessageResponse, status_code=status.HTTP_201_CREATED)
def post_group_message(
    group_id: int,
    body: CompanionMessageCreate,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    group = db.query(CompanionGroup).filter(CompanionGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Companion group not found.")

    user_ids = json.loads(group.user_ids_json)
    if current_user.id not in user_ids:
        raise HTTPException(status_code=403, detail="Unauthorized to send messages in this group.")

    new_msg = CompanionMessage(
        group_id=group_id,
        sender_id=current_user.id,
        message=body.message.strip()
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)

    return CompanionMessageResponse(
        id=new_msg.id,
        group_id=new_msg.group_id,
        sender_id=new_msg.sender_id,
        sender_name=current_user.name,
        message=new_msg.message,
        created_at=new_msg.created_at
    )

