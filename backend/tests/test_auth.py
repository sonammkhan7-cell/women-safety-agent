import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User, VerificationStatus, UserRole

from sqlalchemy.pool import StaticPool

# Use in-memory SQLite with StaticPool for isolated testing
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
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

def test_user_registration_and_login():
    # Register user
    reg_resp = client.post("/api/v1/auth/register", json={
        "name": "Sarah Connor",
        "email": "sarah@example.com",
        "password": "Password123!",
        "phone_number": "+1234567890",
        "emergency_note": "Asthma inhaler in bag"
    })
    assert reg_resp.status_code == 201
    data = reg_resp.json()
    assert data["email"] == "sarah@example.com"
    assert data["verification_status"] == "pending"

    # Login
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "sarah@example.com",
        "password": "Password123!"
    })
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Get profile
    token = token_data["access_token"]
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["name"] == "Sarah Connor"

def test_unverified_user_cannot_access_companion_matching():
    # Register first user (admin in auto mode) and second user
    client.post("/api/v1/auth/register", json={
        "name": "Admin User", "email": "admin@example.com", "password": "Password123!"
    })
    user2_resp = client.post("/api/v1/auth/register", json={
        "name": "Unverified Woman", "email": "unverified@example.com", "password": "Password123!"
    })
    token_resp = client.post("/api/v1/auth/login", json={
        "email": "unverified@example.com", "password": "Password123!"
    })
    token = token_resp.json()["access_token"]

    # Try accessing companion matches without verification
    resp = client.get("/api/v1/companions/matches/1", headers={"Authorization": f"Bearer {token}"})
    # Should be 403 Forbidden
    assert resp.status_code == 403
    assert "Eligibility verification required" in resp.json()["detail"]
