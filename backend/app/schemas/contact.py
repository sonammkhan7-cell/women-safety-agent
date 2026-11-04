from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class TrustedContactCreate(BaseModel):
    contact_name: str = Field(..., min_length=2, max_length=100)
    contact_phone: str = Field(..., min_length=5, max_length=30)
    contact_email: Optional[EmailStr] = None
    relationship: str = Field("Friend", max_length=50)
    is_primary: bool = False

class TrustedContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    contact_name: str
    contact_phone: str
    contact_email: Optional[str] = None
    relationship: str
    is_primary: bool
    created_at: datetime
