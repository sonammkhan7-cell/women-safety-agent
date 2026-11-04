import pytest
from app.utils.geo import (
    haversine_distance, point_to_segment_distance, point_to_polyline_distance,
    encode_polyline, decode_polyline, calculate_route_overlap
)

def test_haversine_distance():
    # Approx distance between Times Square (40.7580, -73.9855) and Empire State (40.7484, -73.9857) is ~1070 meters
    dist = haversine_distance(40.7580, -73.9855, 40.7484, -73.9857)
    assert 1000 <= dist <= 1200

def test_polyline_encoding_decoding():
    points = [(40.7580, -73.9855), (40.7530, -73.9856), (40.7484, -73.9857)]
    encoded = encode_polyline(points)
    assert isinstance(encoded, str)
    decoded = decode_polyline(encoded)
    assert len(decoded) == len(points)
    for orig, dec in zip(points, decoded):
        assert pytest.approx(orig[0], abs=1e-4) == dec[0]
        assert pytest.approx(orig[1], abs=1e-4) == dec[1]

def test_point_to_polyline_distance():
    # Segment from (0.0, 0.0) to (0.0, 0.01) along equator
    line = [(0.0, 0.0), (0.0, 0.01)]
    # Point at (0.001, 0.005) -> distance is roughly ~111 meters north of segment midpoint
    dist = point_to_polyline_distance(0.001, 0.005, line)
    assert 100 <= dist <= 125

def test_route_overlap_calculation():
    # Two almost identical routes
    r1 = [(40.71, -74.00), (40.72, -74.00), (40.73, -74.00), (40.74, -74.00)]
    r2 = [(40.71, -74.00), (40.72, -74.0005), (40.73, -74.0002), (40.74, -74.00)]
    overlap_pct, shared = calculate_route_overlap(r1, r2, corridor_threshold_meters=200.0)
    assert overlap_pct >= 90.0

    # Two completely separated routes
    r3 = [(51.50, -0.12), (51.51, -0.12)]
    overlap_pct_zero, _ = calculate_route_overlap(r1, r3, corridor_threshold_meters=200.0)
    assert overlap_pct_zero == 0.0

