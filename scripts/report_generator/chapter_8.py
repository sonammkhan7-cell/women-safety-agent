# -*- coding: utf-8 -*-
"""
Chapter 8: Algorithmic Framework and Mathematical Formulations for the Master Academic Project Report on Safira.
"""

def get_chapter_8():
    return r"""# CHAPTER 8
# ALGORITHMIC FRAMEWORK AND MATHEMATICAL FORMULATIONS

## 8.1 Closed-Loop Travel Safety Monitoring Model

The core computational engine of Safira is structured as an autonomous **closed-loop feedback control system**. Unlike open-loop safety software that requires external human triggers, Safira implements continuous sensing, filtering, calculation, evaluation, challenge-response verification, and automated escalation.

Figure 8.1 illustrates the closed-loop algorithmic architecture.

```
       +-----------------------------------------------------------+
       |             CLOSED-LOOP TRAVEL SAFETY MODEL               |
       +-----------------------------------------------------------+
                                     |
                                     v
                          [ SENSE TELEMETRY ]
                          - W3C Geolocation API
                          - Coordinate Fix P_t = (lat_t, lon_t)
                          - Sensor Accuracy sigma_t, Speed v_t
                                     |
                                     v
                          [ DYNAMIC FILTERING ]
                          - Noise & Multipath Suppression
                          - Dynamic Threshold: delta_eff = 150m + sigma_t
                                     |
                                     v
                          [ CALCULATE GEODESIC ]
                          - Polyline Segments S_k = (W_k, W_k+1)
                          - Cross-Track Distance d_xt(P_t, S_k)
                          - Minimum Distance d_min = min(d_xt)
                                     |
                                     v
                          [ ANOMALY EVALUATION ]
                          - Condition: d_min > delta_eff ?
                            * NO  -> Reset breach_count = 0 -> Normal State
                            * YES -> Increment breach_count += 1
                                     |
                                     v
                          [ TEMPORAL PERSISTENCE ]
                          - Is breach_count >= 3 ?
                            * NO  -> Log Jitter -> Continue Polling
                            * YES -> Trigger Challenge State
                                     |
                                     v
                          [ VERIFICATION CHALLENGE ]
                          - 60-Second Interactive Modal
                          - Response Received?
                            * "I Am Safe"     -> Reset State
                            * "Update Route"  -> Recalculate Polyline
                            * TIMEOUT (00:00) -> ESCALATE TO SOS
                                     |
                                     v
                          [ AUTONOMOUS ESCALATION ]
                          - Reverse Geocode Address via LocationIQ
                          - Dispatch Multi-Guardian Distress Alert
                          - Publish Real-Time GPS Tracking Map
```

*Figure 8.1: Closed-Loop Monitor-Analyze-Recommend-Act-Escalate Travel Safety Model*

Table 8.1 defines the formal mathematical notations utilized across the algorithmic models.

### Table 8.1: Mathematical Notations and Operational Definitions

| Symbol | Mathematical Domain | Operational Meaning | Unit / Scale |
|:---:|:---:|:---|:---:|
| $R$ | $\mathbb{R}^+$ | Mean spherical radius of the Earth | $6,371,000\text{ meters}$ |
| $P_t$ | $(\phi_t, \lambda_t) \in [-\frac{\pi}{2}, \frac{\pi}{2}] \times [-\pi, \pi]$ | Instantaneous user GPS coordinate (lat, lon) | Radians / Decimal Degrees |
| $\sigma_{\text{GPS}}$ | $\mathbb{R}^+$ | Device reported horizontal 1-$\sigma$ accuracy | Meters ($\text{m}$) |
| $\mathcal{P}$ | $\{W_1, W_2, \dots, W_n\}$ | Ordered sequence of route waypoints | Coordinate Array |
| $S_k$ | $(W_k, W_{k+1})$ | Directed line segment $k$ along the polyline | Vector Segment |
| $d_H(A, B)$ | $\mathbb{R}^+$ | Haversine great-circle geodesic distance | Meters ($\text{m}$) |
| $d_{xt}(P, S)$| $\mathbb{R}^+$ | Perpendicular cross-track distance | Meters ($\text{m}$) |
| $\delta_{\text{base}}$ | $\mathbb{R}^+$ | Baseline safe corridor radius | $150.0\text{ meters}$ |
| $\delta_{\text{eff}}$ | $\mathbb{R}^+$ | Dynamically adjusted safety threshold | Meters ($\text{m}$) |
| $C$ | $[0, 1] \subset \mathbb{R}$ | Normalized companion compatibility score | Percentage ($0 - 100\%$) |
| $w_i$ | $\mathbb{R}^+ \mid \sum w_i = 1$ | Relative importance weights for matching | Dimensionless |

---

## 8.2 Haversine Great-Circle Geodesic Distance Formulation

To compute accurate distances over the Earth's curved ellipsoidal surface, planar Euclidean distance metrics ($\sqrt{\Delta x^2 + \Delta y^2}$) are fundamentally inadequate, as they introduce severe longitudinal distortion away from the equator. Safira utilizes the **Haversine great-circle formula**.

Given two geographic points on the WGS-84 reference sphere:
- Point 1: $(\phi_1, \lambda_1)$ (latitude and longitude in radians)
- Point 2: $(\phi_2, \lambda_2)$ (latitude and longitude in radians)

The angular differences are defined as:

$$\Delta \phi = \phi_2 - \phi_1$$

$$\Delta \lambda = \lambda_2 - \lambda_1$$

The square of half the chord length between the points is given by:

$$a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1) \cdot \cos(\phi_2) \cdot \sin^2\left(\frac{\Delta \lambda}{2}\right)$$

The angular distance in radians is computed using the numerically stable two-argument arctangent function:

$$c = 2 \cdot \text{atan2}\left(\sqrt{a}, \; \sqrt{1 - a}\right)$$

The resulting great-circle geodesic distance $d_H$ is:

$$d_H(\text{Point}_1, \text{Point}_2) = R \cdot c$$

Where $R = 6,371,000\text{ m}$ is the Earth's volumetric mean radius.

---

## 8.3 Point-to-Polyline Perpendicular Cross-Track Distance Algorithm

A route is mathematically represented as a polyline $\mathcal{P} = \{W_1, W_2, \dots, W_n\}$ consisting of $n-1$ connected great-circle segments $S_k = (W_k, W_{k+1})$.

Figure 8.2 illustrates the geometry of the cross-track distance calculation from an instantaneous user position $P_t$ onto segment $S_k = (A, B)$.

```
                     P_t (Instantaneous GPS Fix)
                    / | \
                   /  |  \
                  /   |   \  d_H(B, P_t)
      d_H(A, P_t)/    | d_xt
                /     |     \
               /      |      \
              A-------X-------B
              W_k            W_k+1
              <---- d_at ---->
              <------- d_AB ------->
```

*Figure 8.2: Geometric Representation of Point-to-Segment Cross-Track Distance Calculation*

### Algorithmic Formulation:
For each trajectory segment $S_k$ defined by endpoints $A = (\phi_A, \lambda_A)$ and $B = (\phi_B, \lambda_B)$, and an arbitrary point $P_t = (\phi_P, \lambda_P)$:

1. **Calculate Great-Circle Initial Bearing from $A$ to $B$ ($\theta_{AB}$):**

$$\theta_{AB} = \text{atan2}\Big(\sin(\Delta \lambda_{AB})\cos(\phi_B), \; \cos(\phi_A)\sin(\phi_B) - \sin(\phi_A)\cos(\phi_B)\cos(\Delta \lambda_{AB})\Big)$$

2. **Calculate Great-Circle Initial Bearing from $A$ to $P_t$ ($\theta_{AP}$):**

$$\theta_{AP} = \text{atan2}\Big(\sin(\Delta \lambda_{AP})\cos(\phi_P), \; \cos(\phi_A)\sin(\phi_P) - \sin(\phi_A)\cos(\phi_P)\cos(\Delta \lambda_{AP})\Big)$$

3. **Compute the Perpendicular Cross-Track Distance ($d_{xt}$):**

$$d_{xt}(P_t, S_k) = \arcsin\left(\sin\left(\frac{d_H(A, P_t)}{R}\right) \cdot \sin(\theta_{AP} - \theta_{AB})\right) \cdot R$$

4. **Compute the Along-Track Distance Projection ($d_{at}$):**

$$d_{at}(P_t, S_k) = \arccos\left(\frac{\cos\left(\frac{d_H(A, P_t)}{R}\right)}{\cos\left(\frac{d_{xt}}{R}\right)}\right) \cdot R$$

5. **Segment Boundary Evaluation:**
The projected intercept $X$ lies strictly between segment endpoints $A$ and $B$ if and only if $0 \le d_{at} \le d_H(A, B)$.
- If $d_{at} < 0$, the closest point is endpoint $A$: $\text{dist}(P_t, S_k) = d_H(A, P_t)$
- If $d_{at} > d_H(A, B)$, the closest point is endpoint $B$: $\text{dist}(P_t, S_k) = d_H(B, P_t)$
- Otherwise, the perpendicular distance governs: $\text{dist}(P_t, S_k) = |d_{xt}(P_t, S_k)|$

6. **Global Minimum Distance:**
The overall shortest distance from the traveler to the entire route polyline is:

$$d_{\min}(P_t, \mathcal{P}) = \min_{1 \le k < n} \Big( \text{dist}(P_t, S_k) \Big)$$

---

## 8.4 Dynamic Sensor Accuracy Filtering & Persistence Counter

To eliminate false emergency triggers caused by urban canyon multipath reflections, Safira dynamically modulates the corridor threshold using real-time sensor uncertainty.

### Dynamic Threshold Modulation
The effective deviation boundary $\delta_{\text{eff}}$ is defined as:

$$\delta_{\text{eff}}(t) = \delta_{\text{base}} + \min\Big(\kappa \cdot \sigma_{\text{GPS}}(t), \; \sigma_{\max}\Big)$$

Where:
- $\delta_{\text{base}} = 150.0\text{ meters}$ is the guaranteed baseline corridor width.
- $\sigma_{\text{GPS}}(t)$ is the horizontal accuracy radius reported by the W3C Geolocation API at timestamp $t$.
- $\kappa = 1.0$ is the uncertainty scaling factor.
- $\sigma_{\max} = 50.0\text{ meters}$ is the maximum allowable accuracy relaxation ceiling.

Under ideal satellite visibility ($\sigma_{\text{GPS}} \le 10\text{m}$), $\delta_{\text{eff}} \approx 160\text{m}$. Under poor satellite geometry in dense urban alleys ($\sigma_{\text{GPS}} \ge 50\text{m}$), $\delta_{\text{eff}}$ safely expands to $200.0\text{m}$, absorbing GPS drift without triggering false alarms.

### 3-Point Temporal Persistence Filter
An instantaneous spatial breach does not immediately trigger an emergency alert. An anomaly flag is affirmed if and only if the cross-track distance violates the effective threshold across three consecutive, non-overlapping temporal fixes:

$$\mathcal{A}(t) = \prod_{i=0}^{2} \mathbb{I}\Big( d_{\min}(P_{t-i}, \mathcal{P}) > \delta_{\text{eff}}(t-i) \Big) \in \{0, 1\}$$

Where $\mathbb{I}(\cdot)$ is the indicator function returning 1 if the condition is satisfied and 0 otherwise. 

Only when $\mathcal{A}(t) = 1$ does the system escalate from `NORMAL` to `CHALLENGE_ACTIVE`, activating the 60-second interactive verification modal.

---

## 8.5 Rule-Based Composite Companion Compatibility Formulation

The Journey Buddy matching engine evaluates the mutual compatibility between two verified female commuters: the requesting traveler $T_{\text{req}}$ and a candidate commuter $T_{\text{cand}}$.

```
+-----------------------------------------------------------------------------------+
|               COMPOSITE COMPANION COMPATIBILITY WEIGHT DISTRIBUTION               |
+-----------------------------------------------------------------------------------+
|  [=== Route Overlap Proximity S_route (35%) ====================]                 |
|  [=== Temporal Alignment S_time (25%) ==============]                             |
|  [=== Destination Proximity S_dest (20%) =======]                                 |
|  [=== Travel Mode Concordance S_mode (10%) =]                                     |
|  [=== Community Trust & Verification S_trust (10%) =]                             |
+-----------------------------------------------------------------------------------+
```

*Figure 8.3: Multi-Parameter Composite Compatibility Scoring Distribution*

The total compatibility score $C \in [0, 1]$ is computed as a weighted linear combination of five normalized sub-scores:

$$C = \sum_{i=1}^{5} w_i \cdot S_i = w_1 S_{\text{route}} + w_2 S_{\text{time}} + w_3 S_{\text{dest}} + w_4 S_{\text{mode}} + w_5 S_{\text{trust}}$$

Subject to the normalization constraint $\sum_{i=1}^5 w_i = 1.0$:
- $w_1 = 0.35$ (Origin and Route Proximity Weight)
- $w_2 = 0.25$ (Temporal Departure Window Weight)
- $w_3 = 0.20$ (Destination Proximity Weight)
- $w_4 = 0.10$ (Travel Mode Concordance Weight)
- $w_5 = 0.10$ (Trust and Verification Level Weight)

### Sub-Score Mathematical Definitions:

1. **Origin Proximity Score ($S_{\text{route}}$):**
Measures the geodesic distance between the two departure origins, decaying linearly up to a cutoff distance $D_{\max}^{\text{orig}} = 2500\text{ meters}$:

$$S_{\text{route}} = \max\left(0, \; 1 - \frac{d_H(O_{\text{req}}, O_{\text{cand}})}{D_{\max}^{\text{orig}}}\right)$$

2. **Temporal Alignment Score ($S_{\text{time}}$):**
Evaluates the absolute departure time delta $|\Delta t| = |t_{\text{req}} - t_{\text{cand}}|$ in minutes, decaying linearly up to $T_{\max} = 45\text{ minutes}$:

$$S_{\text{time}} = \max\left(0, \; 1 - \frac{|\Delta t|}{T_{\max}}\right)$$

3. **Destination Proximity Score ($S_{\text{dest}}$):**
Measures distance between drop-off destinations, decaying up to $D_{\max}^{\text{dest}} = 3000\text{ meters}$:

$$S_{\text{dest}} = \max\left(0, \; 1 - \frac{d_H(D_{\text{req}}, D_{\text{cand}})}{D_{\max}^{\text{dest}}}\right)$$

4. **Travel Mode Concordance ($S_{\text{mode}}$):**

$$S_{\text{mode}} = \begin{cases} 
1.0 & \text{if } \text{mode}_{\text{req}} = \text{mode}_{\text{cand}} \\
0.6 & \text{if modes are complementary (e.g., Metro and Walking)} \\
0.2 & \text{if modes are incompatible (e.g., Personal Bike vs Metro)}
\end{cases}$$

5. **Community Trust and Verification Score ($S_{\text{trust}}$):**
Reflects identity verification status and positive companion ratings:

$$S_{\text{trust}} = \begin{cases}
1.0 & \text{if account is Verified with rating } \ge 4.5 \\
0.8 & \text{if account is Verified (new commuter)} \\
0.0 & \text{if unverified (programmatically blocked)}
\end{cases}$$

The final compatibility percentage displayed to commuters is formatted as:

$$\text{Match Percentage} = \text{round}(C \times 100\%)$$

Candidates scoring $C < 0.60$ (below 60%) are excluded from recommendation lists to ensure travelers are paired only with viable companions.

---

## 8.6 Spatial Route Overlap Analysis & Coordinate Decimation

When evaluating route similarity between two multi-segment polylines $\mathcal{P}_1$ and $\mathcal{P}_2$, raw high-density polylines returned by routing engines often contain hundreds of dense vertices, which can cause computational bottlenecks.

Safira implements two optimization techniques:
1. **Axis-Aligned Bounding Box (AABB) Indexing:** Prior to executing expensive geodesic cross-track comparisons, the system evaluates whether the 2D bounding envelopes of the two journeys intersect:

$$\text{Intersect}(\mathcal{B}_1, \mathcal{B}_2) = (\min \phi_1 \le \max \phi_2) \land (\max \phi_1 \ge \min \phi_2) \land (\min \lambda_1 \le \max \lambda_2) \land (\max \lambda_1 \ge \min \lambda_2)$$

If the bounding boxes do not overlap, the candidate is discarded immediately with $\mathcal{O}(1)$ computational cost.

2. **Douglas-Peucker Trajectory Decimation:** Trajectory polylines are simplified using the Douglas-Peucker algorithm, reducing vertex density by up to 70% while preserving geometric fidelity within an $\epsilon = 15\text{-meter}$ tolerance threshold.

---

## 8.7 Threat Modeling & Zero-Knowledge Location Masking

To ensure the safety platform cannot be inverted into a digital surveillance or predatory stalking tool, Safira was subjected to formal threat modeling using the Microsoft STRIDE methodology.

```
+-----------------------------------------------------------------------------------+
|                        SAFIRA STRIDE THREAT MITIGATION MATRIX                     |
+-----------------------------------------------------------------------------------+
| Threat Category        | Specific Transit Threat   | Safira Architectural Defense |
+------------------------+---------------------------+------------------------------+
| Spoofing Identity      | Male bad actor creates    | Mandatory manual ID check;   |
|                        | fake female profile.      | unverified accounts blocked. |
+------------------------+---------------------------+------------------------------+
| Tampering with Data    | Adversary intercepts &    | HMAC-SHA256 JWT tokens;      |
|                        | alters GPS coordinates.   | HTTPS TLS 1.3 transport.     |
+------------------------+---------------------------+------------------------------+
| Repudiation            | Denying triggering false  | Immutable database audit log |
|                        | alarms or panic signals.  | with UTC timestamps & fixes. |
+------------------------+---------------------------+------------------------------+
| Information Disclosure | Commuter stalks peer's    | Zero-Knowledge spatial cloak;|
|                        | home address via app.     | coarse zones; sanitized chat.|
+------------------------+---------------------------+------------------------------+
| Denial of Service      | Flooding API with dummy   | Debounced requests (300ms);  |
|                        | geocoding search queries. | strict Pydantic rate bounds. |
+------------------------+---------------------------+------------------------------+
| Elevation of Privilege | Bypassing verification to | FastAPI `require_verified`   |
|                        | access Journey Buddy.     | dependency injection guard.  |
+------------------------+---------------------------+------------------------------+
```

### Spatial Cloaking Principles:
- **Zero-Knowledge Origin Masking:** When a user schedules a commute, their exact starting residence is never broadcasted to search results. The system automatically snaps the displayed departure marker to the nearest major intersection or public transit stop within a 400-meter radius.
- **Mutual Consent Disclosure:** Complete contact details and exact live coordinates are strictly withheld until both parties confirm a connection request and transition to the confirmed companion state.

<div style="page-break-after: always;"></div>
"""
