import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User, VerificationStatus, UserRole
from app.models.journey import Journey, JourneyStatus, TravelMode
from app.models.contact import TrustedContact
from app.models.alert import EmergencyAlert, AlertType, AlertStatus
from app.services.notification_service import trigger_emergency_alert, resolve_emergency_alert
from datetime import datetime, timezone

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_sos_and_trusted_contact_notifications():
    db = Session()
    user = User(
        name="Elena Rostova", email="elena@test.com", password_hash="hash",
        verification_status=VerificationStatus.VERIFIED, role=UserRole.USER
    )
    db.add(user)
    db.commit()

    # Add 2 trusted contacts
    c1 = TrustedContact(user_id=user.id, contact_name="Mom", contact_phone="+1112223333", is_primary=True)
    c2 = TrustedContact(user_id=user.id, contact_name="Sister", contact_phone="+1112224444", is_primary=False)
    db.add_all([c1, c2])

    journey = Journey(
        user_id=user.id,
        origin_name="Work", origin_lat=40.7500, origin_lng=-73.9800,
        destination_name="Home", destination_lat=40.7600, destination_lng=-73.9800,
        travel_mode=TravelMode.WALKING,
        departure_time=datetime.now(timezone.utc),
        status=JourneyStatus.IN_PROGRESS
    )
    db.add(journey)
    db.commit()

    # Trigger immediate SOS alert
    alert = trigger_emergency_alert(
        db=db,
        journey=journey,
        alert_type=AlertType.SOS,
        lat=40.7540,
        lng=-73.9810,
        address_text="Immediate SOS on 5th Ave"
    )

    assert alert.id is not None
    assert alert.status == AlertStatus.ACTIVE
    assert journey.status == JourneyStatus.ATTENTION_REQUIRED
    assert journey.is_sos_active is True
    assert "EMERGENCY ALERT: Elena Rostova" in alert.notifications_sent_json
    assert "+1112223333" in alert.notifications_sent_json
    assert "+1112224444" in alert.notifications_sent_json

    # Resolve alert
    resolved = resolve_emergency_alert(
        db=db,
        alert_id=alert.id,
        user_id=user.id,
        resolution_notes="Safe with police officer, false alarm."
    )
    assert resolved.status == AlertStatus.RESOLVED
    assert journey.is_sos_active is False
    assert journey.status == JourneyStatus.IN_PROGRESS

