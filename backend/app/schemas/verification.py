from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.user import VerificationStatus
from app.models.verification import DocumentType

class VerificationSubmit(BaseModel):
    document_type: DocumentType = DocumentType.STUDENT_ID
    # For privacy, only submit masked identifier or reference token (e.g., student ID hash or last 4 digits)
    masked_identifier: str = Field(..., min_length=3, max_length=100)
    submission_notes: Optional[str] = Field(None, max_length=500)

class VerificationReview(BaseModel):
    status: VerificationStatus
    reviewer_notes: Optional[str] = Field(None, max_length=500)

class VerificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: VerificationStatus
    document_type: DocumentType
    verification_reference: Optional[str] = None
    masked_identifier: Optional[str] = None
    submission_notes: Optional[str] = None
    reviewer_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

class AdminVerificationResponse(VerificationResponse):
    user_name: str
    user_email: str
