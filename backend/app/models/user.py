import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base

class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    verification_status = Column(
        Enum(VerificationStatus), 
        default=VerificationStatus.PENDING, 
        nullable=False
    )
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    phone_number = Column(String(30), nullable=True)
    emergency_note = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    verifications = relationship(
        "Verification",
        foreign_keys="Verification.user_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    journeys = relationship("Journey", back_populates="user", cascade="all, delete-orphan")
    trusted_contacts = relationship("TrustedContact", back_populates="user", cascade="all, delete-orphan")
    sent_requests = relationship(
        "CompanionRequest", 
        foreign_keys="CompanionRequest.sender_id", 
        back_populates="sender",
        cascade="all, delete-orphan"
    )
    received_requests = relationship(
        "CompanionRequest", 
        foreign_keys="CompanionRequest.receiver_id", 
        back_populates="receiver",
        cascade="all, delete-orphan"
    )
