from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.user import VerificationStatus, UserRole

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = None
    emergency_note: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    is_email_verified: bool
    verification_status: VerificationStatus
    role: UserRole
    phone_number: Optional[str] = None
    emergency_note: Optional[str] = None
    created_at: datetime

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    emergency_note: Optional[str] = None
