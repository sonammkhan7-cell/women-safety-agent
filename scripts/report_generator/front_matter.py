# -*- coding: utf-8 -*-
"""
Front matter for the Master Academic Project Report on Safira (Women Safety Guardian).
Includes Cover Page, Certificate, Acknowledgement, Abstract, Table of Contents,
List of Figures, List of Tables, and List of Abbreviations.
"""

def get_front_matter():
    return r"""# A PROJECT REPORT
## ON
# **WOMEN'S TRAVEL SAFETY GUARDIAN & COMPANION MATCHING PLATFORM (SAFIRA)**

### *A Web-Based Intelligent Geospatial Route Monitoring, Automated Anomaly Detection, and Privacy-Preserving Travel Companion Matching System*

---

**Submitted in partial fulfillment of the requirements for the award of the Degree of**  
### **BACHELOR OF TECHNOLOGY**  
**in**  
### **DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING**

<br/>

**Under the Academic Supervision of:**  
**Assistant Professor (CSE)**  
Department of Computer Science and Engineering  
Career Point University, Kota  

<br/>

**Submitted by:**  
**Sonam Khanam**  
Roll No. / Enrollment ID: K25988 / B.Tech CSE  

<br/>

### **DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING**  
### **CAREER POINT UNIVERSITY, KOTA - 325003, RAJASTHAN (INDIA)**  
**Academic Session: July – December 2026**

<div style="page-break-after: always;"></div>

---

# CERTIFICATE OF ORIGINALITY

This is to certify that the project entitled **“WOMEN’S TRAVEL SAFETY GUARDIAN & COMPANION MATCHING PLATFORM (SAFIRA)”**, submitted by **Sonam Khanam** (Enrollment ID: K25988) in partial fulfillment of the requirements for the award of the degree of **Bachelor of Technology in Computer Science & Engineering** to the **Department of Computer Science & Engineering, Career Point University, Kota (Rajasthan)**, is an authentic record of bonafide project work carried out under my academic supervision and guidance.

To the best of my knowledge, the matter embodied in this project report has not been submitted to any other University or Institute for the award of any degree, diploma, or fellowship. The software implementations, algorithms, user interfaces, database designs, and empirical test cases presented in this document represent the original intellectual work of the candidate, except where due academic citations and references have been explicitly provided.

<br/><br/>

**Date:** 19 November 2026  
**Place:** Kota, Rajasthan  

<br/><br/>
_____________________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; _____________________________  
**Candidate's Signature** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Supervisor's Signature**  
**Sonam Khanam** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Assistant Professor (CSE)**  
Department of CSE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Department of CSE  
Career Point University, Kota &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Career Point University, Kota  

<br/><br/>
_____________________________  
**Head of Department**  
Department of Computer Science & Engineering  
Career Point University, Kota  

<div style="page-break-after: always;"></div>

---

# ACKNOWLEDGEMENT

I wish to express my profound gratitude and deep indebtedness to my project supervisor, **Assistant Professor**, Department of Computer Science & Engineering, Career Point University, Kota, for their invaluable guidance, constant encouragement, critical insights, and technical advice throughout the conception, architecture design, implementation, and documentation of this project. Their constructive criticism and high standards for software architecture were vital to the success of this endeavor.

I am immensely grateful to the **Head of Department**, Department of Computer Science and Engineering, for providing the necessary infrastructural facilities, high-performance computing resources, and academic environment essential for completing this engineering project.

My sincere thanks are also extended to the respected faculty members, technical lab assistants, and staff of the Department of Computer Science and Engineering for their direct and indirect cooperation during the execution of this work.

Special gratitude is due to my family and fellow batchmates for their constant moral encouragement, constructive discussions during peer reviews, and invaluable assistance during the empirical user testing and simulation phases of the platform.

<br/><br/>
**Sonam Khanam**  
B.Tech, Computer Science & Engineering  
Career Point University, Kota  

<div style="page-break-after: always;"></div>

---

# ABSTRACT

Women's personal safety during daily transit, urban commuting, and evening travel remains one of the most critical societal, engineering, and civic challenges globally. Conventional personal safety applications rely predominantly on reactive, manual panic buttons that fail when a user is incapacitated, panicked, or unable to reach their mobile device. Furthermore, existing mobility platforms fail to provide verified, female-exclusive collaborative transit options, leaving individuals to travel isolated along vulnerable routes.

This project presents **Safira (Women Safety Guardian)**, a full-stack, web-based, privacy-engineered travel safety and companion matching platform developed using modern software engineering paradigms. Safira is designed exclusively for verified women, integrating continuous, client-side geospatial route deviation monitoring with deterministic, privacy-preserving travel companion matching.

The architecture comprises a reactive **React 19, TypeScript, and Tailwind CSS** frontend integrated with **Leaflet 1.9** cartography and the **LocationIQ Maps API**, communicating with a high-throughput **FastAPI (Python 3.14)** REST backend backed by **SQLAlchemy 2.0 ORM** and **PostgreSQL/PostGIS** (with SQLite canonical fallback). The system incorporates four primary technical innovations:
1. **Intelligent Geodesic Corridor Monitoring**: Implements a continuous cross-track distance algorithm using the Haversine trigonometric formulation that checks user coordinates against a multi-segment planned route polyline. To eliminate false positives induced by urban satellite multipath and GPS jitter, the system dynamically factors GPS horizontal accuracy ($\pm \sigma$) into a 150-meter tolerance threshold and enforces a 3-point temporal persistence filter before initiating automated safety check-ins and escalating 60-second emergency contact dispatch.
2. **Deterministic Travel Companion Matching ("Journey Buddy")**: A mathematical matching engine that evaluates route overlap percentage, departure time delta ($\le 45\text{ mins}$), destination proximity ($\le 2500\text{ m}$), and travel mode to compute a composite compatibility score ($0-100\%$). The system automatically identifies safe, well-lit public transit hubs and 24/7 cafes as meeting points.
3. **Zero-Knowledge Privacy Architecture**: Prospective matches are shown only coarse, sanitized route corridors and masked initial names. Exact live coordinates and private phone numbers are never exposed publicly without explicit mutual acceptance.
4. **Instant Emergency SOS & Guardian Dispatch**: An immediate-action distress protocol that captures real-time coordinates, performs reverse geocoding via LocationIQ, and broadcasts multi-channel alerts to designated family guardians with an interactive live tracking map.

Empirical verification through automated unit testing, end-to-end integration suites, LocationIQ API routing benchmarks, and simulated route deviation runs demonstrates zero false escalations under normal GPS drift and sub-second emergency dispatch latency. The platform offers a deployable, practical, and privacy-respecting engineering solution to enhance women's transit security.

**Keywords:** Women Safety Guardian, Geospatial Route Monitoring, LocationIQ Maps, Leaflet GIS, Haversine Distance, Route Deviation Anomaly Detection, Travel Companion Matching, Privacy-Preserving Architecture, FastAPI, React.js.

<div style="page-break-after: always;"></div>

---

# TABLE OF CONTENTS

| Chapter / Section | Title | Page No. |
|:---|:---|:---:|
| | **Certificate of Originality** | **i** |
| | **Acknowledgement** | **ii** |
| | **Abstract** | **iii** |
| | **Table of Contents** | **iv** |
| | **List of Figures** | **vi** |
| | **List of Tables** | **vii** |
| | **List of Abbreviations** | **viii** |
| **Chapter 1** | **Introduction** | **1** |
| 1.1 | Background of Women's Travel Safety & Urban Mobility Challenges | 1 |
| 1.2 | Importance of Real-Time Geospatial Corridor Monitoring | 2 |
| 1.3 | Critical Challenges Faced by Women Commuters | 3 |
| 1.4 | Role of Location Intelligence & Verified Companion Networks | 4 |
| 1.5 | Introduction to Safira (Women Safety Guardian) | 5 |
| 1.6 | Objectives of the Project | 6 |
| 1.7 | Scope of the Project | 7 |
| 1.8 | Research & Engineering Design Questions | 8 |
| **Chapter 2** | **Literature Review** | **9** |
| 2.1 | Evolution of Women's Safety Technology: Hardware vs. Software | 9 |
| 2.2 | Geospatial Route Monitoring and Anomaly Detection in GIS | 10 |
| 2.3 | Travel Companion Matching & Collaborative Transit Systems | 11 |
| 2.4 | Privacy-Preserving Location Sharing and Zero-Knowledge Principles | 12 |
| 2.5 | Comparative Literature Summary | 13 |
| 2.6 | Identified Research & Engineering Gaps | 15 |
| **Chapter 3** | **Problem Definition and Proposed System** | **16** |
| 3.1 | Existing Problem Statement | 16 |
| 3.2 | Limitations of Conventional Women Safety Applications | 17 |
| 3.3 | Proposed Safira Solution Architecture | 18 |
| 3.4 | Functional Requirements Specification | 19 |
| 3.5 | Non-Functional Requirements Specification | 21 |
| 3.6 | Scope, Boundary Conditions & Operational Limitations | 22 |
| 3.7 | Comparison with the Initial Project Synopsis | 23 |
| **Chapter 4** | **Technology Stack and Requirements** | **24** |
| 4.1 | Technology Stack Overview | 24 |
| 4.2 | Frontend Technologies: React 19, TypeScript & Tailwind CSS | 25 |
| 4.3 | Geospatial & Cartography Engine: Leaflet 1.9 & LocationIQ Platform | 26 |
| 4.4 | Backend Architecture: Python 3.14, FastAPI & Uvicorn | 27 |
| 4.5 | Database & Persistence: PostgreSQL/PostGIS, SQLite & SQLAlchemy 2.0 | 28 |
| 4.6 | Cryptographic Security, BCrypt Clamping & Stateless JWT | 29 |
| 4.7 | Software Environment Requirements | 30 |
| 4.8 | Hardware Environment Specifications | 31 |
| **Chapter 5** | **System Architecture and Design** | **32** |
| 5.1 | Overall Multi-Tier System Architecture | 32 |
| 5.2 | End-to-End User Application Workflow | 33 |
| 5.3 | Unified Modeling Language (UML) Use Case View | 34 |
| 5.4 | Frontend Component Architecture & State Management | 35 |
| 5.5 | Backend Modular Architecture & Service Layer | 36 |
| 5.6 | Database Schema Design & Entity-Relationship Model | 37 |
| 5.7 | Stateless Authentication & Token Lifecycle Architecture | 39 |
| 5.8 | Geospatial Route Deviation Monitoring Pipeline | 40 |
| 5.9 | Companion Matching Engine Execution Pipeline | 41 |
| 5.10 | REST API Communication Flow & Request Sequences | 42 |
| **Chapter 6** | **Implementation and Working** | **43** |
| 6.1 | Project Directory Structure & Organization | 43 |
| 6.2 | User Registration, Sanitization & Manual Verification Workflow | 44 |
| 6.3 | JWT Security Filter & Role-Based Access Control | 45 |
| 6.4 | Journey Creation, LocationIQ Autocomplete & Reverse Geocoding | 46 |
| 6.5 | Interactive MapView Component: LocationIQ Tiles & Custom GIS Markers | 47 |
| 6.6 | Real-Time Route Deviation Detection Engine | 48 |
| 6.7 | Instant Emergency SOS System & Multi-Channel Guardian Dispatch | 49 |
| 6.8 | Journey Buddy: Collaborative Travel Scheduling & Discovery Interface | 50 |
| 6.9 | Encrypted In-App Coordination Chat for Confirmed Companions | 51 |
| 6.10 | Redesigned Startup-Grade Landing Page UI | 52 |
| **Chapter 7** | **Testing, Verification and Results** | **53** |
| 7.1 | Testing Methodology & Verification Strategy | 53 |
| 7.2 | Test Execution Environment | 54 |
| 7.3 | Comprehensive Functional Test Cases (TC-01 to TC-25) | 55 |
| 7.4 | Automated Unit and Integration Test Results (Pytest Suite) | 58 |
| 7.5 | Frontend Production Build & Bundle Performance Analysis | 59 |
| 7.6 | Real-World Route Simulation & Anomaly Detection Verification | 60 |
| 7.7 | Implementation Review Findings, Code Audits & Mitigations | 61 |
| 7.8 | Summary of Verification & Deployment Readiness | 63 |
| **Chapter 8** | **Algorithmic Framework and Mathematical Formulations** | **64** |
| 8.1 | Closed-Loop Travel Safety Monitoring Model | 64 |
| 8.2 | Haversine Great-Circle Geodesic Distance Formulation | 65 |
| 8.3 | Point-to-Polyline Perpendicular Cross-Track Distance Algorithm | 66 |
| 8.4 | Dynamic Sensor Accuracy Filtering & Persistence Counter | 67 |
| 8.5 | Rule-Based Composite Companion Compatibility Formulation | 68 |
| 8.6 | Spatial Route Overlap Analysis & Coordinate Decimation | 69 |
| 8.7 | Threat Modeling & Zero-Knowledge Location Masking | 70 |
| **Chapter 9** | **Conclusion and Future Scope** | **71** |
| 9.1 | Summary of Implemented Engineering Deliverables | 71 |
| 9.2 | Technical Limitations of Current Architecture | 72 |
| 9.3 | Future Research & Engineering Directions | 73 |
| 9.4 | Concluding Remarks | 74 |
| | **References** | **75** |
| | **Appendix A: Complete REST API Specification** | **77** |
| | **Appendix B: Test Geolocation Datasets & Simulation Scenarios** | **80** |
| | **Appendix C: Repository Source Files Inventory** | **82** |
| | **Appendix D: Selected Core Source Code Excerpts** | **84** |

<div style="page-break-after: always;"></div>

---

# LIST OF FIGURES

- **Figure 5.1**: Multi-Tier System Architecture of the Safira Platform
- **Figure 5.2**: End-to-End User Application Journey Lifecycle Flowchart
- **Figure 5.3**: Comprehensive UML Use Case Diagram for User, Companion, and Guardian Actors
- **Figure 5.4**: Detailed Entity-Relationship (ER) Diagram of the Relational Database Models
- **Figure 5.5**: Stateless JWT Bearer Authentication & Token Refresh Flowchart
- **Figure 5.6**: Geospatial Route Deviation Detection and Escalation State Machine
- **Figure 5.7**: Companion Matching Pipeline and Composite Compatibility Evaluation
- **Figure 5.8**: Sequence Diagram for Emergency SOS Trigger and Guardian Dispatch
- **Figure 6.1**: Modular Monolithic Directory Structure of the Backend and Frontend Repository
- **Figure 6.2**: User Registration and Authentication Interface with Real-Time Validation
- **Figure 6.3**: Redesigned Startup-Level Hero Section with LocationIQ Corridor Preview
- **Figure 6.4**: Interactive Safe Journey Creation Page with LocationIQ Autocomplete Search
- **Figure 6.5**: Live Journey Monitoring Screen with Pulsing GPS Beacon and Telemetry Strip
- **Figure 6.6**: Leaflet Map Displaying Off-Corridor Deviation and 150m Safety Buffer
- **Figure 6.7**: Interactive Route Deviation Confirmation Modal with 60-Second Countdown
- **Figure 6.8**: Journey Buddy ("Travel Together") Companion Discovery and Filtering Interface
- **Figure 6.9**: Confirmed Companion Group Screen with Safe In-App Coordination Chat
- **Figure 6.10**: Trusted Guardians and Emergency Alert History Screen with Distress Location Map
- **Figure 7.1**: Pytest Automated Test Execution Terminal Showing 11 Passed Integration Suites
- **Figure 7.2**: Vite Production Build Terminal Output Demonstrating Sub-Second Bundling
- **Figure 8.1**: Closed-Loop Monitor-Analyze-Recommend-Act-Escalate Travel Safety Model
- **Figure 8.2**: Geometric Representation of Point-to-Segment Cross-Track Distance Calculation
- **Figure 8.3**: Multi-Parameter Composite Compatibility Scoring Distribution

<div style="page-break-after: always;"></div>

---

# LIST OF TABLES

- **Table 1.1**: Project Objectives, Technical Specifications, and Implementation Status
- **Table 2.1**: Comparative Literature Analysis of Published Women's Safety Systems
- **Table 3.1**: Comprehensive Functional Requirements Specification and Audit Status
- **Table 3.2**: Non-Functional Requirements Specification with Quantitative Targets
- **Table 3.3**: Comparison Between Initial Synopsis Specifications and Implemented Platform
- **Table 4.1**: Full-Stack Technology Stack Overview and Architectural Responsibilities
- **Table 4.2**: Software Environment and Dependency Specifications
- **Table 4.3**: Minimum and Recommended Hardware Specifications
- **Table 5.1**: Complete REST API Endpoints Inventory Across All Modules
- **Table 6.1**: Deterministic Companion Compatibility Weight Matrix
- **Table 6.2**: Standard Public Meeting Point Categories and Curated Safety Attributes
- **Table 7.1**: Exhaustive Functional Test Cases Suite (TC-01 through TC-25)
- **Table 7.2**: Implementation Code Review Findings, Security Audits, and Mitigations
- **Table 8.1**: Mathematical Notations and Operational Definitions
- **Table A.1**: Detailed REST API Request DTO Validation Constraints
- **Table A.2**: REST API Response Schemas and Status Codes
- **Table B.1**: Geolocation Coordinates for Real-World Manhattan & Campus Corridors
- **Table C.1**: Complete Repository Source Files Inventory and Line Counts

<div style="page-break-after: always;"></div>

---

# LIST OF ABBREVIATIONS

| Abbreviation | Expansion |
|:---|:---|
| **API** | Application Programming Interface |
| **BCrypt** | Blowfish-Based Adaptive Key Derivation Password Hashing Function |
| **CORS** | Cross-Origin Resource Sharing |
| **CSRF** | Cross-Site Request Forgery |
| **CSS** | Cascading Style Sheets |
| **DTO** | Data Transfer Object |
| **ERD** | Entity-Relationship Diagram |
| **GIS** | Geographic Information System |
| **GPS** | Global Positioning System |
| **HMAC** | Hash-Based Message Authentication Code |
| **HTML** | HyperText Markup Language |
| **HTTP** | HyperText Transfer Protocol |
| **HTTPS** | HyperText Transfer Protocol Secure |
| **JSON** | JavaScript Object Notation |
| **JWT** | JSON Web Token |
| **LMS** | Learning Management System |
| **MVP** | Minimum Viable Product |
| **ORM** | Object-Relational Mapping |
| **OSRM** | Open Source Routing Machine |
| **POI** | Point of Interest |
| **PostGIS** | PostgreSQL Spatial Database Extender |
| **REST** | Representational State Transfer |
| **RBAC** | Role-Based Access Control |
| **SMS** | Short Message Service |
| **SOS** | Save Our Souls (Standard Distress Signal) |
| **SQL** | Structured Query Language |
| **UI** | User Interface |
| **UML** | Unified Modeling Language |
| **URI** | Uniform Resource Identifier |
| **URL** | Uniform Resource Locator |
| **UTC** | Coordinated Universal Time |
| **UUID** | Universally Unique Identifier |
| **Vite** | Frontend Next-Generation Build Tool |
| **WGS-84** | World Geodetic System 1984 |
| **WDAC** | Windows Defender Application Control |

<div style="page-break-after: always;"></div>
"""
