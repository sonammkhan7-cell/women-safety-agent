import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.orm import Session
from app.config import settings
from app.models.journey import Journey, JourneyStatus
from app.models.location import LocationUpdate
from app.models.alert import EmergencyAlert, AlertType, AlertStatus
from app.utils.geo import point_to_polyline_distance, decode_polyline
from app.services.notification_service import trigger_emergency_alert

logger = logging.getLogger(__name__)

def check_gps_deviation(
    db: Session,
    journey: Journey,
    latitude: float,
    longitude: float,
    accuracy: float
) -> Tuple[bool, float, bool]:
    """
    Evaluates GPS point against planned journey route.
    Returns:
      (is_deviation, deviation_distance, prompt_user)
    """
    if not journey.route_data:
        return False, 0.0, False

    try:
        route_dict = json.loads(journey.route_data)
        polyline = route_dict.get("polyline", "")
        pts = decode_polyline(polyline)
    except Exception as e:
        logger.error(f"Failed to decode route polyline for journey {journey.id}: {e}")
        return False, 0.0, False

    # Calculate shortest perpendicular distance to route
    raw_distance = point_to_polyline_distance(latitude, longitude, pts)

    # GPS accuracy check:
    # If the GPS reported accuracy radius is very wide (e.g. > 75m) and the distance
    # is within the accuracy radius, do NOT treat this as a confirmed deviation to avoid false alarms.
    if accuracy > settings.GPS_ACCURACY_THRESHOLD_METERS and raw_distance <= accuracy:
        effective_deviation = False
    else:
        effective_deviation = raw_distance > settings.DEVIATION_DISTANCE_THRESHOLD_METERS

    prompt_user = False

    if effective_deviation:
        journey.consecutive_deviations += 1
        # If deviations persist across consecutive readings
        if journey.consecutive_deviations >= settings.DEVIATION_PERSISTENCE_COUNT:
            if journey.status != JourneyStatus.DEVIATED and journey.status != JourneyStatus.ATTENTION_REQUIRED:
                journey.status = JourneyStatus.DEVIATED
                journey.last_deviation_prompt_at = datetime.now(timezone.utc)
                prompt_user = True
            elif journey.last_deviation_prompt_at is None:
                journey.last_deviation_prompt_at = datetime.now(timezone.utc)
                prompt_user = True
    else:
        # Reset consecutive deviations counter when user returns to route
        journey.consecutive_deviations = max(0, journey.consecutive_deviations - 1)
        if journey.status == JourneyStatus.DEVIATED and journey.consecutive_deviations == 0:
            journey.status = JourneyStatus.IN_PROGRESS
            journey.last_deviation_prompt_at = None

    db.commit()
    db.refresh(journey)

    return effective_deviation, round(raw_distance, 1), prompt_user

def check_deviation_timeout(db: Session, journey: Journey) -> Optional[EmergencyAlert]:
    """
    Checks if a prompted route deviation has exceeded the configurable response timeout.
    If timed out without user confirmation, marks journey as ATTENTION_REQUIRED and creates an alert.
    """
    if journey.status == JourneyStatus.DEVIATED and journey.last_deviation_prompt_at:
        now = datetime.now(timezone.utc)
        prompt_time = journey.last_deviation_prompt_at
        if prompt_time.tzinfo is None:
            prompt_time = prompt_time.replace(tzinfo=timezone.utc)
        
        elapsed = (now - prompt_time).total_seconds()
        if elapsed > settings.DEVIATION_TIMEOUT_SECONDS:
            # Mark attention required
            journey.status = JourneyStatus.ATTENTION_REQUIRED
            db.commit()
            db.refresh(journey)

            # Get latest location
            latest_loc = db.query(LocationUpdate).filter(
                LocationUpdate.journey_id == journey.id
            ).order_by(LocationUpdate.recorded_at.desc()).first()

            lat = latest_loc.latitude if latest_loc else journey.origin_lat
            lng = latest_loc.longitude if latest_loc else journey.origin_lng

            # Trigger automated emergency alert
            alert = trigger_emergency_alert(
                db=db,
                journey=journey,
                alert_type=AlertType.ROUTE_DEVIATION_TIMEOUT,
                lat=lat,
                lng=lng,
                address_text=f"Persistent route deviation near ({lat:.4f}, {lng:.4f}) with no user response within {settings.DEVIATION_TIMEOUT_SECONDS}s"
            )
            return alert
    return None

def resolve_deviation(
    db: Session,
    journey: Journey,
    action: str,
    note: Optional[str] = None
) -> Dict[str, Any]:
    """
    User resolves deviation prompt:
    - 'safe_dismiss': User confirms they are safe and took a minor detour intentionally.
    - 'update_route': User confirms new destination/route, resets deviation counter.
    - 'request_help': User immediately escalates to emergency SOS.
    """
    if action == "safe_dismiss":
        journey.status = JourneyStatus.IN_PROGRESS
        journey.consecutive_deviations = 0
        journey.last_deviation_prompt_at = None
        db.commit()
        return {"status": "ok", "message": "Detour dismissed. Route monitoring resumed."}

    elif action == "update_route":
        journey.status = JourneyStatus.IN_PROGRESS
        journey.consecutive_deviations = 0
        journey.last_deviation_prompt_at = None
        db.commit()
        return {"status": "ok", "message": "Route update confirmed."}

    elif action == "request_help":
        journey.status = JourneyStatus.ATTENTION_REQUIRED
        journey.is_sos_active = True
        db.commit()
        
        latest_loc = db.query(LocationUpdate).filter(
            LocationUpdate.journey_id == journey.id
        ).order_by(LocationUpdate.recorded_at.desc()).first()
        lat = latest_loc.latitude if latest_loc else journey.origin_lat
        lng = latest_loc.longitude if latest_loc else journey.origin_lng

        alert = trigger_emergency_alert(
            db=db,
            journey=journey,
            alert_type=AlertType.MANUAL,
            lat=lat,
            lng=lng,
            address_text=note or "User requested assistance via deviation alert modal"
        )
        return {"status": "alert_triggered", "alert_id": alert.id, "message": "Emergency alert triggered."}

    return {"status": "ignored"}

