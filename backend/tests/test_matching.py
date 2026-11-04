import json
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User, VerificationStatus, UserRole
from app.models.journey import Journey, JourneyStatus, TravelMode
from app.utils.geo import encode_polyline
from app.services.matching_service import find_companion_matches

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.mark.asyncio
async def test_companion_matching_rule_based():
    db = Session()
    now = datetime.now(timezone.utc)

    # 1. Requester: User A (Verified)
    user_a = User(
        name="Alice Walker", email="alice@test.com", password_hash="hash",
        verification_status=VerificationStatus.VERIFIED, role=UserRole.USER
    )
    # 2. Candidate: User B (Verified, similar route and time)
    user_b = User(
        name="Brianna Miller", email="brianna@test.com", password_hash="hash",
        verification_status=VerificationStatus.VERIFIED, role=UserRole.USER
    )
    # 3. Unverified Candidate: User C (Similar route, but NOT verified)
    user_c = User(
        name="Chloe Unverified", email="chloe@test.com", password_hash="hash",
        verification_status=VerificationStatus.PENDING, role=UserRole.USER
    )
    # 4. Far Candidate: User D (Verified, but different route and time)
    user_d = User(
        name="Diana Far", email="diana@test.com", password_hash="hash",
        verification_status=VerificationStatus.VERIFIED, role=UserRole.USER
    )

    db.add_all([user_a, user_b, user_c, user_d])
    db.commit()

    # Route 1: Northbound along 5th Ave
    pts1 = [(40.7500, -73.9800), (40.7550, -73.9800), (40.7600, -73.9800)]
    poly1 = encode_polyline(pts1)
    
    # Route 2: Parallel along Madison Ave (~100m away, highly overlapping corridor)
    pts2 = [(40.7510, -73.9790), (40.7555, -73.9790), (40.7605, -73.9790)]
    poly2 = encode_polyline(pts2)

    # Route Far: in another city
    pts_far = [(51.5000, -0.1200), (51.5100, -0.1200)]
    poly_far = encode_polyline(pts_far)

    # Journey A (Alice)
    j_a = Journey(
        user_id=user_a.id,
        origin_name="Grand Central", origin_lat=40.7500, origin_lng=-73.9800,
        destination_name="Central Park South", destination_lat=40.7600, destination_lng=-73.9800,
        travel_mode=TravelMode.WALKING,
        route_data=json.dumps({"polyline": poly1}),
        departure_time=now,
        status=JourneyStatus.PLANNED,
        is_public_for_matching=True
    )

    # Journey B (Brianna, 5 mins later, similar route)
    j_b = Journey(
        user_id=user_b.id,
        origin_name="Bryant Park", origin_lat=40.7510, origin_lng=-73.9790,
        destination_name="Plaza Hotel", destination_lat=40.7605, destination_lng=-73.9790,
        travel_mode=TravelMode.WALKING,
        route_data=json.dumps({"polyline": poly2}),
        departure_time=now + timedelta(minutes=5),
        status=JourneyStatus.PLANNED,
        is_public_for_matching=True
    )

    # Journey C (Chloe, unverified user)
    j_c = Journey(
        user_id=user_c.id,
        origin_name="Bryant Park", origin_lat=40.7510, origin_lng=-73.9790,
        destination_name="Plaza Hotel", destination_lat=40.7605, destination_lng=-73.9790,
        travel_mode=TravelMode.WALKING,
        route_data=json.dumps({"polyline": poly2}),
        departure_time=now + timedelta(minutes=5),
        status=JourneyStatus.PLANNED,
        is_public_for_matching=True
    )

    # Journey D (Diana, far away)
    j_d = Journey(
        user_id=user_d.id,
        origin_name="Far Origin", origin_lat=51.5000, origin_lng=-0.1200,
        destination_name="Far Dest", destination_lat=51.5100, destination_lng=-0.1200,
        travel_mode=TravelMode.WALKING,
        route_data=json.dumps({"polyline": poly_far}),
        departure_time=now + timedelta(hours=3),
        status=JourneyStatus.PLANNED,
        is_public_for_matching=True
    )

    db.add_all([j_a, j_b, j_c, j_d])
    db.commit()

    matches = await find_companion_matches(db, j_a)

    # Assertions:
    # 1. Unverified user C must NOT be included!
    candidate_ids = [m["user_id"] for m in matches]
    assert user_c.id not in candidate_ids

    # 2. Far user D must NOT be included!
    assert user_d.id not in candidate_ids

    # 3. Verified user B must be found as a high-compatibility match!
    assert user_b.id in candidate_ids
    match_b = next(m for m in matches if m["user_id"] == user_b.id)
    assert match_b["compatibility_score"] >= 75.0
    assert match_b["departure_time_diff_minutes"] == 5
    assert match_b["user_display_name"] == "Brianna M."
    assert "suggested_meeting_point" in match_b
    assert match_b["is_verified"] is True

