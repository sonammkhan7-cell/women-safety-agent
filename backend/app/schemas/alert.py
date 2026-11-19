from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.alert import AlertType, AlertStatus

class EmergencyAlertCreate(BaseModel):
    journey_id: Optional[int] = None
    alert_type: AlertType = AlertType.SOS
    latitude: float
    longitude: float
    address_text: Optional[str] = None
    note: Optional[str] = None

class EmergencyAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    journey_id: int
    user_id: int
    alert_type: AlertType
    last_known_lat: float
    last_known_lng: float
    address_text: Optional[str] = None
    status: AlertStatus
    notifications_sent_json: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

class AlertResolveRequest(BaseModel):
    resolution_notes: str = Field(..., min_length=2, max_length=500)
