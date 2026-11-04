# Safira — Women's Travel Safety & Companion Matching Platform

> **A functional, privacy-conscious MVP engineered to help verified women monitor journeys, detect unexpected route deviations, and optionally connect with other verified women travelling along similar corridors.**

---

## 1. Project Overview & Architecture

Safira provides two tightly integrated safety capabilities:
1. **Journey Monitoring & Route Deviation Detection**: Continuous comparison of GPS coordinates against planned route geometry with GPS accuracy filtering, persistent anomaly detection, interactive check-ins, and automated emergency escalation to trusted contacts.
2. **Deterministic Travel Companion Matching**: Rule-based matching that computes route corridor overlap, departure time compatibility, and destination proximity to connect verified women at safe, public meeting points without ever publishing exact street addresses or live raw GPS coordinates to potential matches.

### Architecture Overview
```
┌────────────────────────────────────────────────────────────────┐
│                       React 19 + TypeScript                     │
│  - Tailwind CSS Styling                                        │
│  - Interactive Dual-Mode MapView (Google Maps + Vector Canvas) │
│  - Browser Geolocation API + Real-Time Route Simulator        │
│  - 10 Dedicated Responsive Pages                               │
└───────────────────────────────┬────────────────────────────────┘
                                │ JSON API (JWT Bearer Auth)
┌───────────────────────────────▼────────────────────────────────┐
│                     FastAPI Modular Backend                    │
│  - Auth Service (JWT + Bcrypt)                                 │
│  - Eligibility Verification Engine (Pending/Verified/Rejected)  │
│  - Geospatial Engine (Haversine, Cross-Track, Corridor Poly)   │
│  - Route Deviation Service (GPS Accuracy Filter + Persistence) │
│  - Companion Matching Engine (Deterministic Rule-Based)        │
│  - Emergency Alert Dispatcher (Immediate SOS + Timeout Logs)   │
└───────────────────────────────┬────────────────────────────────┘
                                │ SQLAlchemy 2.0 ORM
┌───────────────────────────────▼────────────────────────────────┐
│              PostgreSQL + PostGIS (Production Target)          │
│                SQLite Engine (Zero-Config Local Dev)           │
│                 Alembic Database Version Migrations            │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

- **Frontend**:
  - React 19, TypeScript
  - Tailwind CSS
  - React Router DOM
  - Lucide React Icons
  - Interactive Map Component with Google Maps JavaScript API support + fallback high-precision Cartographic SVG/Canvas Renderer
  - Browser Geolocation API
- **Backend**:
  - Python 3.14
  - FastAPI
  - SQLAlchemy 2.0 (PostgreSQL / PostGIS compatible, SQLite fallback for local testability)
  - Pydantic v2 & Pydantic-Settings
  - Alembic for database migrations
  - PyJWT & Bcrypt for authentication & security
  - HTTPX for asynchronous Maps & Places API requests
  - Pytest & Pytest-Asyncio

---

## 3. Directory Structure

```
women safety agent/
├── backend/
│   ├── alembic/                    # Database migrations
│   │   ├── versions/
│   │   │   └── 4467090a62b8_initial_schema.py
│   │   └── env.py
│   ├── app/
│   │   ├── api/                    # Modular API route controllers
│   │   │   ├── alerts.py           # Immediate SOS & Alert resolution
│   │   │   ├── auth.py             # User signup, login, profile
│   │   │   ├── companions.py       # Candidate discovery & mutual requests
│   │   │   ├── contacts.py         # Trusted emergency contacts CRUD
│   │   │   ├── journeys.py         # Journey creation & status lifecycle
│   │   │   ├── tracking.py         # GPS telemetry & deviation resolution
│   │   │   └── verification.py     # Privacy-first eligibility submission
│   │   ├── models/                 # SQLAlchemy database models
│   │   │   ├── alert.py            # EmergencyAlert
│   │   │   ├── companion.py        # CompanionRequest, CompanionGroup
│   │   │   ├── contact.py          # TrustedContact
│   │   │   ├── journey.py          # Journey
│   │   │   ├── location.py         # LocationUpdate
│   │   │   ├── user.py             # User
│   │   │   └── verification.py     # Verification
│   │   ├── schemas/                # Pydantic validation schemas
│   │   ├── services/               # Core business logic & algorithms
│   │   │   ├── auth_service.py
│   │   │   ├── deviation_service.py # GPS accuracy & persistent deviation
│   │   │   ├── maps_service.py      # Google Routes & Places integration
│   │   │   ├── matching_service.py  # Deterministic matching algorithm
│   │   │   ├── notification_service.py # Emergency dispatch to contacts
│   │   │   └── verification_service.py
│   │   ├── utils/
│   │   │   ├── geo.py              # Haversine, cross-track, polyline decode
│   │   │   └── security.py         # Password hashing & JWT
│   │   ├── config.py               # Environment configuration
│   │   ├── database.py             # Engine & session management
│   │   └── main.py                 # FastAPI application instance
│   ├── tests/                      # Comprehensive test suite (11 passing tests)
│   │   ├── test_alerts.py
│   │   ├── test_auth.py
│   │   ├── test_deviation.py
│   │   ├── test_e2e_flow.py        # End-to-end full lifecycle integration
│   │   ├── test_geo.py
│   │   └── test_matching.py
│   ├── requirements.txt
│   ├── seed.py                     # Realistic database seeder
│   ├── alembic.ini
│   ├── .env.example
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts           # Type-safe API client
│   │   ├── components/
│   │   │   ├── DeviationModal.tsx  # Safety check-in countdown modal
│   │   │   ├── MapView.tsx         # Interactive Map (Google Maps + Canvas)
│   │   │   ├── Navbar.tsx          # Responsive navigation & status badges
│   │   │   └── SOSButton.tsx       # Immediate one-tap emergency distress
│   │   ├── context/
│   │   │   └── AuthContext.tsx     # Global auth state & session
│   │   ├── pages/
│   │   │   ├── ActiveCompanionJourneyPage.tsx # Coordinated shared journey
│   │   │   ├── AdminVerificationPage.tsx      # Admin verification review
│   │   │   ├── AuthPage.tsx                   # Registration & Login
│   │   │   ├── CompanionDiscoveryPage.tsx     # Corridor matching discovery
│   │   │   ├── CompanionRequestsPage.tsx      # Mutual requests incoming/outgoing
│   │   │   ├── CreateJourneyPage.tsx          # Route planning & preview
│   │   │   ├── DashboardPage.tsx              # Overview & active journey HUD
│   │   │   ├── LandingPage.tsx                # Product value & quick test logins
│   │   │   ├── LiveJourneyPage.tsx            # Live GPS tracking & simulator
│   │   │   ├── ProfileSettingsPage.tsx        # Contacts & alert history
│   │   │   └── VerificationPage.tsx           # Eligibility submission
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
└── README.md
```

---

## 4. Safety & Matching Algorithms

### A. GPS Accuracy Filtering & Route Deviation
1. **GPS Accuracy Filtering**: Standard GPS on mobile browsers experiences jitter (accuracy circle: 10m - 100m+). If `accuracy > GPS_ACCURACY_THRESHOLD_METERS (50m)` and reported distance to route is within reported accuracy radius, the system **does not trigger false alarms**.
2. **Persistent Route Deviation Detection**:
   - Compares perpendicular distance $d$ from user coordinates to each segment of the planned route polyline.
   - If $d > 150\text{m}$ with acceptable accuracy, increments `consecutive_deviations`.
   - When `consecutive_deviations >= 3`, marks status `DEVIATED` and surfaces the check-in modal.
3. **Timed Escalation**:
   - The user is prompted: *"Did you intentionally change your route?"*
   - Options: *"I'm Safe (Intentional Detour)"*, *"Update Route"*, *"Request Help"*.
   - If unanswered within 60 seconds (configurable countdown), marks status `ATTENTION_REQUIRED`, dispatches emergency notification with exact coordinates and timestamp to all configured trusted contacts.
4. **Immediate One-Tap SOS**:
   - Available on all monitoring screens; bypasses deviation timeouts and alerts contacts instantly.

### B. Deterministic Companion Matching
Safira calculates compatibility **deterministically** without black-box ML:
$$\text{Score} = (0.40 \times \text{Overlap\%}) + (0.30 \times \text{TimeScore}) + (0.20 \times \text{DestScore}) + (0.10 \times \text{ModeScore})$$
- **Eligibility Barrier**: Only accounts with `verification_status == VERIFIED` are matched.
- **Corridor Overlap**: Projects piecewise coordinates within a 300m buffer corridor.
- **Departure Window**: Filtered to departures within $\le 45$ minutes.
- **Destination Proximity**: Compares arrival coordinates within $\le 2.5\text{km}$.
- **Public Meeting Spot Discovery**: Discovers verified safe public hubs (transit stations with CCTV, 24/7 staffed cafes, public civic libraries) via Google Places API or curated hubs.

### C. Privacy Architecture
- Exact street addresses (e.g. flat number, house) are **never revealed** to prospective companions.
- Raw live GPS is never broadcast to unapproved users.
- Matching candidates only see an **approximate corridor** until both users mutually **Accept** the companion request.
- Mutual disconnect / block / report options are available at any time.

---

## 5. Quick Start Instructions

### Prerequisites
- Node.js (v18+) & npm
- Python (v3.11+)

### Backend Setup
1. Open PowerShell and navigate to the backend directory:
   ```powershell
   cd "women safety agent"
   ```
2. Activate or use Python environment:
   ```powershell
   $env:PYTHONPATH = "$PWD\venv\Lib\site-packages;$PWD\backend"
   ```
3. Run database migrations:
   ```powershell
   & "C:\Users\SONAM KHANAM\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m alembic -c backend\alembic.ini upgrade head
   ```
4. Seed realistic test accounts and journeys:
   ```powershell
   & "C:\Users\SONAM KHANAM\AppData\Local\Python\pythoncore-3.14-64\python.exe" backend\seed.py
   ```
5. Start the FastAPI backend server:
   ```powershell
   & "C:\Users\SONAM KHANAM\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
   ```
   API Docs available at: `http://localhost:8000/docs`

### Frontend Setup
1. In another terminal, navigate to `frontend`:
   ```powershell
   cd "women safety agent\frontend"
   npm run dev
   ```
2. Open your browser at `http://localhost:5173`.

---

## 6. Pre-Configured Test Credentials

| Account | Email | Password | Role / Status | Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Admin Reviewer** | `admin@safira.org` | `AdminPass123!` | Admin / Verified | Access Admin Eligibility Verification Portal |
| **Maya Kapoor** | `maya@university.edu` | `MayaPass123!` | User / Verified | Planned corridor from Times Square to Central Park |
| **Priya Sharma** | `priya@citytech.org` | `PriyaPass123!` | User / Verified | High-compatibility match (parallel Broadway corridor) |
| **Chloe Davis** | `chloe@outlook.com` | `ChloePass123!` | User / Pending | Unverified applicant (demonstrates eligibility gate) |

*(One-click quick login buttons for all these test accounts are also embedded directly on the Landing Page!)*

---

## 7. Running Backend Tests

Run the full automated test suite (11 comprehensive unit & integration tests):
```powershell
$env:PYTHONPATH = "$PWD\venv\Lib\site-packages;$PWD\backend"
& "C:\Users\SONAM KHANAM\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m pytest -v -p no:cacheprovider backend\tests
```
All 11 tests pass:
- `test_sos_and_trusted_contact_notifications`
- `test_user_registration_and_login`
- `test_unverified_user_cannot_access_companion_matching`
- `test_deviation_detection_with_gps_accuracy`
- `test_deviation_timeout_escalation`
- `test_full_journey_safety_and_companion_matching_lifecycle`
- `test_haversine_distance`
- `test_polyline_encoding_decoding`
- `test_point_to_polyline_distance`
- `test_route_overlap_calculation`
- `test_companion_matching_rule_based`

