# -*- coding: utf-8 -*-
"""
Chapter 6: Implementation and Working for the Master Academic Project Report on Safira.
"""

def get_chapter_6():
    return r"""# CHAPTER 6
# IMPLEMENTATION AND WORKING

## 6.1 Project Directory Structure & Organization

The codebase of Safira is organized as a clean, modular monorepo cleanly decoupling the React 19 frontend client from the FastAPI asynchronous backend services. Figure 6.1 documents the directory layout of the complete project repository.

```
women-safety-agent/
 ├── .env.local                       # Local environment secrets (LocationIQ API Key)
 ├── .gitignore                        # Git exclusion rules (node_modules, .env, *.db)
 ├── package.json                      # Frontend dependencies, scripts, Vite build config
 ├── tsconfig.json                     # TypeScript strict configuration
 ├── vite.config.ts                    # Vite dev server and proxy definitions
 ├── README.md                         # Project documentation and quickstart instructions
 ├── index.html                        # HTML5 root template mounting React root
 │
 ├── src/                              # Frontend React 19 Source Code
 │    ├── main.tsx                     # Entry point bootstrapping React into DOM
 │    ├── App.tsx                      # Root component configuring routing & layout
 │    ├── index.css                    # Tailwind CSS 4.0 directives & base styles
 │    ├── types/                       # TypeScript shared interfaces and DTOs
 │    │    ├── auth.ts                 # User, Token, Verification status interfaces
 │    │    ├── journey.ts              # Coordinate, Waypoint, Journey, Alert types
 │    │    └── companion.ts            # CompanionTrip, Request, Message models
 │    ├── context/
 │    │    └── AuthContext.tsx         # Global JWT state, user profile, login/logout
 │    ├── components/
 │    │    ├── Navbar.tsx              # Top navigation bar with safety status indicators
 │    │    ├── MapView.tsx             # Interactive Leaflet map container with LocationIQ
 │    │    ├── DeviationModal.tsx      # 60-second interactive deviation safety challenge
 │    │    └── RouteCard.tsx           # Journey summary card component
 │    └── pages/
 │         ├── LandingPage.tsx         # Redesigned hero section with radar preview
 │         ├── LoginPage.tsx           # Authentication sign-in form
 │         ├── SignupPage.tsx          # Account registration with BCrypt clamping
 │         ├── CreateJourneyPage.tsx   # LocationIQ Autocomplete route planner
 │         ├── JourneyMonitoringPage.tsx # Live GPS tracking & deviation engine container
 │         ├── JourneyBuddyPage.tsx    # "Travel Together" companion matching hub
 │         ├── GuardiansPage.tsx       # Emergency contacts and historical distress logs
 │         ├── SOSPanel.tsx            # One-touch emergency panic dispatch screen
 │         └── VerificationPage.tsx    # Identity document submission & admin portal
 │
 ├── backend/                          # Backend FastAPI Python Source Code
 │    ├── app/
 │    │    ├── main.py                 # FastAPI application factory, CORS, exception handlers
 │    │    ├── core/
 │    │    │    ├── config.py          # App settings, secrets, environment variables
 │    │    │    ├── database.py        # SQLAlchemy engine, session maker, base model
 │    │    │    └── security.py        # BCrypt hashing, JWT encoding/decoding
 │    │    ├── models/                 # SQLAlchemy 2.0 ORM database entity classes
 │    │    │    ├── user.py            # User and verification document tables
 │    │    │    ├── journey.py         # Journeys, waypoints, and deviation logs
 │    │    │    ├── guardian.py        # Trusted guardians and SOS distress tables
 │    │    │    └── companion.py       # Companion trips, match requests, and messages
 │    │    ├── schemas/                # Pydantic v2 validation DTOs
 │    │    │    ├── auth.py            # Signup, login, and user profile schemas
 │    │    │    ├── journey.py         # Route creation and coordinate telemetry schemas
 │    │    │    └── companion.py       # Trip scheduling and message schemas
 │    │    ├── api/                    # Modular RESTful route controllers
 │    │    │    ├── auth.py            # /api/auth routes
 │    │    │    ├── journeys.py        # /api/journeys routes
 │    │    │    ├── companions.py      # /api/companions routes
 │    │    │    ├── guardians.py       # /api/guardians and /api/sos routes
 │    │    │    └── verification.py   # /api/verification routes
 │    │    └── services/
 │    │         ├── spatial.py         # Geodesic Haversine & cross-track algorithms
 │    │         └── matching.py        # Spatio-temporal companion compatibility engine
 │    └── requirements.txt             # Python backend dependencies
 │
 └── tests/                            # Automated Testing Suite
      ├── test_api.py                 # Pytest suites for auth, journeys, and SOS
      └── test_companions.py          # Pytest suites for companion matching and chat
```

*Figure 6.1: Modular Monolithic Directory Structure of the Backend and Frontend Repository*

---

## 6.2 User Registration, Sanitization & Manual Verification Workflow

The user onboarding subsystem enforces rigorous input sanitization, cryptographic password hashing, and a multi-stage identity verification workflow.

```
[ User Enters Credentials ] 
         │
         ▼
[ Frontend Input Validation ] ─── Validates email format, phone digits, password rules
         │
         ▼
[ Password Clamping (<=72B) ] ─── Truncates/guards against BCrypt silent byte overflow
         │
         ▼
[ POST /api/auth/signup ]
         │
         ▼
[ Check Email Uniqueness ] ───── If duplicate -> 400 Bad Request ("Email already in use")
         │
         ▼
[ BCrypt Password Hashing ] ──── Blowfish cipher with random salt (12 work rounds)
         │
         ▼
[ Insert Database Record ] ───── user.is_verified = False, status = "Pending"
         │
         ▼
[ Admin Document Review ] ────── Admin reviews submitted ID in /api/verification
         │
    ┌────┴────────────────────────┐
    ▼                             ▼
[ Approved: is_verified=True ]   [ Rejected: status='Rejected' ]
    │                             │
    ▼                             ▼
[ Full Access to Journey Buddy ] [ Restricted to Solo Journey Monitoring ]
```

### Password Clamping and Hash Implementation
To mitigate BCrypt's architectural 72-byte truncation vulnerability, the backend implements defensive clamping:

```python
# backend/app/core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    # Defensively clamp password to 72 bytes to prevent BCrypt truncation anomalies
    password_bytes = password.encode("utf-8")[:72]
    return pwd_context.hash(password_bytes.decode("utf-8", errors="ignore"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    clamped_bytes = plain_password.encode("utf-8")[:72]
    return pwd_context.verify(clamped_bytes.decode("utf-8", errors="ignore"), hashed_password)
```

### Identity Verification Gating
During initial registration, all accounts are assigned `is_verified = False` and `verification_status = "Pending"`. Users upload identity documents (student ID, national identity card, or corporate work badge) via `/api/verification/upload`. An administrative review interface allows authorized staff to inspect submissions and update statuses. The `is_verified` flag acts as an immutable prerequisite for accessing companion matching APIs.

---

## 6.3 JWT Security Filter & Role-Based Access Control

Safira utilizes FastAPI's dependency injection system to establish declarative, reusable security gates across all endpoints.

```python
# backend/app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def require_verified_woman(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: Verified female account required for Journey Buddy matching."
        )
    return current_user
```

Endpoints decorated with `Depends(require_verified_woman)` automatically reject unverified accounts with an HTTP 403 Forbidden status, ensuring travel companion features remain strictly accessible to authenticated female commuters.

---

## 6.4 Journey Creation, LocationIQ Autocomplete & Reverse Geocoding

The journey planning interface (`CreateJourneyPage.tsx`) provides high-speed, debounced destination search powered by the LocationIQ Autocomplete API.

```typescript
// Debounced Autocomplete Handler in CreateJourneyPage.tsx
const handleSearch = useCallback(
  debounce(async (query: string, field: 'origin' | 'destination') => {
    if (!query || query.trim().length < 3) return;
    try {
      const response = await axios.get('https://api.locationiq.com/v1/autocomplete', {
        params: {
          key: import.meta.env.VITE_LOCATIONIQ_API_KEY,
          q: query,
          limit: 5,
          countrycodes: 'in,us',
          format: 'json'
        }
      });
      if (field === 'origin') {
        setOriginSuggestions(response.data);
      } else {
        setDestinationSuggestions(response.data);
      }
    } catch (error) {
      console.error('LocationIQ autocomplete failed:', error);
    }
  }, 300),
  []
);
```

### Route Polyline Fetching
When the user confirms both origin and destination points, Safira queries LocationIQ’s Directions API (`/v1/directions/driving/` or `/v1/directions/walking/`). The API returns a high-precision polyline geometry representing the recommended trajectory. Safira stores this polyline in the journey entity and passes the coordinate array directly to the Leaflet map renderer.

---

## 6.5 Interactive MapView Component: LocationIQ Tiles & Custom GIS Markers

The cartography component (`MapView.tsx`) encapsulates the Leaflet map instance, tile layers, polyline rendering, and custom DOM markers.

```typescript
// MapView.tsx Leaflet Initialization
useEffect(() => {
  if (!mapContainerRef.current) return;

  const mapInstance = L.map(mapContainerRef.current, {
    zoomControl: false,
    attributionControl: false
  }).setView([initialLat, initialLon], 14);

  // LocationIQ Streets Tile Layer with Night Mode Support
  const tileUrl = isNightMode
    ? `https://{s}-tiles.locationiq.com/v3/streets/r/{z}/{x}/{y}.png?key=${apiKey}`
    : `https://{s}-tiles.locationiq.com/v3/streets/r/{z}/{x}/{y}.png?key=${apiKey}`;

  L.tileLayer(tileUrl, {
    maxZoom: 19,
    subdomains: ['a', 'b', 'c']
  }).addTo(mapInstance);

  // Render Planned Route Polyline
  if (routeCoordinates && routeCoordinates.length > 0) {
    const latLngs = routeCoordinates.map(c => [c.latitude, c.longitude] as [number, number]);
    const routeLine = L.polyline(latLngs, {
      color: '#EC4899', // Rose safety primary
      weight: 5,
      opacity: 0.85,
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(mapInstance);
    mapInstance.fitBounds(routeLine.getBounds(), { padding: [40, 40] });
  }

  // Pulsing GPS Beacon Marker
  const pulsingIcon = L.divIcon({
    className: 'custom-pulsing-marker',
    html: `<div class="relative flex items-center justify-center">
             <div class="absolute w-8 h-8 bg-pink-500 rounded-full animate-ping opacity-75"></div>
             <div class="relative w-4 h-4 bg-pink-600 rounded-full border-2 border-white shadow-lg"></div>
           </div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16]
  });

  const userMarker = L.marker([currentLat, currentLon], { icon: pulsingIcon }).addTo(mapInstance);

  return () => {
    mapInstance.remove();
  };
}, [isNightMode, routeCoordinates]);
```

The map features an interactive toggle between standard daytime street cartography and high-contrast night safety mode, custom SVG icons for safe meeting checkpoints, and an animated radial beacon highlighting the user's real-time position.

---

## 6.6 Real-Time Route Deviation Detection Engine

The core anomaly detection engine runs locally within the user's browser runtime during an active journey, polling coordinates every 5 to 10 seconds via `navigator.geolocation.watchPosition`.

```typescript
// Client-Side Deviation Detection Logic in JourneyMonitoringPage.tsx
const evaluateCorridorDeviation = (
  userLat: number,
  userLon: number,
  gpsAccuracy: number,
  polylineCoords: Coordinate[]
) => {
  // Compute minimum cross-track distance across all segments
  let minDistanceMeters = Infinity;

  for (let i = 0; i < polylineCoords.length - 1; i++) {
    const p1 = polylineCoords[i];
    const p2 = polylineCoords[i + 1];
    const segmentDistance = calculatePerpendicularDistance(
      userLat, userLon,
      p1.latitude, p1.longitude,
      p2.latitude, p2.longitude
    );
    if (segmentDistance < minDistanceMeters) {
      minDistanceMeters = segmentDistance;
    }
  }

  // Dynamic threshold incorporating GPS horizontal accuracy
  const effectiveThreshold = 150 + Math.min(gpsAccuracy, 50);

  if (minDistanceMeters > effectiveThreshold) {
    consecutiveBreachCountRef.current += 1;
    if (consecutiveBreachCountRef.current >= 3) {
      // 3 consecutive off-route fixes confirm persistent deviation
      triggerDeviationChallenge(minDistanceMeters, effectiveThreshold);
    }
  } else {
    // Reset persistence counter when returning to safety corridor
    consecutiveBreachCountRef.current = 0;
  }
};
```

When a persistent deviation is confirmed, the application launches an interactive 60-second modal dialog (`DeviationModal.tsx`). The modal plays an auditory chime and prompts the traveler: **"Are you safe? You appear off your planned route."** 

If the traveler taps **"I am Safe"**, the persistence counter resets to zero and monitoring resumes. If the traveler taps **"Update Route"**, a new polyline is computed from the current location. If the 60-second timer elapses with zero user interaction, the system autonomously triggers the Emergency SOS protocol.

---

## 6.7 Instant Emergency SOS System & Multi-Channel Guardian Dispatch

The emergency distress system (`SOSPanel.tsx`) provides an immediate, high-priority intervention protocol accessible at any time via a dedicated one-touch panic button.

When triggered, the system:
1. Immediately samples high-accuracy GPS coordinates from the device sensor.
2. Dispatches a high-priority `POST /api/sos/trigger` request to the backend.
3. The backend executes a reverse-geocoding lookup via LocationIQ to determine the localized street address (e.g., *"Opposite Central Bus Station, Jhalawar Road, Kota"*).
4. Persists the incident in the `sos_alerts` database table.
5. Queries the user's configured emergency guardians from the `guardians` table.
6. Simulates multi-channel SMS and Email dispatch to all designated guardians containing the user's name, timestamp, resolved street address, and a secure live tracking URL.

```python
# backend/app/api/guardians.py - SOS Dispatch Handler
@router.post("/sos/trigger", response_model=SOSAlertResponse)
async def trigger_emergency_sos(
    payload: SOSAlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Reverse geocode coordinates using LocationIQ
    street_address = await reverse_geocode_locationiq(payload.latitude, payload.longitude)
    
    alert = SOSAlert(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        street_address=street_address,
        trigger_mode=payload.trigger_mode or "manual_panic",
        resolved=False
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    # Broadcast alert to all active registered guardians
    guardians = db.query(Guardian).filter(Guardian.user_id == current_user.id).all()
    dispatch_guardian_broadcast(guardians, current_user.full_name, alert)
    
    return alert
```

---

## 6.8 Journey Buddy: Collaborative Travel Scheduling & Discovery Interface

The "Journey Buddy" module (`JourneyBuddyPage.tsx`) enables verified female commuters to schedule future trips and discover compatible travel companions.

```
[ Verified Female User ] ─── Enters Origin, Destination, Departure Time, Travel Mode
           │
           ▼
[ POST /api/companions/trips ] ─── Persists Scheduled Trip
           │
           ▼
[ Matching Engine Query ] ─────── Scans trips matching time window (+/- 45 mins)
           │
           ▼
[ Spatio-Temporal Compatibility Evaluation ]
 - Spatial Origin Proximity (w1 = 0.35)
 - Temporal Alignment (w2 = 0.25)
 - Destination Proximity (w3 = 0.20)
 - Travel Mode Concordance (w4 = 0.10)
 - Trust & Verification Score (w5 = 0.10)
           │
           ▼
[ Attach Nearest Public Safe Rendezvous POI ]
           │
           ▼
[ Render Candidate Cards with Compatibility % & Safe Meeting Point ]
```

When browsing available companions, users are presented with candidate cards displaying:
- Masked name (e.g., *"Priya S."*) and verified badge.
- Departure time bracket and travel mode (Metro, Bus, Walking, Auto-Rickshaw).
- Normalized compatibility rating (e.g., **94% Match**).
- Recommended public meeting checkpoint (e.g., *"Metro Gate 2 Coffee Stand - 24/7 Monitored"*).
- Direct **"Connect"** button to dispatch a companion request.

---

## 6.9 Encrypted In-App Coordination Chat for Confirmed Companions

To protect commuter privacy and eliminate the need to share personal phone numbers or social media handles, Safira provides a sandboxed, encrypted in-app messaging channel.

- **Mutual Acceptance Gate:** The chat interface is strictly inaccessible until the recipient explicitly accepts a companion connection request (`status = "accepted"`).
- **In-App Message Threading:** Messages are linked to the specific `request_id`, providing localized context for the scheduled commute.
- **Privacy Protections:** The chat interface does not display personal phone numbers, home addresses, or external contact links, allowing users to coordinate meeting logistics securely.

---

## 6.10 Redesigned Startup-Grade Landing Page UI

To maximize user trust, empathetic communication, and project evaluation appeal, the landing page (`LandingPage.tsx`) was completely redesigned as a modern, startup-grade web experience:
- **Hero Section:** Features a bold, protective headline (*"Your Safety. Your Journey. Our Priority."*) paired with an animated interactive radar preview demonstrating live corridor deviation monitoring.
- **Six Core Capability Cards:** Highlights Real-Time Route Monitoring, 150m Deviation Shield, Journey Buddy Matching, One-Touch SOS Dispatch, Zero-Knowledge Privacy, and Safe Public Checkpoints.
- **Four-Step Workflow Visualizer:** Clear progression demonstrating: Plan Route $\rightarrow$ Verify Trajectory $\rightarrow$ Travel in Pairs $\rightarrow$ Autonomous Escalation.
- **One-Click Evaluator Test Accounts:** Provides pre-configured test credentials (`Priya Sharma - Verified`, `Ananya Verma - Pending`, `Admin Reviewer`) enabling academic evaluators to test all user roles with a single click.

<div style="page-break-after: always;"></div>
"""
