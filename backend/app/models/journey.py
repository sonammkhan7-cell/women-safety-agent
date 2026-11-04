import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base

class JourneyStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DEVIATED = "deviated"
    ATTENTION_REQUIRED = "attention_required"
    CANCELLED = "cancelled"

class TravelMode(str, enum.Enum):
    WALKING = "walking"
    TRANSIT = "transit"
    DRIVING = "driving"
    BICYCLING = "bicycling"

class Journey(Base):
    __tablename__ = "journeys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Origin & Destination
    origin_name = Column(String(255), nullable=False)
    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)
    
    destination_name = Column(String(255), nullable=False)
    destination_lat = Column(Float, nullable=False)
    destination_lng = Column(Float, nullable=False)
    
    travel_mode = Column(Enum(TravelMode), default=TravelMode.WALKING, nullable=False)
    
    # Route Data stored as JSON (polyline, waypoints, distance, duration)
    route_data = Column(Text, nullable=True)
    
    departure_time = Column(DateTime, nullable=False)
    expected_arrival = Column(DateTime, nullable=True)
    
    status = Column(Enum(JourneyStatus), default=JourneyStatus.PLANNED, nullable=False)
    is_public_for_matching = Column(Boolean, default=True, nullable=False)
    
    # Monitoring state
    consecutive_deviations = Column(Integer, default=0, nullable=False)
    last_deviation_prompt_at = Column(DateTime, nullable=True)
    is_sos_active = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="journeys")
    locations = relationship("LocationUpdate", back_populates="journey", cascade="all, delete-orphan", order_by="LocationUpdate.recorded_at.desc()")
    alerts = relationship("EmergencyAlert", back_populates="journey", cascade="all, delete-orphan")

