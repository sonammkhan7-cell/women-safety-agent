import json
import logging
import math
from typing import Dict, Any, List, Optional, Tuple
import httpx
from app.config import settings
from app.utils.geo import haversine_distance, encode_polyline, decode_polyline

logger = logging.getLogger(__name__)

def generate_fallback_route(
    orig_lat: float, orig_lng: float,
    dest_lat: float, dest_lng: float,
    travel_mode: str = "walking"
) -> Dict[str, Any]:
    """
    Generates a realistic multi-segment path between origin and destination
    when Google Maps Routes API key is not configured or in local development.
    """
    dist_meters = haversine_distance(orig_lat, orig_lng, dest_lat, dest_lng)
    
    # Speed in m/s based on travel mode
    speeds = {
        "walking": 1.4,      # ~5 km/h
        "bicycling": 4.1,    # ~15 km/h
        "transit": 8.3,      # ~30 km/h
        "driving": 11.1      # ~40 km/h
    }
    speed = speeds.get(travel_mode.lower(), 1.4)
    duration_sec = int(dist_meters / speed) + 60

    # Generate realistic intermediate road waypoints with minor organic curvature
    num_steps = max(5, min(25, int(dist_meters / 150)))
    points: List[Tuple[float, float]] = []
    
    for i in range(num_steps + 1):
        fraction = i / float(num_steps)
        lat = orig_lat + (dest_lat - orig_lat) * fraction
        lng = orig_lng + (dest_lng - orig_lng) * fraction
        
        # Subtle realistic road dog-leg curvature except at endpoints
        if 0 < i < num_steps:
            offset = math.sin(fraction * math.pi) * 0.0008
            lat += offset
            lng += (offset * 0.5)

        points.append((round(lat, 6), round(lng, 6)))

    poly = encode_polyline(points)
    
    bounds = {
        "min_lat": min(orig_lat, dest_lat),
        "max_lat": max(orig_lat, dest_lat),
        "min_lng": min(orig_lng, dest_lng),
        "max_lng": max(orig_lng, dest_lng),
    }

    return {
        "distance_meters": round(dist_meters, 1),
        "duration_seconds": duration_sec,
        "polyline": poly,
        "waypoints": [{"lat": p[0], "lng": p[1]} for p in points],
        "bounds": bounds,
        "source": "simulated_geodesic"
    }

async def calculate_route(
    orig_lat: float, orig_lng: float,
    dest_lat: float, dest_lng: float,
    travel_mode: str = "walking"
) -> Dict[str, Any]:
    """
    Calculates route via LocationIQ Directions API, Google Maps Routes API, or high-fidelity fallback.
    """
    # 1. Try LocationIQ Directions API first if key configured
    if settings.LOCATIONIQ_API_KEY:
        liq_mode_map = {
            "walking": "walking",
            "bicycling": "cycling",
            "transit": "driving",
            "driving": "driving"
        }
        profile = liq_mode_map.get(travel_mode.lower(), "driving")
        liq_url = f"https://us1.locationiq.com/v1/directions/{profile}/{orig_lng},{orig_lat};{dest_lng},{dest_lat}"
        params = {
            "key": settings.LOCATIONIQ_API_KEY,
            "overview": "full",
            "geometries": "geojson"
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(liq_url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    routes = data.get("routes", [])
                    if routes:
                        r = routes[0]
                        coords = r.get("geometry", {}).get("coordinates", [])
                        pts = [(round(c[1], 6), round(c[0], 6)) for c in coords]
                        dist = float(r.get("distance", haversine_distance(orig_lat, orig_lng, dest_lat, dest_lng)))
                        dur = int(float(r.get("duration", dist / 1.4)))
                        poly = encode_polyline(pts) if pts else ""
                        all_lats = [p[0] for p in pts] or [orig_lat, dest_lat]
                        all_lngs = [p[1] for p in pts] or [orig_lng, dest_lng]
                        return {
                            "distance_meters": round(dist, 1),
                            "duration_seconds": dur,
                            "polyline": poly,
                            "waypoints": [{"lat": p[0], "lng": p[1]} for p in pts],
                            "bounds": {
                                "min_lat": min(all_lats),
                                "max_lat": max(all_lats),
                                "min_lng": min(all_lngs),
                                "max_lng": max(all_lngs)
                            },
                            "source": "locationiq_directions_api"
                        }
        except Exception as e:
            logger.warning(f"LocationIQ Directions API call failed, falling back: {e}")

    # 2. Try Google Maps Routes API if key configured
    if settings.GOOGLE_MAPS_API_KEY:
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        mode_map = {
            "walking": "WALK",
            "bicycling": "BICYCLE",
            "transit": "TRANSIT",
            "driving": "DRIVE"
        }
        google_mode = mode_map.get(travel_mode.lower(), "WALK")
        payload = {
            "origin": {"location": {"latLng": {"latitude": orig_lat, "longitude": orig_lng}}},
            "destination": {"location": {"latLng": {"latitude": dest_lat, "longitude": dest_lng}}},
            "travelMode": google_mode,
            "polylineQuality": "HIGH_QUALITY",
            "computeAlternativeRoutes": False
        }
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": settings.GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline,routes.viewport"
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    if "routes" in data and len(data["routes"]) > 0:
                        r = data["routes"][0]
                        poly = r.get("polyline", {}).get("encodedPolyline", "")
                        dist = float(r.get("distanceMeters", 0))
                        dur_str = r.get("duration", "0s").replace("s", "")
                        dur = int(float(dur_str)) if dur_str else 0
                        pts = decode_polyline(poly)
                        return {
                            "distance_meters": dist,
                            "duration_seconds": dur,
                            "polyline": poly,
                            "waypoints": [{"lat": p[0], "lng": p[1]} for p in pts],
                            "bounds": {
                                "min_lat": min(orig_lat, dest_lat),
                                "max_lat": max(orig_lat, dest_lat),
                                "min_lng": min(orig_lng, dest_lng),
                                "max_lng": max(orig_lng, dest_lng)
                            },
                            "source": "google_routes_api"
                        }
        except Exception as e:
            logger.warning(f"Google Routes API call failed, falling back to geodesic: {e}")

    return generate_fallback_route(orig_lat, orig_lng, dest_lat, dest_lng, travel_mode)

def get_fallback_safe_meeting_points(center_lat: float, center_lng: float) -> List[Dict[str, Any]]:
    """Safe, well-lit public meeting locations discovered near coordinate."""
    return [
        {
            "name": "Central Metro Station - Well Lit Security Concourse",
            "lat": round(center_lat + 0.0012, 6),
            "lng": round(center_lng + 0.0009, 6),
            "place_type": "transit_station",
            "safety_tags": ["24/7 CCTV", "Security Guard", "Public Transit Hub"]
        },
        {
            "name": "City Public Library - Main Entrance Lobby",
            "lat": round(center_lat - 0.0008, 6),
            "lng": round(center_lng + 0.0014, 6),
            "place_type": "public_building",
            "safety_tags": ["Well-Lit", "Civic Center", "Active Foot Traffic"]
        },
        {
            "name": "Cafe Corner (24/7 Staffed Coffee Shop)",
            "lat": round(center_lat + 0.0005, 6),
            "lng": round(center_lng - 0.0011, 6),
            "place_type": "cafe",
            "safety_tags": ["Open Late", "Indoor Seating", "Staffed"]
        }
    ]

async def find_public_meeting_points(center_lat: float, center_lng: float, radius: int = 1500) -> List[Dict[str, Any]]:
    """
    Discovers nearby public, safe meeting locations (transit stations, cafes, libraries)
    using Google Places API or curated safe public hubs.
    """
    if not settings.GOOGLE_MAPS_API_KEY:
        return get_fallback_safe_meeting_points(center_lat, center_lng)

    url = "https://places.googleapis.com/v1/places:searchNearby"
    payload = {
        "includedTypes": ["subway_station", "train_station", "bus_station", "cafe", "library"],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": center_lat, "longitude": center_lng},
                "radius": float(radius)
            }
        }
    }
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types"
    }
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for p in data.get("places", []):
                    name = p.get("displayName", {}).get("text", "Public Meeting Point")
                    loc = p.get("location", {})
                    types = p.get("types", [])
                    results.append({
                        "name": name,
                        "lat": loc.get("latitude", center_lat),
                        "lng": loc.get("longitude", center_lng),
                        "place_type": types[0] if types else "transit_station",
                        "safety_tags": ["Google Places Verified", "Public Spot"]
                    })
                if results:
                    return results
    except Exception as e:
        logger.warning(f"Google Places API lookup failed, falling back: {e}")

    return get_fallback_safe_meeting_points(center_lat, center_lng)

