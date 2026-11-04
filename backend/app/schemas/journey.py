from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.journey import JourneyStatus, TravelMode

class Waypoint(BaseModel):
    lat: float
    lng: float

class JourneyCreate(BaseModel):
    origin_name: str = Field(..., min_length=2, max_length=255)
    origin_lat: float
    origin_lng: float
    destination_name: str = Field(..., min_length=2, max_length=255)
    destination_lat: float
    destination_lng: float
    travel_mode: TravelMode = TravelMode.WALKING
    departure_time: datetime
    is_public_for_matching: bool = True

class JourneyStatusUpdate(BaseModel):
    status: JourneyStatus

class JourneyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    origin_name: str
    origin_lat: float
    origin_lng: float
    destination_name: str
    destination_lat: float
    destination_lng: float
    travel_mode: TravelMode
    route_data: Optional[str] = None
    departure_time: datetime
    expected_arrival: Optional[datetime] = None
    status: JourneyStatus
    is_public_for_matching: bool
    consecutive_deviations: int
    last_deviation_prompt_at: Optional[datetime] = None
    is_sos_active: bool
    created_at: datetime
    updated_at: datetime

class RoutePreviewRequest(BaseModel):
    origin_lat: float
    origin_lng: float
    destination_lat: float
    destination_lng: float
    travel_mode: TravelMode = TravelMode.WALKING

class RoutePreviewResponse(BaseModel):
    distance_meters: float
    duration_seconds: int
    polyline: str
    waypoints: List[Waypoint]
    bounds: Dict[str, float]
