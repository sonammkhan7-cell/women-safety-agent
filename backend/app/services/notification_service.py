import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.journey import Journey, JourneyStatus
from app.models.contact import TrustedContact
from app.models.alert import EmergencyAlert, AlertType, AlertStatus

logger = logging.getLogger(__name__)

def trigger_emergency_alert(
    db: Session,
    journey: Journey,
    alert_type: AlertType,
    lat: float,
    lng: float,
    address_text: Optional[str] = None
) -> EmergencyAlert:
    """
    Creates an emergency alert, marks journey as ATTENTION_REQUIRED and SOS active,
    and dispatches simulated notifications to all configured trusted contacts.
    """
    journey.status = JourneyStatus.ATTENTION_REQUIRED
    journey.is_sos_active = True

    # Retrieve all trusted contacts for this user
    contacts = db.query(TrustedContact).filter(TrustedContact.user_id == journey.user_id).all()
    
    notifications = []
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    for c in contacts:
        msg = (
            f"EMERGENCY ALERT: {journey.user.name} may need urgent assistance! "
            f"Alert Type: {alert_type.value.upper()}. "
            f"Last known location: https://maps.google.com/?q={lat:.5f},{lng:.5f} at {timestamp_str}."
        )
        notifications.append({
            "contact_id": c.id,
            "contact_name": c.contact_name,
            "contact_phone": c.contact_phone,
            "contact_email": c.contact_email,
            "message": msg,
            "status": "DISPATCHED_SIMULATED",
            "dispatched_at": timestamp_str
        })
        logger.warning(f"[EMERGENCY DISPATCH] Sent to {c.contact_name} ({c.contact_phone}): {msg}")

    alert = EmergencyAlert(
        journey_id=journey.id,
        user_id=journey.user_id,
        alert_type=alert_type,
        last_known_lat=lat,
        last_known_lng=lng,
        address_text=address_text or f"GPS Coordinates: ({lat:.5f}, {lng:.5f})",
        status=AlertStatus.ACTIVE,
        notifications_sent_json=json.dumps(notifications)
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

def resolve_emergency_alert(
    db: Session,
    alert_id: int,
    user_id: int,
    resolution_notes: str
) -> EmergencyAlert:
    """Resolves an emergency alert and restores journey status if appropriate."""
    alert = db.query(EmergencyAlert).filter(
        EmergencyAlert.id == alert_id,
        EmergencyAlert.user_id == user_id
    ).first()

    if not alert:
        raise ValueError("Emergency alert not found or access unauthorized.")

    alert.status = AlertStatus.RESOLVED
    alert.resolution_notes = resolution_notes
    alert.resolved_at = datetime.now(timezone.utc)

    # Check if there are other active alerts for this journey
    active_count = db.query(EmergencyAlert).filter(
        EmergencyAlert.journey_id == alert.journey_id,
        EmergencyAlert.status == AlertStatus.ACTIVE,
        EmergencyAlert.id != alert.id
    ).count()

    if active_count == 0 and alert.journey:
        alert.journey.is_sos_active = False
        if alert.journey.status == JourneyStatus.ATTENTION_REQUIRED:
            alert.journey.status = JourneyStatus.IN_PROGRESS

    db.commit()
    db.refresh(alert)
    return alert

