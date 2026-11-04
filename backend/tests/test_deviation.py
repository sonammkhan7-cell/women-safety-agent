import json
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User, VerificationStatus, UserRole
from app.models.journey import Journey, JourneyStatus, TravelMode
from app.models.location import LocationUpdate
from app.models.alert import EmergencyAlert, AlertType
from app.utils.geo import encode_polyline
from app.services.deviation_service import check_gps_deviation, check_deviation_timeout, resolve_deviation
from app.config import settings

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_deviation_detection_with_gps_accuracy():
    db = Session()
    # Create test user
    user = User(
        name="Jane Doe", email="jane@test.com", password_hash="hash",
        verification_status=VerificationStatus.VERIFIED, role=UserRole.USER
    )
    db.add(user)
    db.commit()

    # Route: line along latitude 40.7500 from lng -73.9900 to -73.9800
    points = [(40.7500, -73.9900), (40.7500, -73.9850), (40.7500, -73.9800)]
    poly = encode_polyline(points)
    route_json = json.dumps({"polyline": poly, "distance_meters": 1000})

    journey = Journey(
        user_id=user.id,
        origin_name="Start", origin_lat=40.7500, origin_lng=-73.9900,
        destination_name="End", destination_lat=40.7500, destination_lng=-73.9800,
        travel_mode=TravelMode.WALKING,
        route_data=route_json,
        departure_time=datetime.now(timezone.utc),
        status=JourneyStatus.IN_PROGRESS
    )
    db.add(journey)
    db.commit()

    # 1. On route: point exactly on route -> no deviation
    is_dev, dist, prompt = check_gps_deviation(db, journey, 40.7500, -73.9850, accuracy=5.0)
    assert not is_dev
    assert dist < 10.0
    assert not prompt

    # 2. Large deviation distance (e.g. 350m off route) but GPS accuracy is bad (e.g. 400m)
    # Because accuracy is > 50m and dist <= accuracy, it should NOT trigger a false deviation alarm!
    is_dev_bad_gps, _, prompt_bad_gps = check_gps_deviation(db, journey, 40.7530, -73.9850, accuracy=400.0)
    assert not is_dev_bad_gps
    assert not prompt_bad_gps

    # 3. Persistent real deviations with high accuracy (10m accuracy, ~400m off-route)
    # Consecutive check 1
    is_dev1, dist1, prompt1 = check_gps_deviation(db, journey, 40.7535, -73.9850, accuracy=10.0)
    assert is_dev1
    assert journey.consecutive_deviations == 1
    assert not prompt1  # Needs DEVIATION_PERSISTENCE_COUNT (3) before prompting

    # Consecutive check 2
    is_dev2, dist2, prompt2 = check_gps_deviation(db, journey, 40.7535, -73.9850, accuracy=10.0)
    assert is_dev2
    assert journey.consecutive_deviations == 2
    assert not prompt2

    # Consecutive check 3 -> triggers persistent deviation alert prompt!
    is_dev3, dist3, prompt3 = check_gps_deviation(db, journey, 40.7535, -73.9850, accuracy=10.0)
    assert is_dev3
    assert journey.consecutive_deviations >= 3
    assert prompt3
    assert journey.status == JourneyStatus.DEVIATED
    assert journey.last_deviation_prompt_at is not None

def test_deviation_timeout_escalation():
    db = Session()
    user = User(
        name="Clara Oswald", email="clara@test.com", password_hash="hash",
        verification_status=VerificationStatus.VERIFIED, role=UserRole.USER
    )
    db.add(user)
    db.commit()

    # Set up journey in DEVIATED state with prompt timestamp older than timeout
    old_time = datetime.now(timezone.utc) - timedelta(seconds=settings.DEVIATION_TIMEOUT_SECONDS + 10)
    journey = Journey(
        user_id=user.id,
        origin_name="Home", origin_lat=40.7500, origin_lng=-73.9900,
        destination_name="Office", destination_lat=40.7500, destination_lng=-73.9800,
        travel_mode=TravelMode.WALKING,
        departure_time=datetime.now(timezone.utc),
        status=JourneyStatus.DEVIATED,
        last_deviation_prompt_at=old_time
    )
    db.add(journey)
    db.commit()

    # Check timeout
    alert = check_deviation_timeout(db, journey)
    assert alert is not None
    assert alert.alert_type == AlertType.ROUTE_DEVIATION_TIMEOUT
    assert journey.status == JourneyStatus.ATTENTION_REQUIRED
    assert journey.is_sos_active is True

