from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class LocationUpdate(Base):
    __tablename__ = "location_updates"

    id = Column(Integer, primary_key=True, index=True)
    journey_id = Column(Integer, ForeignKey("journeys.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)  # in meters
    speed = Column(Float, nullable=True)     # m/s
    heading = Column(Float, nullable=True)   # degrees
    is_deviation = Column(Boolean, default=False, nullable=False)
    deviation_distance = Column(Float, default=0.0, nullable=False)  # distance from route in meters
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    journey = relationship("Journey", back_populates="locations")

