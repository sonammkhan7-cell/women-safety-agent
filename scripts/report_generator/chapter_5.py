# -*- coding: utf-8 -*-
"""
Chapter 5: System Architecture and Design for the Master Academic Project Report on Safira.
"""

def get_chapter_5():
    return r"""# CHAPTER 5
# SYSTEM ARCHITECTURE AND DESIGN

## 5.1 Overall Multi-Tier System Architecture

The Safira platform is engineered as a decoupled, multi-tier software system adhering to modular enterprise architectural patterns. The architecture enforces a strict separation of concerns among the client-side presentation layer, the stateless application server layer, the GIS spatial computation subsystem, and the relational persistence tier.

Figure 5.1 illustrates the comprehensive multi-tier architectural topology of the Safira platform.

```mermaid
graph TD
    subgraph ClientTier ["Client Presentation Tier (React 19 + TypeScript)"]
        UI["Landing & Dashboard UI"]
        LeafletMap["Leaflet 1.9 Cartography Engine"]
        GeoWatcher["W3C Geolocation Telemetry Watcher"]
        DevMonitor["Client-Side Route Deviation Monitor"]
        AuthContext["Auth Context & Token Storage"]
    end

    subgraph GatewayTier ["API Routing & Security Gateway (FastAPI)"]
        CORS["CORS Middleware"]
        AuthGuard["JWT Security Filter (Bearer HS256)"]
        RBAC["Role & Verification Guard (is_verified)"]
        Pydantic["Pydantic v2 Request Validation & DTOs"]
    end

    subgraph ServiceTier ["Core Business & Algorithmic Service Layer"]
        JourneyService["Journey Lifecycle Service"]
        DeviationService["Anomaly & Escalation Engine"]
        MatchingEngine["Companion Matching Engine (0-100%)"]
        SOSService["Instant Distress & Reverse Geocoding"]
        SpatialUtils["Haversine & Cross-Track Geodesic Math"]
    end

    subgraph DataTier ["Data Persistence Tier (SQLAlchemy 2.0 ORM)"]
        PostgreSQL[("PostgreSQL 16 + PostGIS Spatial DB")]
        SQLite[("SQLite 3 Canonical Fallback DB")]
    end

    subgraph ExternalTier ["External Geospatial Infrastructure (LocationIQ)"]
        TilesAPI["Raster & Vector Map Tiles API"]
        AutoCompleteAPI["Debounced Autocomplete Geocoding API"]
        DirectionsAPI["Turn-by-Turn Directions & Polyline API"]
        ReverseGeoAPI["Reverse Geocoding Address API"]
    end

    UI --> AuthContext
    GeoWatcher --> DevMonitor
    DevMonitor --> LeafletMap
    LeafletMap <--> TilesAPI

    UI --> CORS
    DevMonitor --> CORS
    CORS --> AuthGuard
    AuthGuard --> RBAC
    RBAC --> Pydantic

    Pydantic --> JourneyService
    Pydantic --> DeviationService
    Pydantic --> MatchingEngine
    Pydantic --> SOSService

    JourneyService --> SpatialUtils
    DeviationService --> SpatialUtils
    MatchingEngine --> SpatialUtils

    JourneyService <--> DirectionsAPI
    UI <--> AutoCompleteAPI
    SOSService <--> ReverseGeoAPI

    JourneyService --> PostgreSQL
    DeviationService --> PostgreSQL
    MatchingEngine --> PostgreSQL
    SOSService --> PostgreSQL
    PostgreSQL -. Fallback .-> SQLite
```

*Figure 5.1: Multi-Tier System Architecture of the Safira Platform*

### Architectural Tier Descriptions:
1. **Client Presentation Tier:** Implemented as a responsive React 19 single-page application. Executes client-side geolocation polling, renders interactive cartography via Leaflet 1.9, computes real-time cross-track distance math, and provides visual distress workflows.
2. **API Routing & Security Gateway:** Governed by FastAPI middleware. Intercepts all incoming HTTP traffic, enforces Cross-Origin Resource Sharing (CORS) policies, validates JWT cryptographic signatures, extracts user credentials, and rejects unauthenticated or unverified requests.
3. **Core Business & Algorithmic Service Layer:** Houses pure Python domain logic, including the Haversine geodesic calculation engine, the 3-point temporal persistence filter, the multi-factor companion compatibility scoring algorithm, and the emergency notification dispatcher.
4. **Data Persistence Tier:** Abstracted via SQLAlchemy 2.0 ORM. Maps relational entities across tables and manages transactional consistency across PostgreSQL (with PostGIS extensions) and SQLite.
5. **External Geospatial Infrastructure:** The LocationIQ platform provides external cartographic tiles, autocomplete geocoding, turn-by-turn routing, and reverse geocoding services.

---

## 5.2 End-to-End User Application Workflow

The operational lifecycle of a user within the Safira platform progresses through structured, verifiable states: identity onboarding, administrative verification, route planning, active monitoring, potential anomaly mitigation, and collaborative companion coordination.

Figure 5.2 models the complete end-to-end user state machine and application journey.

```mermaid
stateDiagram-v2
    [*] --> Unregistered

    Unregistered --> Registered : User Signup & Password Clamping
    Registered --> LoggedIn : JWT Token Issuance (Pending Verification)

    state LoggedIn {
        [*] --> VerificationPending
        VerificationPending --> VerificationApproved : Admin ID Document Review
        VerificationPending --> VerificationRejected : Invalid Document / Male Identity
        VerificationRejected --> VerificationPending : Resubmit Valid Document
        
        state VerificationApproved {
            [*] --> UserDashboard
            
            state UserDashboard {
                [*] --> Idle
                Idle --> PlanningJourney : Enter Origin & Destination
                PlanningJourney --> LocationIQRoute : Autocomplete & Route Polyline
                LocationIQRoute --> ActiveJourney : Start Journey & Geolocation Watch
                
                state ActiveJourney {
                    [*] --> CorridorMonitoring
                    CorridorMonitoring --> CorridorMonitoring : dist <= 150m + sigma (Normal)
                    CorridorMonitoring --> TemporalBreachCounter : dist > 150m + sigma
                    TemporalBreachCounter --> CorridorMonitoring : Return to Corridor (< 3 ticks)
                    TemporalBreachCounter --> SafetyModalTriggered : 3 Consecutive Off-Route Ticks
                    
                    state SafetyModalTriggered {
                        [*] --> Countdown60s
                        Countdown60s --> CorridorMonitoring : User taps "I Am Safe"
                        Countdown60s --> SOSAlertActive : 60s Timeout (No Response)
                    }
                    
                    CorridorMonitoring --> SOSAlertActive : Manual One-Touch SOS Panic
                }

                ActiveJourney --> JourneyCompleted : User taps "End Journey"
                JourneyCompleted --> Idle

                Idle --> JourneyBuddyHub : Verified User Access
                state JourneyBuddyHub {
                    [*] --> BrowseTrips
                    BrowseTrips --> PostNewTrip : Schedule Upcoming Commute
                    BrowseTrips --> FilterCandidates : Spatio-Temporal Query
                    FilterCandidates --> SendRequest : Request Companion (Compatibility Score)
                    SendRequest --> CompanionAccepted : Peer Accepts Connection
                    CompanionAccepted --> EncryptedChat : Secure Rendezvous Coordination
                    CompanionAccepted --> MeetAtSafePOI : Public Checkpoint Meeting
                }
            }
        }
    }

    state SOSAlertActive {
        [*] --> CaptureInstantGPS
        CaptureInstantGPS --> ReverseGeocodeAddress
        ReverseGeocodeAddress --> BroadcastGuardians
        BroadcastGuardians --> GuardianLiveTracking
    }
```

*Figure 5.2: End-to-End User Application Journey Lifecycle Flowchart*

---

## 5.3 Unified Modeling Language (UML) Use Case View

The Safira system accommodates four distinct human and external system actors:
1. **Verified Female Traveler:** The primary end-user who plans journeys, monitors real-time routes, responds to deviation check-ins, accesses the Journey Buddy network, and triggers SOS alerts.
2. **Unverified / Onboarding User:** A newly registered user with restricted permissions who can explore public features, submit identity documents, and configure trusted guardians, but is locked out of companion matching.
3. **Platform Administrator:** Responsible for reviewing submitted identity credentials, confirming eligibility, and transitioning verification states.
4. **Emergency Contact / Guardian:** Receives automated distress alerts, views reverse-geocoded incident locations, and tracks emergency telemetry.
5. **LocationIQ Geospatial Services:** External API system providing map tiles, geocoding, directions, and reverse-address resolution.

Figure 5.3 models the UML Use Case relationships across these actors.

```mermaid
flowchart LR
    subgraph Actors
        U["Verified Female Traveler"]
        UV["Unverified User"]
        ADM["System Administrator"]
        G["Trusted Guardian"]
        LIQ["LocationIQ API Engine"]
    end

    subgraph UseCases ["Safira Platform Use Cases"]
        UC01["UC-01: Register & Authenticate"]
        UC02["UC-02: Submit Verification Documents"]
        UC03["UC-03: Review & Approve Verification"]
        UC04["UC-04: Manage Emergency Guardians"]
        UC05["UC-05: Autocomplete Address & Plan Route"]
        UC06["UC-06: Monitor Active Trajectory Corridor"]
        UC07["UC-07: Handle Route Deviation Challenge"]
        UC08["UC-08: Trigger Instant SOS Distress"]
        UC09["UC-09: Receive Guardian Emergency Broadcast"]
        UC10["UC-10: Schedule Journey Buddy Trip"]
        UC11["UC-11: Match Compatible Travel Companions"]
        UC12["UC-12: In-App Coordination Chat"]
        UC13["UC-13: Fetch Map Tiles & Polyline Directions"]
    end

    UV --> UC01
    UV --> UC02
    UV --> UC04

    ADM --> UC03

    U --> UC01
    U --> UC04
    U --> UC05
    U --> UC06
    U --> UC07
    U --> UC08
    U --> UC10
    U --> UC11
    U --> UC12

    G --> UC09

    UC05 <--> LIQ
    UC08 <--> LIQ
    UC13 <--> LIQ
```

*Figure 5.3: Comprehensive UML Use Case Diagram for User, Companion, and Guardian Actors*

---

## 5.4 Frontend Component Architecture & State Management

The frontend is structured hierarchically to maintain clean separation between global authentication state, active journey telemetry, interactive map rendering, and collaborative companion networking.

```
App.tsx (Root Container)
 │
 ├── AuthProvider (JWT Context, User State, Verification Flag, LocalStorage)
 │    │
 │    ├── Layout.tsx (Responsive Navigation, Safety Header, Status Pill)
 │    │    │
 │    │    ├── LandingPage.tsx (Startup Hero, Radar Preview, Evaluator Logins)
 │    │    ├── LoginPage.tsx / SignupPage.tsx (Auth Forms, Clamped BCrypt Input)
 │    │    │
 │    │    ├── CreateJourneyPage.tsx (LocationIQ Autocomplete, Waypoint Selection)
 │    │    ├── JourneyMonitoringPage.tsx (Active Monitoring Container)
 │    │    │    │
 │    │    │    ├── MapView.tsx (Leaflet Map, LocationIQ Tiles, Pulsing Beacon)
 │    │    │    ├── TelemetryBar.tsx (Speed, Accuracy, Distance Remaining)
 │    │    │    └── DeviationModal.tsx (60s Safety Countdown Dialog)
 │    │    │
 │    │    ├── SOSPanel.tsx (One-Touch Distress Button, Reverse Geocode Card)
 │    │    ├── GuardiansPage.tsx (CRUD Contacts, Alert History Log)
 │    │    ├── VerificationPage.tsx (Document Upload, Admin Review View)
 │    │    │
 │    │    └── JourneyBuddyPage.tsx (Travel Together Module)
 │    │         ├── TripScheduler.tsx (Publish Commute Itinerary)
 │    │         ├── CandidateFinder.tsx (Compatibility Filtering & Cards)
 │    │         ├── SafeMeetingPointPicker.tsx (LocationIQ Public POI Locator)
 │    │         └── CompanionChatModal.tsx (Encrypted In-App Chat Dialog)
```

### Custom React Hooks:
- `useGeolocation`: Abstracts the browser’s `navigator.geolocation.watchPosition` API. Manages high-accuracy GPS sampling, error handling (permission denied, timeout, position unavailable), and delivers instantaneous coordinate, speed, heading, and accuracy metrics.
- `useJourneyMonitor`: Implements the client-side cross-track geodesic math. Ingests the current GPS fix, calculates perpendicular distance against every segment of the active route polyline, tracks consecutive breaches, and controls the trigger state for the 60-second deviation modal.

---

## 5.5 Backend Modular Architecture & Service Layer

The FastAPI backend is organized into clear architectural packages:

```
backend/
 ├── app/
 │    ├── main.py                 # Application factory, CORS, exception handlers, router mounts
 │    ├── core/
 │    │    ├── config.py          # Pydantic Settings, environment variables, JWT secrets
 │    │    ├── database.py        # SQLAlchemy engine, sessionmaker, declarative Base
 │    │    └── security.py        # BCrypt hashing, JWT encoding/decoding, token validation
 │    ├── models/
 │    │    ├── user.py            # User and VerificationDoc SQLAlchemy entities
 │    │    ├── journey.py         # Journey, Waypoint, and DeviationAlert entities
 │    │    ├── guardian.py        # Guardian and SOSAlert entities
 │    │    └── companion.py       # CompanionProfile, CompanionTrip, Request, Message entities
 │    ├── schemas/
 │    │    ├── auth.py            # Signup, Login, Token, and UserResponse DTOs
 │    │    ├── journey.py         # JourneyCreate, WaypointCreate, TelemetrySync DTOs
 │    │    ├── guardian.py        # GuardianCreate, SOSAlertCreate DTOs
 │    │    └── companion.py       # TripCreate, CompanionMatchQuery, MessageCreate DTOs
 │    ├── api/
 │    │    ├── auth.py            # /api/auth endpoints (signup, login, me)
 │    │    ├── journeys.py        # /api/journeys endpoints (CRUD, deviations, telemetry)
 │    │    ├── guardians.py       # /api/guardians & /api/sos endpoints
 │    │    ├── companions.py      # /api/companions endpoints (trips, match, chat)
 │    │    └── verification.py   # /api/verification endpoints (upload, review)
 │    └── services/
 │         ├── spatial.py         # Haversine formula, cross-track distance calculations
 │         ├── matching.py        # Spatio-temporal companion compatibility scoring
 │         └── notifier.py        # Guardian notification dispatch simulation
 ├── tests/
 │    ├── test_api.py             # Integration test suite for Auth, Journeys, and SOS
 │    └── test_companions.py      # Integration test suite for Journey Buddy matching & chat
 └── requirements.txt             # Python runtime dependencies
```

---

## 5.6 Database Schema Design & Entity-Relationship Model

The persistence layer models ten interrelated entities capturing the complete domain graph of the platform.

Figure 5.4 documents the Entity-Relationship (ER) model of the Safira platform.

```mermaid
erDiagram
    USERS ||--o{ VERIFICATION_DOCS : submits
    USERS ||--o{ JOURNEYS : owns
    USERS ||--o{ GUARDIANS : configures
    USERS ||--o{ SOS_ALERTS : triggers
    USERS ||--o| COMPANION_PROFILES : maintains
    USERS ||--o{ COMPANION_TRIPS : posts
    USERS ||--o{ COMPANION_REQUESTS : initiates
    USERS ||--o{ COMPANION_MESSAGES : sends

    JOURNEYS ||--o{ WAYPOINTS : contains
    JOURNEYS ||--o{ DEVIATION_ALERTS : incurs

    COMPANION_TRIPS ||--o{ COMPANION_REQUESTS : receives
    COMPANION_REQUESTS ||--o{ COMPANION_MESSAGES : context_for

    USERS {
        string id PK
        string email UK
        string hashed_password
        string full_name
        string phone_number
        string verification_status
        boolean is_verified
        datetime created_at
    }

    VERIFICATION_DOCS {
        string id PK
        string user_id FK
        string document_type
        string document_number_hash
        string document_url
        string status
        datetime reviewed_at
    }

    JOURNEYS {
        string id PK
        string user_id FK
        string title
        string origin_name
        float origin_lat
        float origin_lon
        string destination_name
        float destination_lat
        float destination_lon
        text route_polyline
        string status
        datetime created_at
    }

    WAYPOINTS {
        string id PK
        string journey_id FK
        string name
        float lat
        float lon
        int order_index
        boolean is_passed
    }

    DEVIATION_ALERTS {
        string id PK
        string journey_id FK
        float user_lat
        float user_lon
        float distance_meters
        float threshold_meters
        string resolution_status
        datetime created_at
    }

    GUARDIANS {
        string id PK
        string user_id FK
        string name
        string phone_number
        string email
        string relationship
        boolean notify_on_deviation
        boolean notify_on_sos
    }

    SOS_ALERTS {
        string id PK
        string user_id FK
        float lat
        float lon
        string street_address
        string trigger_mode
        boolean resolved
        datetime triggered_at
    }

    COMPANION_PROFILES {
        string id PK
        string user_id FK
        string preferred_name
        string bio
        string commute_frequency
        float trust_score
    }

    COMPANION_TRIPS {
        string id PK
        string user_id FK
        string origin_name
        float origin_lat
        float origin_lon
        string destination_name
        float destination_lat
        float destination_lon
        datetime departure_time
        string travel_mode
        string status
    }

    COMPANION_REQUESTS {
        string id PK
        string sender_id FK
        string receiver_id FK
        string trip_id FK
        float compatibility_score
        string status
        datetime created_at
    }

    COMPANION_MESSAGES {
        string id PK
        string request_id FK
        string sender_id FK
        text message_text
        datetime sent_at
    }
```

*Figure 5.4: Detailed Entity-Relationship (ER) Diagram of the Relational Database Models*

---

## 5.7 Stateless Authentication & Token Lifecycle Architecture

Authentication in Safira enforces strict statelessness to support horizontal scalability.

Figure 5.5 diagrams the authentication lifecycle from initial registration through token validation.

```mermaid
sequenceDiagram
    autonumber
    actor User as Female Commuter
    participant Frontend as React 19 Client
    participant API as FastAPI Auth Router
    participant Security as BCrypt & JWT Service
    participant DB as Relational Database

    Note over User,Frontend: Registration Flow
    User->>Frontend: Enters Email, Full Name, Password
    Frontend->>Frontend: Client-side validation & password clamping (<=72 bytes)
    Frontend->>API: POST /api/auth/signup (Email, Name, Clamped Password)
    API->>DB: Check if Email already exists
    alt Email already registered
        DB-->>API: User record found
        API-->>Frontend: 400 Bad Request ("Email already registered")
        Frontend-->>User: Display meaningful signup error
    else Email is unique
        API->>Security: Hash password (BCrypt work_factor=12)
        Security-->>API: Generated Salt & Hash
        API->>DB: INSERT into users (id, email, hash, is_verified=False)
        DB-->>API: User record persisted
        API->>Security: Generate JWT token (sub=user_id, is_verified=False)
        Security-->>API: Encoded Bearer Token
        API-->>Frontend: 201 Created { access_token, token_type: "bearer", user }
        Frontend->>Frontend: Store token in LocalStorage & set AuthContext
        Frontend-->>User: Navigate to Onboarding / Journey Hub
    end

    Note over User,Frontend: Protected Request Flow
    User->>Frontend: Accesses Journey Buddy Matching
    Frontend->>API: GET /api/companions/match (Header: Bearer <token>)
    API->>Security: Validate JWT signature (HS256) & check expiration
    alt Token invalid or expired
        Security-->>API: Verification Exception
        API-->>Frontend: 401 Unauthorized
        Frontend->>Frontend: Clear token & redirect to /login
    else Token signature valid
        Security-->>API: Extracted Claims (user_id, is_verified)
        API->>API: Evaluate RBAC (is_verified == True)
        alt User not verified
            API-->>Frontend: 403 Forbidden ("Verification Required")
            Frontend-->>User: Prompt to submit ID verification
        else User is verified
            API->>DB: Query compatible female trips
            DB-->>API: Trip candidate list
            API-->>Frontend: 200 OK [ Matching Candidates with Compatibility Scores ]
            Frontend-->>User: Render Journey Buddy Cards
        end
    end
```

*Figure 5.5: Stateless JWT Bearer Authentication & Token Refresh Flowchart*

---

## 5.8 Geospatial Route Deviation Monitoring Pipeline

The continuous route corridor monitoring pipeline operates as an autonomous state machine running within the user's browser runtime.

Figure 5.6 details the algorithmic state transitions of the deviation detection engine.

```mermaid
stateDiagram-v2
    [*] --> Standby : Journey Activated

    state Standby {
        [*] --> PollingGPS
        PollingGPS --> IngestFix : navigator.geolocation tick (every 5-10s)
        IngestFix --> EvaluateAccuracy : Read latitude, longitude, accuracy (sigma)
        
        state EvaluateAccuracy {
            [*] --> ComputeCrossTrack : sigma <= 50m
            [*] --> BufferExpand : sigma > 50m (Urban canyoning)
            BufferExpand --> ComputeCrossTrack : delta_eff = 150m + sigma
        }

        ComputeCrossTrack --> CompareThreshold : Find min cross-track dist to all route segments
        
        state CompareThreshold {
            [*] --> WithinCorridor : dist <= delta_eff
            [*] --> BreachDetected : dist > delta_eff
        }

        WithinCorridor --> ResetPersistence : breach_counter = 0
        ResetPersistence --> PollingGPS : Next tick

        BreachDetected --> IncrementPersistence : breach_counter += 1
        IncrementPersistence --> PollingGPS : breach_counter < 3 (Transient Jitter)
        IncrementPersistence --> ActiveDeviationState : breach_counter == 3 (Persistent Anomaly)
    }

    state ActiveDeviationState {
        [*] --> PlayAuditoryChime
        PlayAuditoryChime --> RenderModal : Display 60-Second Challenge Modal
        
        state RenderModal {
            [*] --> CountdownActive
            CountdownActive --> UserSafe : User taps "I Am Safe"
            CountdownActive --> UserReroute : User taps "Update Route"
            CountdownActive --> TimeoutTriggered : Timer reaches 00:00 (No Response)
        }

        UserSafe --> Standby : Reset breach_counter = 0, resume monitoring
        UserReroute --> RecalculateRoute : Fetch new polyline from current coordinate
        RecalculateRoute --> Standby : Resume monitoring along new corridor
        TimeoutTriggered --> EmergencyEscalation : System autonomously triggers SOS
    }

    state EmergencyEscalation {
        [*] --> PostDeviationToBackend : POST /api/journeys/{id}/deviations
        PostDeviationToBackend --> PostSOSToBackend : POST /api/sos/trigger (mode='auto_deviation')
        PostSOSToBackend --> ReverseGeocode : Fetch street address from LocationIQ
        ReverseGeocode --> AlertGuardians : Dispatch SMS/Email alert to trusted contacts
        AlertGuardians --> LiveTrackingPortal : Publish emergency tracking URL
    }
```

*Figure 5.6: Geospatial Route Deviation Detection and Escalation State Machine*

---

## 5.9 Companion Matching Engine Execution Pipeline

The Journey Buddy matching engine executes a deterministic, multi-factor filtering and scoring pipeline.

Figure 5.7 illustrates the mathematical execution sequence of the companion matching service.

```mermaid
flowchart TD
    Start["User Creates Trip Request (Origin, Dest, Depart Time, Mode)"] --> Step1["Step 1: Database Spatio-Temporal Query Filter"]
    
    subgraph Stage1 ["Stage 1: Coarse Database Filtering"]
        Step1 --> QueryTrips["Filter Trips WHERE status = 'scheduled' AND user_id != current_user"]
        QueryTrips --> TimeWindow["Filter ABS(trip.departure_time - request.time) <= 45 Minutes"]
        TimeWindow --> VerificationCheck["Filter ONLY trips where user.is_verified = True"]
    end

    Stage1 --> Step2["Step 2: Geodesic Spatial Proximity Filter"]

    subgraph Stage2 ["Stage 2: Geodesic Endpoint Bounds"]
        Step2 --> OrigDist["Calculate Haversine Distance: d_origin = dist(Req.Origin, Trip.Origin)"]
        OrigDist --> DestDist["Calculate Haversine Distance: d_dest = dist(Req.Dest, Trip.Dest)"]
        DestDist --> BoundCheck{"d_origin <= 2500m AND d_dest <= 3000m?"}
        BoundCheck -- No --> RejectCandidate["Drop Candidate (Incompatible Path)"]
        BoundCheck -- Yes --> AcceptForScoring["Pass to Multi-Factor Scoring Engine"]
    end

    Stage2 --> Step3["Step 3: Multi-Factor Compatibility Scoring Engine"]

    subgraph Stage3 ["Stage 3: Composite Scoring (0 - 100%)"]
        AcceptForScoring --> CalcRouteScore["Compute Route Proximity Score (w1 = 0.35)"]
        CalcRouteScore --> CalcTimeScore["Compute Temporal Proximity Score (w2 = 0.25)"]
        CalcTimeScore --> CalcDestScore["Compute Destination Proximity Score (w3 = 0.20)"]
        CalcDestScore --> CalcModeScore["Compute Travel Mode Concordance (w4 = 0.10)"]
        CalcModeScore --> CalcTrustScore["Compute Verification & Rating Score (w5 = 0.10)"]
        CalcTrustScore --> SumScore["Total Compatibility C = SUM(wi * Si) * 100%"]
    end

    Stage3 --> Step4["Step 4: Safe Public Rendezvous Point Attachment"]

    subgraph Stage4 ["Stage 4: Safe Checkpoint Recommendation"]
        SumScore --> QueryPOIs["Query LocationIQ POIs near Midpoint (Metro, Lit Cafes, Police)"]
        QueryPOIs --> AttachPOI["Attach Nearest Safe Public Meeting Checkpoint"]
    end

    Stage4 --> Output["Return Ranked Compatibility Cards to Client"]
```

*Figure 5.7: Companion Matching Pipeline and Composite Compatibility Evaluation*

---

## 5.10 REST API Communication Flow & Request Sequences

Table 5.1 inventories all 24 RESTful endpoints provided by the Safira backend application.

### Table 5.1: Complete REST API Endpoints Inventory Across All Modules

| HTTP Verb | Endpoint URI Path | Auth Required | Target Module | Functional Description |
|:---:|:---|:---:|:---:|:---|
| `POST` | `/api/auth/signup` | No | Auth | Register new female commuter with clamped password hashing |
| `POST` | `/api/auth/login` | No | Auth | Authenticate user and issue 24-hour stateless JWT token |
| `GET` | `/api/auth/me` | Bearer JWT | Auth | Fetch current user profile, roles, and verification status |
| `POST` | `/api/verification/upload` | Bearer JWT | Verification | Submit identity document record for female verification |
| `GET` | `/api/verification/status` | Bearer JWT | Verification | Fetch current verification status (`Pending`/`Verified`/`Rejected`) |
| `POST` | `/api/verification/review` | Admin JWT | Verification | Admin endpoint to approve or reject submitted verification |
| `POST` | `/api/journeys` | Bearer JWT | Journeys | Create a new planned journey with origin and destination |
| `GET` | `/api/journeys` | Bearer JWT | Journeys | List all active and historical journeys for current user |
| `GET` | `/api/journeys/{id}` | Bearer JWT | Journeys | Fetch specific journey details including route polyline |
| `PUT` | `/api/journeys/{id}/status` | Bearer JWT | Journeys | Update journey status (`active`, `completed`, `cancelled`) |
| `POST` | `/api/journeys/{id}/telemetry`| Bearer JWT | Journeys | Sync real-time GPS coordinate fix, speed, and accuracy |
| `POST` | `/api/journeys/{id}/deviations`| Bearer JWT | Journeys | Log an off-route deviation anomaly and triggering metrics |
| `POST` | `/api/journeys/{id}/resolve`| Bearer JWT | Journeys | Resolve deviation anomaly (safe confirmation or reroute) |
| `POST` | `/api/guardians` | Bearer JWT | Guardians | Register a new trusted emergency contact |
| `GET` | `/api/guardians` | Bearer JWT | Guardians | List all configured emergency guardians for current user |
| `DELETE`| `/api/guardians/{id}` | Bearer JWT | Guardians | Delete an emergency guardian from profile |
| `POST` | `/api/sos/trigger` | Bearer JWT | Emergency SOS | Trigger instant SOS panic alert with current coordinates |
| `GET` | `/api/sos/history` | Bearer JWT | Emergency SOS | Retrieve historical distress alerts and dispatch logs |
| `POST` | `/api/companions/trips` | Verified JWT | Journey Buddy | Schedule a future commute trip for companion matching |
| `GET` | `/api/companions/trips` | Verified JWT | Journey Buddy | List active trips scheduled by current user |
| `POST` | `/api/companions/match` | Verified JWT | Journey Buddy | Query matching female candidates based on spatio-temporal route |
| `POST` | `/api/companions/request` | Verified JWT | Journey Buddy | Send travel companion connection request to matched peer |
| `PUT` | `/api/companions/request/{id}`| Verified JWT | Journey Buddy | Accept or decline incoming companion connection request |
| `POST` | `/api/companions/messages` | Verified JWT | Journey Buddy | Send encrypted in-app message within confirmed companion pair |

Figure 5.8 models the critical REST sequence during an emergency SOS event.

```mermaid
sequenceDiagram
    autonumber
    actor User as Female Commuter
    participant UI as SOS Panel / Auto Timeout
    participant API as FastAPI Emergency Router
    participant LIQ as LocationIQ Reverse Geocoder
    participant DB as Relational Database
    actor Guardian as Registered Guardian

    User->>UI: Taps Instant Red SOS Button
    UI->>UI: Read instantaneous GPS fix from navigator.geolocation
    UI->>API: POST /api/sos/trigger { lat, lon, mode: "manual_panic" }
    
    activate API
    API->>LIQ: GET /v1/reverse.php?lat={lat}&lon={lon}&format=json
    LIQ-->>API: 200 OK { display_name: "Station Rd, Nayapura, Kota, 324001" }
    
    API->>DB: INSERT into sos_alerts (user_id, lat, lon, address, trigger_mode)
    DB-->>API: Alert record saved (alert_id: UUID)
    
    API->>DB: SELECT * FROM guardians WHERE user_id = current_user
    DB-->>API: Guardian list [ { name, phone, email } ]
    
    API->>API: Dispatch simulated SMS & Email notifications with live tracking URL
    API-->>UI: 201 Created { alert_id, status: "broadcast_dispatched", address }
    deactivate API

    UI-->>User: High-visibility confirmation screen & siren animation
    API-)Guardian: Emergency Alert Dispatched: "EMERGENCY: User at Station Rd, Kota. Track: https://safira.org/track/{alert_id}"
```

*Figure 5.8: Sequence Diagram for Emergency SOS Trigger and Guardian Dispatch*

<div style="page-break-after: always;"></div>
"""
