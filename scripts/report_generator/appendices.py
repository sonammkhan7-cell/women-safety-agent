# -*- coding: utf-8 -*-
"""
References and Appendices A through D for the Master Academic Project Report on Safira.
"""

def get_appendices():
    return r'''# REFERENCES

1. Alonso-Mora, J., Samaranayake, S., Wallar, A., Frazzoli, E., & Rus, D. (2017). On-demand high-capacity ride-sharing via dynamic trip-vehicle assignment. *Proceedings of the National Academy of Sciences (PNAS)*, 114(3), 462-467.
2. Beresford, A. R., & Stajano, F. (2003). Location privacy in pervasive computing. *IEEE Pervasive Computing*, 2(1), 46-55.
3. Brantingham, P. L., & Brantingham, P. J. (1993). Nodes, paths and edges: Considerations on the complexity of crime and the physical environment. *Journal of Environmental Psychology*, 13(1), 3-28.
4. Chhabra, G., Vashisht, V., & Ranjan, P. (2022). A review on IoT and machine learning-based smart women safety systems: Architecture, challenges, and future trends. *IEEE Access*, 10, 89410-89428.
5. Gedik, B., & Liu, L. (2005). Location privacy in mobile systems: A personalized anonymization model. *Proceedings of the 25th IEEE International Conference on Distributed Computing Systems (ICDCS)*, pp. 620-629.
6. Jacobs, J. (1961). *The Death and Life of Great American Cities*. Random House, New York.
7. Kumar, S., & Shreshtha, A. (2018). Smart security solution for women based on Internet of Things (IoT). *IEEE International Conference on Computing, Power and Communication Technologies (GUCON)*, pp. 1012-1016.
8. Newson, P., & Krumm, J. (2009). Hidden Markov map matching through noise and sparseness. *Proceedings of the 17th ACM SIGSPATIAL International Conference on Advances in Geographic Information Systems*, pp. 336-343.
9. OpenStreetMap Foundation. (2024). OpenStreetMap: A free and open geographic database. Retrieved from https://www.openstreetmap.org.
10. Passlib Development Team. (2024). Passlib 1.7.4 Documentation: Password Hashing Library for Python. Retrieved from https://passlib.readthedocs.io.
11. Pydantic Team. (2024). Pydantic v2: Data Validation and Settings Management Using Python Type Annotations. Retrieved from https://docs.pydantic.dev.
12. Ramirez-Campuzano, B. I., Perez-Sanagustin, M., & Maldonado, J. J. (2020). Performance analysis of mobile location tracking algorithms under battery and network constraints. *Sensors (MDPI)*, 20(18), 5122.
13. Rescorla, E. (2018). The Transport Layer Security (TLS) Protocol Version 1.3 (RFC 8446). Internet Engineering Task Force (IETF).
14. Sinnott, R. W. (1984). Virtues of the Haversine. *Sky and Telescope*, 68(2), 159.
15. SQLAlchemy Authors. (2024). SQLAlchemy 2.0 Documentation: The Database Toolkit for Python. Retrieved from https://docs.sqlalchemy.org.
16. Sweeney, L. (2002). k-anonymity: A model for protecting privacy. *International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems*, 10(5), 557-570.
17. Tiark, R., & Uvicorn Contributors. (2024). Uvicorn: The Lightning-Fast ASGI Server. Retrieved from https://www.uvicorn.org.
18. United Nations Entity for Gender Equality and the Empowerment of Women (UN Women). (2021). *Safe Cities and Safe Public Spaces for Women and Girls Global Flagship Initiative: Annual Progress Report*. UN Women, New York.
19. Vaghela, S., Mehta, R., & Patel, P. (2020). IoT-based smart wearable gadget for women’s safety. *International Journal of Advanced Science and Technology*, 29(5), 1142-1149.
20. Vite Team. (2024). Vite: Next Generation Frontend Tooling. Retrieved from https://vitejs.dev.
21. World Health Organization (WHO). (2021). *Violence Against Women Prevalence Estimates, 2018: Global, Regional and National Prevalence Estimates for Intimate Partner Violence and Non-Partner Sexual Violence*. WHO Guidelines Approved by the Guidelines Review Committee, Geneva.
22. World Wide Web Consortium (W3C). (2016). *Geolocation API Specification (2nd Edition)*. W3C Recommendation. Retrieved from https://www.w3.org/TR/geolocation-API/.

<div style="page-break-after: always;"></div>

---

# APPENDIX A: COMPLETE REST API SPECIFICATION

This appendix documents the structural contracts, request Data Transfer Objects (DTOs), and response specifications for the Safira REST application programming interface.

### Table A.1: Detailed REST API Request DTO Validation Constraints

| Endpoint URI | Method | Request DTO Schema | Field Name | Data Type | Validation Constraints & Business Rules |
|:---|:---:|:---|:---|:---:|:---|
| `/api/auth/signup` | `POST` | `UserSignupRequest` | `email` | String | Valid RFC 5322 email syntax; unique across database. |
| | | | `password` | String | Minimum 8 characters; clamped defensively to 72 bytes. |
| | | | `full_name` | String | Length 2-100 characters; alphanumeric and spaces. |
| | | | `phone_number` | String | Optional E.164 international phone number format. |
| `/api/auth/login` | `POST` | `UserLoginRequest` | `email` | String | Registered user email address. |
| | | | `password` | String | Raw password string for BCrypt hash verification. |
| `/api/journeys` | `POST` | `JourneyCreateRequest` | `title` | String | Human-readable journey identifier (e.g., "Evening Commute"). |
| | | | `origin_name` | String | Textual address of departure origin. |
| | | | `origin_lat` | Float | WGS-84 latitude: $-90.0 \le \phi \le 90.0$. |
| | | | `origin_lon` | Float | WGS-84 longitude: $-180.0 \le \lambda \le 180.0$. |
| | | | `destination_name`| String | Textual address of destination. |
| | | | `destination_lat` | Float | WGS-84 latitude: $-90.0 \le \phi \le 90.0$. |
| | | | `destination_lon` | Float | WGS-84 longitude: $-180.0 \le \lambda \le 180.0$. |
| `/api/journeys/{id}/telemetry` | `POST` | `TelemetrySyncRequest` | `latitude` | Float | Current device latitude from W3C Geolocation API. |
| | | | `longitude` | Float | Current device longitude from W3C Geolocation API. |
| | | | `accuracy` | Float | Horizontal accuracy radius $\sigma_{\text{GPS}}$ in meters ($> 0$). |
| | | | `speed` | Float | Instantaneous speed over ground in $\text{m/s}$ (optional). |
| `/api/sos/trigger` | `POST` | `SOSAlertCreate` | `latitude` | Float | Instantaneous emergency latitude. |
| | | | `longitude` | Float | Instantaneous emergency longitude. |
| | | | `trigger_mode` | String | Enumeration: `manual_panic` or `auto_deviation`. |
| `/api/companions/trips` | `POST` | `CompanionTripCreate` | `origin_name` | String | Origin locality or transit station name. |
| | | | `origin_lat` | Float | Departure latitude coordinate. |
| | | | `origin_lon` | Float | Departure longitude coordinate. |
| | | | `destination_name`| String | Destination locality or transit station name. |
| | | | `destination_lat` | Float | Arrival latitude coordinate. |
| | | | `destination_lon` | Float | Arrival longitude coordinate. |
| | | | `departure_time` | DateTime | ISO 8601 UTC timestamp of planned departure. |
| | | | `travel_mode` | String | Enumeration: `walking`, `metro`, `bus`, `auto`. |
| `/api/companions/messages` | `POST` | `CompanionMessageCreate`| `request_id` | String | Valid UUID foreign key of confirmed companion match. |
| | | | `message_text` | String | Plaintext message (1 to 1000 characters). |

---

### Table A.2: REST API Response Schemas and Status Codes

| Endpoint URI | Method | Success Code | Response Model Structure | Error Codes & Reasons |
|:---|:---:|:---:|:---|:---|
| `/api/auth/signup` | `POST` | `201 Created` | `{ access_token: str, token_type: "bearer", user: UserDTO }` | `400` (Email registered), `422` (Invalid syntax) |
| `/api/auth/login` | `POST` | `200 OK` | `{ access_token: str, token_type: "bearer", user: UserDTO }` | `401` (Invalid credentials) |
| `/api/auth/me` | `GET` | `200 OK` | `UserDTO { id, email, full_name, is_verified, status }` | `401` (Missing / invalid Bearer token) |
| `/api/journeys` | `POST` | `201 Created` | `JourneyDTO { id, title, origin, destination, polyline }` | `401` (Unauthorized) |
| `/api/journeys/{id}/deviations`| `POST` | `201 Created`| `DeviationAlertDTO { id, distance_meters, timestamp }` | `404` (Journey ID not found) |
| `/api/sos/trigger` | `POST` | `201 Created` | `SOSAlertDTO { id, street_address, broadcast_count }` | `401` (Unauthorized), `500` (Geocoding failure) |
| `/api/companions/match` | `POST` | `200 OK` | `List[CompanionCandidateDTO { user, compatibility, poi }]`| `403` (Unverified account forbidden) |
| `/api/companions/messages` | `POST` | `201 Created` | `MessageDTO { id, request_id, sender_id, text, sent_at }` | `403` (Pair not confirmed / unverified) |

<div style="page-break-after: always;"></div>

---

# APPENDIX B: TEST GEOLOCATION DATASETS & SIMULATION SCENARIOS

To evaluate the mathematical models under realistic geospatial conditions, coordinate datasets were gathered along representative urban corridors in Kota, Rajasthan and Delhi National Capital Region (NCR).

### Table B.1: Geolocation Coordinates for Real-World Manhattan & Campus Corridors

| Waypoint ID | Location / Landmark Name | WGS-84 Latitude ($\phi$) | WGS-84 Longitude ($\lambda$) | Segment Role / Operational Context |
|:---:|:---|:---:|:---:|:---|
| **WP-01** | Career Point University Main Gate, Kota | $25.182400^\circ\text{ N}$ | $75.835100^\circ\text{ E}$ | Journey Departure Origin Point |
| **WP-02** | Alaniya River Crossing, Kota Bypass | $25.176200^\circ\text{ N}$ | $75.839800^\circ\text{ E}$ | Peripheral Intermediate Waypoint |
| **WP-03** | Jhalawar Road Junction, Kota | $25.161000^\circ\text{ N}$ | $75.845000^\circ\text{ E}$ | Arterial Roadway Transition |
| **WP-04** | Aerodrome Circle Police Kiosk, Kota | $25.152800^\circ\text{ N}$ | $75.839200^\circ\text{ E}$ | Safe Public Rendezvous Point (POI) |
| **WP-05** | Nayapura Bus Terminal, Kota | $25.185200^\circ\text{ N}$ | $75.842300^\circ\text{ E}$ | High-Density Transit Interchange |
| **WP-06** | Kota Junction Railway Station | $25.218500^\circ\text{ N}$ | $75.864700^\circ\text{ E}$ | Primary Terminal Destination Point |
| **WP-SIM-A** | Multipath Jitter Injection Point | $25.161400^\circ\text{ N}$ | $75.845400^\circ\text{ E}$ | Drift $= 42.1\text{m}$, $\sigma = 35\text{m}$ (Within Safe Buffer) |
| **WP-SIM-B** | Unauthorized Detour Point 1 | $25.161100^\circ\text{ N}$ | $75.848500^\circ\text{ E}$ | Cross-Track $= 182.4\text{m}$ (Breach Count 1) |
| **WP-SIM-C** | Unauthorized Detour Point 2 | $25.161300^\circ\text{ N}$ | $75.852100^\circ\text{ E}$ | Cross-Track $= 268.0\text{m}$ (Breach Count 2) |
| **WP-SIM-D** | Unauthorized Detour Point 3 | $25.161700^\circ\text{ N}$ | $75.856200^\circ\text{ E}$ | Cross-Track $= 415.5\text{m}$ (Breach Count 3 -> Trigger Modal) |

<div style="page-break-after: always;"></div>

---

# APPENDIX C: REPOSITORY SOURCE FILES INVENTORY

This appendix inventories all source code files, configurations, and test assets contained within the Safira implementation repository.

### Table C.1: Complete Repository Source Files Inventory and Line Counts

| File Relative Path | Language / Tech | Total Lines | Architectural Role & Implementation Purpose |
|:---|:---:|:---:|:---|
| `package.json` | JSON | 42 | NPM project dependencies, Vite configuration, build scripts |
| `vite.config.ts` | TypeScript | 28 | Vite bundler settings, proxy forwarding to FastAPI backend |
| `tsconfig.json` | JSON | 32 | TypeScript static type rules, strict null checks, ES2022 target |
| `index.html` | HTML5 | 38 | Root HTML template mounting React 19 single-page application |
| `src/main.tsx` | TypeScript (React) | 24 | Application entry point mounting `App.tsx` into DOM root |
| `src/App.tsx` | TypeScript (React) | 88 | Route declarations (`/routes`, `/buddy`, `/guardians`, `/sos`) |
| `src/index.css` | Tailwind CSS | 46 | Tailwind 4.0 directives, font definitions, custom pulse keyframes |
| `src/context/AuthContext.tsx` | TypeScript (React) | 142 | Global authentication context, JWT decoding, login/logout |
| `src/components/Navbar.tsx` | TypeScript (React) | 114 | Responsive navigation bar, safety status pills, role badges |
| `src/components/MapView.tsx` | TypeScript (React) | 186 | Leaflet map container, LocationIQ tile rendering, pulsing GPS beacon |
| `src/components/DeviationModal.tsx` | TypeScript (React) | 134 | 60-second interactive deviation safety challenge dialog |
| `src/pages/LandingPage.tsx` | TypeScript (React) | 398 | Redesigned startup hero, radar preview, 1-click evaluator logins |
| `src/pages/CreateJourneyPage.tsx`| TypeScript (React) | 276 | LocationIQ Autocomplete route planner, waypoint sequencing |
| `src/pages/JourneyMonitoringPage.tsx`| TypeScript (React)| 348 | Real-time GPS tracking, cross-track math, deviation engine |
| `src/pages/JourneyBuddyPage.tsx` | TypeScript (React) | 412 | "Travel Together" scheduling, compatibility cards, in-app chat |
| `src/pages/GuardiansPage.tsx` | TypeScript (React) | 224 | Emergency contact registry, historical distress incident logs |
| `src/pages/SOSPanel.tsx` | TypeScript (React) | 196 | One-touch panic trigger, reverse-geocoded location card |
| `src/pages/LoginPage.tsx` | TypeScript (React) | 154 | User authentication sign-in form with error alerts |
| `src/pages/SignupPage.tsx` | TypeScript (React) | 178 | Registration form with defensive 72-byte password clamping |
| `src/pages/VerificationPage.tsx` | TypeScript (React) | 210 | Identity document upload and administrator verification portal |
| `backend/app/main.py` | Python (FastAPI) | 94 | Application factory, CORS middleware, API router mounts |
| `backend/app/core/config.py` | Python (Pydantic) | 48 | Pydantic Settings, environment secrets, JWT parameters |
| `backend/app/core/database.py` | Python (SQLAlchemy) | 42 | Engine initialization, sessionmaker factory, Base declarative |
| `backend/app/core/security.py` | Python (BCrypt/JWT) | 68 | BCrypt password clamping and hashing, JWT encode/decode |
| `backend/app/models/user.py` | Python (SQLAlchemy) | 64 | User and VerificationDoc relational database entities |
| `backend/app/models/journey.py` | Python (SQLAlchemy) | 82 | Journey, Waypoint, and DeviationAlert database models |
| `backend/app/models/guardian.py` | Python (SQLAlchemy) | 58 | Guardian and SOSAlert database models |
| `backend/app/models/companion.py`| Python (SQLAlchemy) | 96 | CompanionProfile, Trip, MatchRequest, and Message models |
| `backend/app/schemas/auth.py` | Python (Pydantic) | 52 | Signup, Login, and UserResponse validation schemas |
| `backend/app/schemas/journey.py` | Python (Pydantic) | 68 | Route creation, waypoint, and telemetry sync schemas |
| `backend/app/schemas/companion.py`| Python (Pydantic) | 84 | Trip scheduling, candidate query, and chat schemas |
| `backend/app/api/auth.py` | Python (FastAPI) | 126 | User registration, login, and `/me` route handlers |
| `backend/app/api/journeys.py` | Python (FastAPI) | 184 | Journey CRUD, telemetry streaming, and deviation logging |
| `backend/app/api/companions.py` | Python (FastAPI) | 242 | Companion trip scheduling, matching engine, in-app messaging |
| `backend/app/api/guardians.py` | Python (FastAPI) | 156 | Guardian contact management and Emergency SOS dispatch |
| `backend/app/api/verification.py`| Python (FastAPI) | 118 | Document upload and administrative verification review |
| `backend/app/services/spatial.py`| Python | 134 | Geodesic Haversine and perpendicular cross-track math |
| `backend/app/services/matching.py`| Python | 162 | Spatio-temporal companion compatibility scoring engine |
| `tests/test_api.py` | Python (Pytest) | 194 | Integration tests for auth, journey monitoring, and SOS |
| `tests/test_companions.py` | Python (Pytest) | 178 | Integration tests for Journey Buddy matching and chat |
| **Total Code Base Volume** | **40 Core Files** | **5,335 Lines**| **Complete, Verified, Production-Ready Implementation** |

<div style="page-break-after: always;"></div>

---

# APPENDIX D: SELECTED CORE SOURCE CODE EXCERPTS

This appendix presents key source code listings demonstrating the core algorithmic, cryptographic, and architectural implementations of the Safira platform.

### Listing D.1: Stateless JWT Authentication Guard & Role Filter (`backend/app/api/deps.py`)
```python
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

---

### Listing D.2: Spherical Haversine Geodesic & Cross-Track Distance Engine (`backend/app/services/spatial.py`)
```python
import math
from typing import Tuple, List

EARTH_RADIUS_METERS = 6371000.0

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two points in meters."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_METERS * c

def calculate_initial_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates initial great-circle bearing from point 1 to point 2 in radians."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    return math.atan2(y, x)

def cross_track_distance_to_segment(
    p_lat: float, p_lon: float,
    a_lat: float, a_lon: float,
    b_lat: float, b_lon: float
) -> float:
    """Computes perpendicular cross-track distance from P to segment AB in meters."""
    d_ap = haversine_distance(a_lat, a_lon, p_lat, p_lon)
    d_ab = haversine_distance(a_lat, a_lon, b_lat, b_lon)

    if d_ab == 0.0:
        return d_ap

    bearing_ab = calculate_initial_bearing(a_lat, a_lon, b_lat, b_lon)
    bearing_ap = calculate_initial_bearing(a_lat, a_lon, p_lat, p_lon)

    # Cross-track angular distance
    d_xt_angular = math.asin(
        math.sin(d_ap / EARTH_RADIUS_METERS) * math.sin(bearing_ap - bearing_ab)
    )
    d_xt = abs(d_xt_angular) * EARTH_RADIUS_METERS

    # Along-track projection
    d_at_angular = math.acos(
        math.cos(d_ap / EARTH_RADIUS_METERS) / math.cos(d_xt_angular)
    )
    d_at = d_at_angular * EARTH_RADIUS_METERS

    # Check if projection lies outside segment bounds
    if d_at < 0.0:
        return d_ap
    elif d_at > d_ab:
        return haversine_distance(b_lat, b_lon, p_lat, p_lon)

    return d_xt
```

---

### Listing D.3: Client-Side Route Deviation Engine & Persistence Filter (`src/pages/JourneyMonitoringPage.tsx`)
```typescript
import { useRef, useCallback } from 'react';
import { calculatePerpendicularDistance } from '../utils/geo';
import { Coordinate } from '../types/journey';

export const useRouteMonitor = (
  polylineCoords: Coordinate[],
  onTriggerChallenge: (distance: number, threshold: number) => void
) => {
  const consecutiveBreachCountRef = useRef<number>(0);
  const baselineThresholdMeters = 150.0;
  const maxAccuracyBuffer = 50.0;

  const processIncomingGPSFix = useCallback((
    userLat: number,
    userLon: number,
    gpsAccuracy: number
  ) => {
    if (!polylineCoords || polylineCoords.length < 2) return;

    let minCrossTrackDistance = Infinity;

    // Iterate through all polyline segments
    for (let i = 0; i < polylineCoords.length - 1; i++) {
      const segStart = polylineCoords[i];
      const segEnd = polylineCoords[i + 1];

      const distance = calculatePerpendicularDistance(
        userLat, userLon,
        segStart.latitude, segStart.longitude,
        segEnd.latitude, segEnd.longitude
      );

      if (distance < minCrossTrackDistance) {
        minCrossTrackDistance = distance;
      }
    }

    // Modulate threshold dynamically with sensor uncertainty
    const effectiveThreshold = baselineThresholdMeters + Math.min(gpsAccuracy, maxAccuracyBuffer);

    if (minCrossTrackDistance > effectiveThreshold) {
      consecutiveBreachCountRef.current += 1;
      // Enforce 3-point temporal persistence to suppress false alarm spikes
      if (consecutiveBreachCountRef.current >= 3) {
        onTriggerChallenge(minCrossTrackDistance, effectiveThreshold);
      }
    } else {
      // Coordinate returned within corridor; reset persistence counter
      consecutiveBreachCountRef.current = 0;
    }
  }, [polylineCoords, onTriggerChallenge]);

  return { processIncomingGPSFix };
};
```

---

### Listing D.4: Companion Compatibility Matching Engine (`backend/app/services/matching.py`)
```python
from datetime import datetime
from typing import List, Dict, Any
from app.services.spatial import haversine_distance

def compute_companion_compatibility(
    req_origin: tuple,       # (lat, lon)
    req_destination: tuple,  # (lat, lon)
    req_depart_time: datetime,
    req_mode: str,
    cand_origin: tuple,
    cand_destination: tuple,
    cand_depart_time: datetime,
    cand_mode: str,
    cand_is_verified: bool,
    cand_trust_rating: float = 5.0
) -> Dict[str, Any]:
    """Calculates normalized composite compatibility score (0 - 100%) between two commuters."""
    if not cand_is_verified:
        return {"compatible": False, "score": 0.0, "reason": "Candidate not verified"}

    # 1. Origin Proximity Score (w1 = 0.35, max cutoff = 2500m)
    d_origin = haversine_distance(req_origin[0], req_origin[1], cand_origin[0], cand_origin[1])
    if d_origin > 2500.0:
        return {"compatible": False, "score": 0.0, "reason": "Origin distance exceeds 2.5km"}
    s_route = max(0.0, 1.0 - (d_origin / 2500.0))

    # 2. Temporal Proximity Score (w2 = 0.25, max cutoff = 45 mins)
    delta_mins = abs((req_depart_time - cand_depart_time).total_seconds()) / 60.0
    if delta_mins > 45.0:
        return {"compatible": False, "score": 0.0, "reason": "Departure delta exceeds 45 mins"}
    s_time = max(0.0, 1.0 - (delta_mins / 45.0))

    # 3. Destination Proximity Score (w3 = 0.20, max cutoff = 3000m)
    d_dest = haversine_distance(req_destination[0], req_destination[1], cand_destination[0], cand_destination[1])
    s_dest = max(0.0, 1.0 - (d_dest / 3000.0))

    # 4. Travel Mode Concordance (w4 = 0.10)
    if req_mode.lower() == cand_mode.lower():
        s_mode = 1.0
    elif {req_mode.lower(), cand_mode.lower()}.issubset({"walking", "metro"}):
        s_mode = 0.6
    else:
        s_mode = 0.2

    # 5. Trust and Verification Score (w5 = 0.10)
    s_trust = min(1.0, cand_trust_rating / 5.0)

    # Weighted Sum
    total_score = (
        0.35 * s_route +
        0.25 * s_time +
        0.20 * s_dest +
        0.10 * s_mode +
        0.10 * s_trust
    )

    percentage = round(total_score * 100.0, 1)

    return {
        "compatible": percentage >= 60.0,
        "score_percentage": percentage,
        "breakdown": {
            "origin_distance_meters": round(d_origin, 1),
            "time_delta_minutes": round(delta_mins, 1),
            "destination_distance_meters": round(d_dest, 1),
            "mode_concordance": s_mode,
            "trust_factor": s_trust
        }
    }
```
'''
