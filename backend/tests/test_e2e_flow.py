import json
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
TestClient.__test__ = False
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Isolated In-Memory DB
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_full_journey_safety_and_companion_matching_lifecycle():
    # 1. Register Admin User
    admin_reg = client.post("/api/v1/auth/register", json={
        "name": "System Admin",
        "email": "admin@test.org",
        "password": "Password123!"
    })
    assert admin_reg.status_code == 201
    admin_token = client.post("/api/v1/auth/login", json={
        "email": "admin@test.org", "password": "Password123!"
    }).json()["access_token"]

    # 2. Register Woman User 1: Maya
    maya_reg = client.post("/api/v1/auth/register", json={
        "name": "Maya Kapoor",
        "email": "maya@university.edu",
        "password": "Password123!",
        "phone_number": "+1 555-0142"
    })
    assert maya_reg.status_code == 201
    maya_id = maya_reg.json()["id"]
    maya_token = client.post("/api/v1/auth/login", json={
        "email": "maya@university.edu", "password": "Password123!"
    }).json()["access_token"]
    maya_headers = {"Authorization": f"Bearer {maya_token}"}

    # 3. Add Trusted Contact for Maya
    contact_resp = client.post("/api/v1/contacts/", headers=maya_headers, json={
        "contact_name": "Aunt Anita",
        "contact_phone": "+1 555-0199",
        "relationship": "Family Guardian",
        "is_primary": True
    })
    assert contact_resp.status_code == 201

    # 4. Submit Verification for Maya
    verif_sub = client.post("/api/v1/verification/submit", headers=maya_headers, json={
        "document_type": "student_id",
        "masked_identifier": "STU-***-4821",
        "submission_notes": "Graduate engineering student"
    })
    assert verif_sub.status_code == 200
    verif_id = verif_sub.json()["id"]

    # 5. Admin Approves Maya's Verification
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    review_resp = client.post(f"/api/v1/verification/admin/review/{verif_id}", headers=admin_headers, json={
        "status": "verified",
        "reviewer_notes": "Identity confirmed via campus directory"
    })
    assert review_resp.status_code == 200
    assert review_resp.json()["status"] == "verified"

    # 6. Register Woman User 2: Priya (Verified)
    priya_reg = client.post("/api/v1/auth/register", json={
        "name": "Priya Sharma",
        "email": "priya@citytech.org",
        "password": "Password123!"
    })
    assert priya_reg.status_code == 201
    priya_token = client.post("/api/v1/auth/login", json={
        "email": "priya@citytech.org", "password": "Password123!"
    }).json()["access_token"]
    priya_headers = {"Authorization": f"Bearer {priya_token}"}

    # Priya gets verified by Admin
    p_verif = client.post("/api/v1/verification/submit", headers=priya_headers, json={
        "document_type": "institutional_email",
        "masked_identifier": "RES-***-9943"
    })
    client.post(f"/api/v1/verification/admin/review/{p_verif.json()['id']}", headers=admin_headers, json={
        "status": "verified"
    })

    # 7. Maya creates Journey 1 (Times Square to Columbus Circle)
    now = datetime.now(timezone.utc)
    j1_resp = client.post("/api/v1/journeys/", headers=maya_headers, json={
        "origin_name": "Times Square North Station",
        "origin_lat": 40.7580,
        "origin_lng": -73.9855,
        "destination_name": "Columbus Circle & 59th St",
        "destination_lat": 40.7681,
        "destination_lng": -73.9819,
        "travel_mode": "walking",
        "departure_time": (now + timedelta(minutes=10)).isoformat(),
        "is_public_for_matching": True
    })
    assert j1_resp.status_code == 201
    j1_id = j1_resp.json()["id"]

    # 8. Priya creates Journey 2 (Parallel corridor, departing 5 mins later)
    j2_resp = client.post("/api/v1/journeys/", headers=priya_headers, json={
        "origin_name": "Broadway & 44th St",
        "origin_lat": 40.7585,
        "origin_lng": -73.9850,
        "destination_name": "Central Park South & 7th Ave",
        "destination_lat": 40.7685,
        "destination_lng": -73.9815,
        "travel_mode": "walking",
        "departure_time": (now + timedelta(minutes=15)).isoformat(),
        "is_public_for_matching": True
    })
    assert j2_resp.status_code == 201
    j2_id = j2_resp.json()["id"]

    # 9. Start Maya's Journey (Tracking active)
    client.patch(f"/api/v1/journeys/{j1_id}/status", headers=maya_headers, json={"status": "in_progress"})

    # 10. Normal On-Route Location Update
    loc_norm = client.post(f"/api/v1/tracking/{j1_id}/location", headers=maya_headers, json={
        "latitude": 40.7580,
        "longitude": -73.9855,
        "accuracy": 8.0
    })
    assert loc_norm.status_code == 200
    assert not loc_norm.json()["is_deviation"]

    # 11. Persistent Off-Route Deviation (3 consecutive updates)
    for _ in range(3):
        loc_dev = client.post(f"/api/v1/tracking/{j1_id}/location", headers=maya_headers, json={
            "latitude": 40.7620,
            "longitude": -73.9800,  # ~350m off route
            "accuracy": 10.0
        })
    assert loc_dev.json()["is_deviation"] is True
    assert loc_dev.json()["prompt_user"] is True
    assert loc_dev.json()["journey_status"] == "deviated"

    # 12. Resolve Deviation: User clicks "I'm Safe" (safe_dismiss)
    res_resp = client.post(f"/api/v1/tracking/{j1_id}/resolve-deviation", headers=maya_headers, json={
        "action": "safe_dismiss"
    })
    assert res_resp.status_code == 200
    assert res_resp.json()["status"] == "ok"

    # 13. Companion Matching: Priya searches for companions for Journey 2 (Maya is in_progress & verified)
    matches_resp = client.get(f"/api/v1/companions/matches/{j2_id}", headers=priya_headers)
    assert matches_resp.status_code == 200
    matches = matches_resp.json()
    assert len(matches) >= 1
    maya_match = matches[0]
    assert maya_match["compatibility_score"] >= 60.0
    assert maya_match["user_display_name"] == "Maya K."
    assert "suggested_meeting_point" in maya_match

    # 14. Priya sends Companion Request to Maya
    req_resp = client.post("/api/v1/companions/requests", headers=priya_headers, json={
        "receiver_journey_id": j1_id,
        "initial_message": "Would love to walk together to campus!"
    })
    assert req_resp.status_code == 201
    req_id = req_resp.json()["id"]

    # 15. Maya receives and accepts the Companion Request
    accept_resp = client.patch(f"/api/v1/companions/requests/{req_id}", headers=maya_headers, json={
        "status": "accepted"
    })
    assert accept_resp.status_code == 200
    assert accept_resp.json()["status"] == "accepted"

    # 16. Mutual companion connection confirmed
    active_group = client.get(f"/api/v1/companions/groups/1", headers=maya_headers)
    assert active_group.status_code == 200
    assert active_group.json()["status"] == "active"
    assert maya_id in active_group.json()["user_ids"]

    # 17. Immediate SOS Action
    sos_resp = client.post("/api/v1/alerts/sos", headers=maya_headers, json={
        "journey_id": j1_id,
        "alert_type": "sos",
        "latitude": 40.7620,
        "longitude": -73.9800,
        "address_text": "Broadway & 52nd St"
    })
    assert sos_resp.status_code == 201
    sos_data = sos_resp.json()
    assert sos_data["status"] == "active"
    assert "Aunt Anita" in sos_data["notifications_sent_json"]

    # 18. Resolve SOS Alert
    resolve_resp = client.post(f"/api/v1/alerts/{sos_data['id']}/resolve", headers=maya_headers, json={
        "resolution_notes": "Connected with companion Priya, safe."
    })
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "resolved"
