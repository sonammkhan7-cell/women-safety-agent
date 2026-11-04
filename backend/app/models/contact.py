from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship as orm_relationship
from app.database import Base

class TrustedContact(Base):
    __tablename__ = "trusted_contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_name = Column(String(100), nullable=False)
    contact_phone = Column(String(30), nullable=False)
    contact_email = Column(String(255), nullable=True)
    relationship = Column(String(50), default="Friend", nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = orm_relationship("User", back_populates="trusted_contacts")
