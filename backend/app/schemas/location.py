from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class LocationUpdateCreate(BaseModel):
    latitude: float
    longitude: float
    accuracy: float = Field(..., ge=0.0)  # in meters
    speed: Optional[float] = None
    heading: Optional[float] = None

class LocationUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    journey_id: int
    latitude: float
    longitude: float
    accuracy: float
    is_deviation: bool
    deviation_distance: float
    recorded_at: datetime

class DeviationResolution(BaseModel):
    action: str = Field(..., description="'safe_dismiss', 'update_route', or 'request_help'")
    note: Optional[str] = None
