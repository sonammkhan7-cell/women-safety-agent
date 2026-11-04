import json
from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.journey import Journey, JourneyStatus
from app.schemas.journey import (
    JourneyCreate, JourneyResponse, JourneyStatusUpdate, RoutePreviewRequest, RoutePreviewResponse
)
from app.services.auth_service import get_current_user
from app.services.maps_service import calculate_route

router = APIRouter(prefix="/journeys", tags=["Journeys"])

@router.post("/preview-route", response_model=RoutePreviewResponse)
async def preview_route(
    req: RoutePreviewRequest,
    current_user: User = Depends(get_current_user)
):
    route = await calculate_route(
        req.origin_lat, req.origin_lng,
        req.destination_lat, req.destination_lng,
        req.travel_mode.value
    )
    return route

@router.post("/", response_model=JourneyResponse, status_code=status.HTTP_201_CREATED)
async def create_journey(
    data: JourneyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Calculate route geometry
    route_calc = await calculate_route(
        data.origin_lat, data.origin_lng,
        data.destination_lat, data.destination_lng,
        data.travel_mode.value
    )
    
    dep_time = data.departure_time
    if dep_time.tzinfo is None:
        dep_time = dep_time.replace(tzinfo=timezone.utc)
    
    duration = route_calc.get("duration_seconds", 1800)
    expected_arr = dep_time + timedelta(seconds=duration)

    journey = Journey(
        user_id=current_user.id,
        origin_name=data.origin_name,
        origin_lat=data.origin_lat,
        origin_lng=data.origin_lng,
        destination_name=data.destination_name,
        destination_lat=data.destination_lat,
        destination_lng=data.destination_lng,
        travel_mode=data.travel_mode,
        route_data=json.dumps(route_calc),
        departure_time=dep_time,
        expected_arrival=expected_arr,
        status=JourneyStatus.PLANNED,
        is_public_for_matching=data.is_public_for_matching
    )
    db.add(journey)
    db.commit()
    db.refresh(journey)
    return journey

@router.get("/", response_model=List[JourneyResponse])
def list_my_journeys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Journey).filter(Journey.user_id == current_user.id).order_by(Journey.created_at.desc()).all()

@router.get("/{journey_id}", response_model=JourneyResponse)
def get_journey_by_id(
    journey_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    journey = db.query(Journey).filter(Journey.id == journey_id).first()
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found.")
    
    # User can view if they own it or are part of mutual companion group
    if journey.user_id != current_user.id:
        # Check mutual companion group
        pass
    return journey

@router.patch("/{journey_id}/status", response_model=JourneyResponse)
def update_status(
    journey_id: int,
    status_update: JourneyStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    journey = db.query(Journey).filter(Journey.id == journey_id, Journey.user_id == current_user.id).first()
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found.")

    journey.status = status_update.status
    if status_update.status == JourneyStatus.COMPLETED or status_update.status == JourneyStatus.CANCELLED:
        journey.is_sos_active = False
        journey.consecutive_deviations = 0

    db.commit()
    db.refresh(journey)
    return journey

