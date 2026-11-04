from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.journey import Journey, JourneyStatus
from app.models.location import LocationUpdate
from app.schemas.location import (
    LocationUpdateCreate, LocationUpdateResponse, DeviationResolution
)
from app.services.auth_service import get_current_user
from app.services.deviation_service import (
    check_gps_deviation, check_deviation_timeout, resolve_deviation
)

router = APIRouter(prefix="/tracking", tags=["Location Tracking & Route Monitoring"])

@router.post("/{journey_id}/location")
def record_location_update(
    journey_id: int,
    loc_in: LocationUpdateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    journey = db.query(Journey).filter(Journey.id == journey_id, Journey.user_id == current_user.id).first()
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found.")

    if journey.status in [JourneyStatus.COMPLETED, JourneyStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Cannot record location for completed or cancelled journey.")

    # Check if existing deviation prompt timed out
    check_deviation_timeout(db, journey)

    # Evaluate deviation against planned route considering GPS accuracy
    is_dev, dev_dist, prompt_user = check_gps_deviation(
        db=db,
        journey=journey,
        latitude=loc_in.latitude,
        longitude=loc_in.longitude,
        accuracy=loc_in.accuracy
    )

    # Store location update
    loc_record = LocationUpdate(
        journey_id=journey.id,
        latitude=loc_in.latitude,
        longitude=loc_in.longitude,
        accuracy=loc_in.accuracy,
        speed=loc_in.speed,
        heading=loc_in.heading,
        is_deviation=is_dev,
        deviation_distance=dev_dist
    )
    db.add(loc_record)
    db.commit()
    db.refresh(loc_record)

    return {
        "id": loc_record.id,
        "journey_id": journey.id,
        "is_deviation": is_dev,
        "deviation_distance": dev_dist,
        "consecutive_deviations": journey.consecutive_deviations,
        "prompt_user": prompt_user,
        "journey_status": journey.status,
        "is_sos_active": journey.is_sos_active,
        "last_deviation_prompt_at": journey.last_deviation_prompt_at,
        "recorded_at": loc_record.recorded_at
    }

@router.post("/{journey_id}/resolve-deviation")
def resolve_prompt(
    journey_id: int,
    resolution: DeviationResolution,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    journey = db.query(Journey).filter(Journey.id == journey_id, Journey.user_id == current_user.id).first()
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found.")

    result = resolve_deviation(db, journey, resolution.action, resolution.note)
    return result

@router.get("/{journey_id}/history", response_model=List[LocationUpdateResponse])
def get_location_history(
    journey_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    journey = db.query(Journey).filter(Journey.id == journey_id).first()
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found.")
    
    # Check permissions
    if journey.user_id != current_user.id:
        pass

    updates = db.query(LocationUpdate).filter(
        LocationUpdate.journey_id == journey_id
    ).order_by(LocationUpdate.recorded_at.desc()).limit(limit).all()

    return updates

