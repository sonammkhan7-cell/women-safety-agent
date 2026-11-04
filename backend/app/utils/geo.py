import math
from typing import List, Tuple, Dict, Any, Optional

EARTH_RADIUS_METERS = 6371000.0

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on the earth in meters."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return EARTH_RADIUS_METERS * c

def point_to_segment_distance(
    p_lat: float, p_lon: float,
    a_lat: float, a_lon: float,
    b_lat: float, b_lon: float
) -> float:
    """
    Calculate minimum distance in meters from point P to line segment AB.
    Projects P onto AB using equirectangular projection approximation for short segments.
    """
    # If segment start and end are practically the same point
    seg_length = haversine_distance(a_lat, a_lon, b_lat, b_lon)
    if seg_length < 1e-4:
        return haversine_distance(p_lat, p_lon, a_lat, a_lon)

    # Use local Cartesian projection centered on A
    avg_lat_rad = math.radians((a_lat + b_lat + p_lat) / 3.0)
    cos_lat = math.cos(avg_lat_rad)

    # Convert degrees to meters approximately
    # 1 deg lat ~ 111139 m, 1 deg lon ~ 111139 * cos(lat) m
    scale_y = 111139.0
    scale_x = 111139.0 * cos_lat

    ax = a_lon * scale_x
    ay = a_lat * scale_y
    bx = b_lon * scale_x
    by = b_lat * scale_y
    px = p_lon * scale_x
    py = p_lat * scale_y

    dx = bx - ax
    dy = by - ay

    # Vector AB dot AP / |AB|^2
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)

    # Clamp t to segment [0, 1]
    t = max(0.0, min(1.0, t))

    # Nearest point on segment
    nearest_x = ax + t * dx
    nearest_y = ay + t * dy

    dist = math.hypot(px - nearest_x, py - nearest_y)
    return dist

def point_to_polyline_distance(
    lat: float, lon: float, polyline_points: List[Tuple[float, float]]
) -> float:
    """
    Calculate the minimum perpendicular distance from a GPS point to a route polyline.
    """
    if not polyline_points:
        return float("inf")
    if len(polyline_points) == 1:
        return haversine_distance(lat, lon, polyline_points[0][0], polyline_points[0][1])

    min_dist = float("inf")
    for i in range(len(polyline_points) - 1):
        a_lat, a_lon = polyline_points[i]
        b_lat, b_lon = polyline_points[i + 1]
        dist = point_to_segment_distance(lat, lon, a_lat, a_lon, b_lat, b_lon)
        if dist < min_dist:
            min_dist = dist

    return min_dist

def decode_polyline(encoded: str) -> List[Tuple[float, float]]:
    """
    Decodes an encoded Google Maps Polyline string into a list of (lat, lng) tuples.
    """
    points = []
    index = 0
    lat = 0
    lng = 0
    length = len(encoded)

    while index < length:
        b = 0
        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        points.append((lat / 1e5, lng / 1e5))

    return points

def encode_polyline(points: List[Tuple[float, float]]) -> str:
    """
    Encodes a list of (lat, lng) tuples into a Google Maps Polyline string.
    """
    def encode_value(val: int) -> str:
        val = ~(val << 1) if val < 0 else (val << 1)
        res = []
        while val >= 0x20:
            res.append(chr((0x20 | (val & 0x1f)) + 63))
            val >>= 5
        res.append(chr(val + 63))
        return "".join(res)

    encoded = []
    prev_lat = 0
    prev_lng = 0

    for lat, lng in points:
        lat_e5 = int(round(lat * 1e5))
        lng_e5 = int(round(lng * 1e5))
        encoded.append(encode_value(lat_e5 - prev_lat))
        encoded.append(encode_value(lng_e5 - prev_lng))
        prev_lat = lat_e5
        prev_lng = lng_e5

    return "".join(encoded)

def calculate_route_overlap(
    route1_points: List[Tuple[float, float]],
    route2_points: List[Tuple[float, float]],
    corridor_threshold_meters: float = 250.0
) -> Tuple[float, List[Tuple[float, float]]]:
    """
    Calculate deterministic route overlap percentage (0 - 100%) and shared corridor points.
    Samples points along route1 and tests proximity to route2.
    """
    if not route1_points or not route2_points:
        return 0.0, []

    matched_count = 0
    total_samples = len(route1_points)
    shared_points = []

    for pt in route1_points:
        dist = point_to_polyline_distance(pt[0], pt[1], route2_points)
        if dist <= corridor_threshold_meters:
            matched_count += 1
            shared_points.append(pt)

    overlap_pct = (matched_count / total_samples) * 100.0 if total_samples > 0 else 0.0
    return round(overlap_pct, 1), shared_points

