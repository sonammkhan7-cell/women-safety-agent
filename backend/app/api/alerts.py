from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.journey import Journey, JourneyStatus
from app.models.alert import EmergencyAlert, AlertType, AlertStatus
from app.schemas.alert import (
    EmergencyAlertCreate, EmergencyAlertResponse, AlertResolveRequest
)
from app.services.auth_service import get_current_user
from app.services.notification_service import (
    trigger_emergency_alert, resolve_emergency_alert
)

router = APIRouter(prefix="/alerts", tags=["Emergency Alerts & SOS"])

@router.post("/sos", response_model=EmergencyAlertResponse, status_code=status.HTTP_201_CREATED)
def trigger_sos(
    sos_data: EmergencyAlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Immediate SOS action that dispatches emergency alerts without waiting for route deviation timeout.
    """
    journey = None
    if sos_data.journey_id:
        journey = db.query(Journey).filter(
            Journey.id == sos_data.journey_id,
            Journey.user_id == current_user.id
        ).first()

    if not journey:
        # Find active or planned journey
        journey = db.query(Journey).filter(
            Journey.user_id == current_user.id,
            Journey.status.in_([JourneyStatus.IN_PROGRESS, JourneyStatus.PLANNED, JourneyStatus.DEVIATED])
        ).order_by(Journey.created_at.desc()).first()

    if not journey:
        # Create an ad-hoc emergency incident journey
        from datetime import datetime, timezone
        from app.models.journey import TravelMode
        now = datetime.now(timezone.utc)
        journey = Journey(
            user_id=current_user.id,
            origin_name=sos_data.address_text or "Emergency SOS Incident Location",
            origin_lat=sos_data.latitude,
            origin_lng=sos_data.longitude,
            destination_name="Emergency Support Dispatch",
            destination_lat=sos_data.latitude,
            destination_lng=sos_data.longitude,
            travel_mode=TravelMode.WALKING,
            departure_time=now,
            status=JourneyStatus.ATTENTION_REQUIRED,
            is_public_for_matching=False,
            is_sos_active=True
        )
        db.add(journey)
        db.commit()
        db.refresh(journey)

    alert = trigger_emergency_alert(
        db=db,
        journey=journey,
        alert_type=sos_data.alert_type,
        lat=sos_data.latitude,
        lng=sos_data.longitude,
        address_text=sos_data.address_text or sos_data.note or "Immediate User SOS Triggered"
    )
    return alert

@router.get("/active", response_model=List[EmergencyAlertResponse])
def get_active_emergency_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns any active emergency alerts for the user to display live guardian tracking."""
    return db.query(EmergencyAlert).filter(
        EmergencyAlert.user_id == current_user.id,
        EmergencyAlert.status == AlertStatus.ACTIVE
    ).order_by(EmergencyAlert.created_at.desc()).all()

@router.get("/", response_model=List[EmergencyAlertResponse])
def get_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(EmergencyAlert).filter(
        EmergencyAlert.user_id == current_user.id
    ).order_by(EmergencyAlert.created_at.desc()).all()

@router.post("/{alert_id}/resolve", response_model=EmergencyAlertResponse)
def resolve_alert(
    alert_id: int,
    body: AlertResolveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        alert = resolve_emergency_alert(
            db=db,
            alert_id=alert_id,
            user_id=current_user.id,
            resolution_notes=body.resolution_notes
        )
        return alert
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

