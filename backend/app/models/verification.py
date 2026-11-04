import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.user import VerificationStatus

class DocumentType(str, enum.Enum):
    STUDENT_ID = "student_id"
    GOVERNMENT_ID = "government_id"
    COMMUNITY_REFERRAL = "community_referral"
    INSTITUTIONAL_EMAIL = "institutional_email"

class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    document_type = Column(Enum(DocumentType), default=DocumentType.STUDENT_ID, nullable=False)
    # Store only masked reference or proof token, never full raw document files
    verification_reference = Column(String(255), nullable=True)
    masked_identifier = Column(String(100), nullable=True) # e.g. "STU-***-4821"
    submission_notes = Column(Text, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", foreign_keys=[user_id], back_populates="verifications")
    reviewer = relationship("User", foreign_keys=[reviewer_id])

