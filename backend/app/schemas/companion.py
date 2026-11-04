from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.companion import RequestStatus, GroupStatus
from app.models.journey import TravelMode

class MeetingPoint(BaseModel):
    name: str
    lat: float
    lng: float
    place_type: str = "transit_station"

class CompanionCandidate(BaseModel):
    journey_id: int
    user_id: int
    user_display_name: str # e.g. "Maya K. (Verified)"
    is_verified: bool
    travel_mode: TravelMode
    departure_time: datetime
    departure_time_diff_minutes: int
    compatibility_score: float # 0 to 100%
    route_overlap_percentage: float
    approx_shared_route: List[Dict[str, float]] # Coarse privacy-preserving waypoints
    suggested_meeting_point: MeetingPoint
    destination_proximity_meters: float

class CompanionRequestCreate(BaseModel):
    receiver_journey_id: int
    initial_message: Optional[str] = Field(None, max_length=500)

class CompanionRequestUpdate(BaseModel):
    status: RequestStatus # ACCEPTED or REJECTED or CANCELLED

class CompanionRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender_id: int
    receiver_id: int
    sender_journey_id: int
    receiver_journey_id: int
    status: RequestStatus
    initial_message: Optional[str] = None
    compatibility_score: Optional[float] = None
    meeting_suggestion: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    sender_name: Optional[str] = None
    receiver_name: Optional[str] = None

class CompanionGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    user_ids: List[int]
    journey_ids: List[int]
    meeting_point_name: Optional[str] = None
    meeting_point_lat: Optional[float] = None
    meeting_point_lng: Optional[float] = None
    meeting_time: Optional[datetime] = None
    status: GroupStatus
    created_at: datetime
    updated_at: datetime
