import json
from datetime import datetime, timezone, timedelta
from app.database import SessionLocal, engine, Base
from app.models.user import User, VerificationStatus, UserRole
from app.models.verification import Verification, DocumentType
from app.models.journey import Journey, JourneyStatus, TravelMode
from app.models.contact import TrustedContact
from app.utils.security import hash_password
from app.utils.geo import encode_polyline

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing data for clean seed
    if db.query(User).filter(User.email == "admin@safira.org").first():
        print("Database already seeded.")
        db.close()
        return

    print("Seeding database with realistic test profiles...")

    # 1. Admin
    admin = User(
        name="Elena Rostova (Admin)",
        email="admin@safira.org",
        password_hash=hash_password("AdminPass123!"),
        verification_status=VerificationStatus.VERIFIED,
        role=UserRole.ADMIN,
        phone_number="+1 555-0100",
        emergency_note="Staff Admin Account",
        is_email_verified=True
    )
    db.add(admin)
    db.flush()

    # 2. Verified User: Maya Kapoor (Student)
    maya = User(
        name="Maya Kapoor",
        email="maya@university.edu",
        password_hash=hash_password("MayaPass123!"),
        verification_status=VerificationStatus.VERIFIED,
        role=UserRole.USER,
        phone_number="+1 555-0142",
        emergency_note="Carry emergency whistle in front jacket pocket",
        is_email_verified=True
    )
    db.add(maya)
    db.flush()

    # Maya's Verification Record
    verif_maya = Verification(
        user_id=maya.id,
        status=VerificationStatus.VERIFIED,
        document_type=DocumentType.STUDENT_ID,
        verification_reference="VERIF-STUDENT-8821",
        masked_identifier="STU-***-4821",
        submission_notes="Enrolled graduate student at University Metro Campus",
        reviewer_notes="Verified against university enrollment directory",
        reviewed_at=datetime.now(timezone.utc),
        reviewer_id=admin.id
    )
    db.add(verif_maya)

    # Maya's Trusted Contact
    contact_maya = TrustedContact(
        user_id=maya.id,
        contact_name="Aunt Anita",
        contact_phone="+1 555-0199",
        contact_email="anita@family.org",
        relationship="Family Guardian",
        is_primary=True
    )
    db.add(contact_maya)

    # 3. Verified User: Priya Sharma (Researcher)
    priya = User(
        name="Priya Sharma",
        email="priya@citytech.org",
        password_hash=hash_password("PriyaPass123!"),
        verification_status=VerificationStatus.VERIFIED,
        role=UserRole.USER,
        phone_number="+1 555-0188",
        emergency_note="Call roommate Aisha if late",
        is_email_verified=True
    )
    db.add(priya)
    db.flush()

    verif_priya = Verification(
        user_id=priya.id,
        status=VerificationStatus.VERIFIED,
        document_type=DocumentType.INSTITUTIONAL_EMAIL,
        verification_reference="VERIF-INST-9943",
        masked_identifier="RES-***-9943",
        submission_notes="Senior Research Fellow at CityTech Institute",
        reviewer_notes="Institutional domain and ID confirmed",
        reviewed_at=datetime.now(timezone.utc),
        reviewer_id=admin.id
    )
    db.add(verif_priya)

    contact_priya = TrustedContact(
        user_id=priya.id,
        contact_name="Aisha Khan",
        contact_phone="+1 555-0177",
        contact_email="aisha@citytech.org",
        relationship="Roommate",
        is_primary=True
    )
    db.add(contact_priya)

    # 4. Pending User: Chloe Davis
    chloe = User(
        name="Chloe Davis",
        email="chloe@outlook.com",
        password_hash=hash_password("ChloePass123!"),
        verification_status=VerificationStatus.PENDING,
        role=UserRole.USER,
        phone_number="+1 555-0133",
        emergency_note="Emergency contact is brother David",
        is_email_verified=True
    )
    db.add(chloe)
    db.flush()

    verif_chloe = Verification(
        user_id=chloe.id,
        status=VerificationStatus.PENDING,
        document_type=DocumentType.COMMUNITY_REFERRAL,
        verification_reference="VERIF-COMM-1024",
        masked_identifier="REF-***-1024",
        submission_notes="Referred by University Women's Tech Club"
    )
    db.add(verif_chloe)

    # Sample Route Corridors in New York Metro area (or customizable)
    # Origin: Times Square area (40.7580, -73.9855) -> Destination: Columbus Circle / Central Park (40.7681, -73.9819)
    route_points_maya = [
        (40.7580, -73.9855),
        (40.7600, -73.9845),
        (40.7625, -73.9835),
        (40.7650, -73.9825),
        (40.7681, -73.9819)
    ]
    poly_maya = encode_polyline(route_points_maya)

    now = datetime.now(timezone.utc)
    dep_time_maya = now + timedelta(minutes=15)

    journey_maya = Journey(
        user_id=maya.id,
        origin_name="Times Square Station - North Concourse",
        origin_lat=40.7580,
        origin_lng=-73.9855,
        destination_name="Columbus Circle & 59th St",
        destination_lat=40.7681,
        destination_lng=-73.9819,
        travel_mode=TravelMode.WALKING,
        route_data=json.dumps({
            "distance_meters": 1250,
            "duration_seconds": 900,
            "polyline": poly_maya,
            "waypoints": [{"lat": p[0], "lng": p[1]} for p in route_points_maya],
            "bounds": {"min_lat": 40.7580, "max_lat": 40.7681, "min_lng": -73.9855, "max_lng": -73.9819}
        }),
        departure_time=dep_time_maya,
        expected_arrival=dep_time_maya + timedelta(minutes=15),
        status=JourneyStatus.PLANNED,
        is_public_for_matching=True
    )
    db.add(journey_maya)

    # Priya's matching journey: departing 5 mins later, parallel corridor (Broadway / 7th Ave)
    route_points_priya = [
        (40.7585, -73.9850),
        (40.7605, -73.9840),
        (40.7630, -73.9830),
        (40.7655, -73.9822),
        (40.7685, -73.9815)
    ]
    poly_priya = encode_polyline(route_points_priya)
    dep_time_priya = now + timedelta(minutes=20)

    journey_priya = Journey(
        user_id=priya.id,
        origin_name="Broadway & 44th St (Well-Lit Public Corner)",
        origin_lat=40.7585,
        origin_lng=-73.9850,
        destination_name="Central Park South & 7th Ave",
        destination_lat=40.7685,
        destination_lng=-73.9815,
        travel_mode=TravelMode.WALKING,
        route_data=json.dumps({
            "distance_meters": 1280,
            "duration_seconds": 920,
            "polyline": poly_priya,
            "waypoints": [{"lat": p[0], "lng": p[1]} for p in route_points_priya],
            "bounds": {"min_lat": 40.7585, "max_lat": 40.7685, "min_lng": -73.9850, "max_lng": -73.9815}
        }),
        departure_time=dep_time_priya,
        expected_arrival=dep_time_priya + timedelta(minutes=16),
        status=JourneyStatus.PLANNED,
        is_public_for_matching=True
    )
    db.add(journey_priya)

    db.commit()
    print("Seeding completed successfully!")
    print("Test credentials:")
    print("  Admin: admin@safira.org / AdminPass123!")
    print("  Verified User 1: maya@university.edu / MayaPass123!")
    print("  Verified User 2: priya@citytech.org / PriyaPass123!")
    print("  Pending User: chloe@outlook.com / ChloePass123!")
    db.close()

if __name__ == "__main__":
    seed_database()

