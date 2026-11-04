import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base

class AlertType(str, enum.Enum):
    SOS = "sos"
    ROUTE_DEVIATION_TIMEOUT = "route_deviation_timeout"
    MANUAL = "manual"

class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"

class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"

    id = Column(Integer, primary_key=True, index=True)
    journey_id = Column(Integer, ForeignKey("journeys.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_type = Column(Enum(AlertType), default=AlertType.SOS, nullable=False)
    last_known_lat = Column(Float, nullable=False)
    last_known_lng = Column(Float, nullable=False)
    address_text = Column(String(255), nullable=True)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE, nullable=False)
    notifications_sent_json = Column(Text, nullable=True)  # logs of contacts notified
    resolution_notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    journey = relationship("Journey", foreign_keys=[journey_id], back_populates="alerts")
    user = relationship("User", foreign_keys=[user_id])
