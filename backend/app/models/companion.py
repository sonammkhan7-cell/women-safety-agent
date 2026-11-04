import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base

class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class GroupStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DISBANDED = "disbanded"

class CompanionRequest(Base):
    __tablename__ = "companion_requests"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_journey_id = Column(Integer, ForeignKey("journeys.id", ondelete="CASCADE"), nullable=False)
    receiver_journey_id = Column(Integer, ForeignKey("journeys.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING, nullable=False)
    initial_message = Column(String(500), nullable=True)
    compatibility_score = Column(Float, nullable=True)
    meeting_suggestion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_requests")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_requests")
    sender_journey = relationship("Journey", foreign_keys=[sender_journey_id])
    receiver_journey = relationship("Journey", foreign_keys=[receiver_journey_id])
    group = relationship("CompanionGroup", back_populates="request", uselist=False)

class CompanionGroup(Base):
    __tablename__ = "companion_groups"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("companion_requests.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_ids_json = Column(Text, nullable=False) # e.g. "[1, 2]"
    journey_ids_json = Column(Text, nullable=False) # e.g. "[10, 15]"
    meeting_point_name = Column(String(255), nullable=True)
    meeting_point_lat = Column(Float, nullable=True)
    meeting_point_lng = Column(Float, nullable=True)
    meeting_time = Column(DateTime, nullable=True)
    status = Column(Enum(GroupStatus), default=GroupStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    request = relationship("CompanionRequest", back_populates="group")

