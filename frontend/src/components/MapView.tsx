import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { 
  Shield, MapPin, AlertTriangle, Coffee, Compass, Crosshair, 
  Layers, AlertOctagon, CheckCircle2 
} from 'lucide-react';
import { api } from '../api/client';

interface Point {
  lat: number;
  lng: number;
}

interface MeetingPoint {
  name: string;
  lat: number;
  lng: number;
  place_type?: string;
}

interface MapViewProps {
  origin?: { name?: string; lat: number; lng: number };
  destination?: { name?: string; lat: number; lng: number };
  currentLocation?: { lat: number; lng: number; accuracy?: number } | null;
  waypoints?: Point[];
  meetingPoints?: MeetingPoint[];
  isDeviated?: boolean;
  deviationDistance?: number;
  isSosActive?: boolean;
  interactive?: boolean;
  height?: string;
  onPointSelect?: (point: { lat: number; lng: number; name: string }) => void;
  onLocateMe?: () => void;
}

export const MapView: React.FC<MapViewProps> = ({
  origin,
  destination,
  currentLocation,
  waypoints = [],
  meetingPoints = [],
  isDeviated = false,
  deviationDistance = 0,
  isSosActive = false,
  interactive = true,
  height = '460px',
  onPointSelect,
  onLocateMe,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const routePolylineRef = useRef<L.Polyline | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);

  const [mapStyle, setMapStyle] = useState<'streets' | 'dark'>('streets');
  const [selectedMeeting, setSelectedMeeting] = useState<MeetingPoint | null>(null);

  const locationIqKey = api.locationIQ.getKey();

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const defaultCenter: [number, number] = [
        currentLocation?.lat || origin?.lat || 40.7580,
        currentLocation?.lng || origin?.lng || -73.9855
      ];

      const map = L.map(mapContainerRef.current, {
        center: defaultCenter,
        zoom: 14,
        zoomControl: false,
        attributionControl: false,
        dragging: interactive,
        touchZoom: interactive,
        scrollWheelZoom: interactive,
      });

      // Tile Layer using LocationIQ with OSM fallback
      const streetsUrl = locationIqKey
        ? `https://{s}-tiles.locationiq.com/v3/streets/r/{z}/{x}/{y}.png?key=${locationIqKey}`
        : 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
      const tileLayer = L.tileLayer(streetsUrl, {
        maxZoom: 19,
        subdomains: locationIqKey ? ['a', 'b', 'c'] : ['a', 'b', 'c'],
        errorTileUrl: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
      }).addTo(map);

      tileLayerRef.current = tileLayer;

      // Add Zoom Control at bottom right
      if (interactive) {
        L.control.zoom({ position: 'bottomright' }).addTo(map);
      }

      const markersGroup = L.layerGroup().addTo(map);
      markersLayerRef.current = markersGroup;
      mapInstanceRef.current = map;
    }

    return () => {
      // Map cleanup on unmount
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update Tile Style
  useEffect(() => {
    if (!tileLayerRef.current || !mapInstanceRef.current) return;
    
    // Choose between LocationIQ Streets and Carto Dark for night safety mode
    const url = mapStyle === 'streets'
      ? (locationIqKey
          ? `https://{s}-tiles.locationiq.com/v3/streets/r/{z}/{x}/{y}.png?key=${locationIqKey}`
          : 'https://tile.openstreetmap.org/{z}/{x}/{y}.png')
      : 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';

    tileLayerRef.current.setUrl(url);
  }, [mapStyle, locationIqKey]);

  // Update Markers and Polylines
  useEffect(() => {
    const map = mapInstanceRef.current;
    const markersGroup = markersLayerRef.current;
    if (!map || !markersGroup) return;

    markersGroup.clearLayers();

    const boundsPoints: L.LatLngExpression[] = [];

    // 1. Origin Marker
    if (origin && typeof origin.lat === 'number' && typeof origin.lng === 'number') {
      const originIcon = L.divIcon({
        className: 'custom-map-icon',
        html: `
          <div style="display:flex;flex-direction:column;align-items:center;cursor:pointer;">
            <div style="background:#4f46e5;color:white;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(79,70,229,0.5);border:2px solid white;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
            </div>
            <div style="background:rgba(15,23,42,0.9);color:white;font-size:10px;font-weight:700;padding:2px 6px;border-radius:6px;margin-top:3px;white-space:nowrap;border:1px solid rgba(255,255,255,0.2);">
              ${origin.name || 'Start'}
            </div>
          </div>
        `,
        iconSize: [30, 48],
        iconAnchor: [15, 30]
      });

      const marker = L.marker([origin.lat, origin.lng], { icon: originIcon });
      marker.bindPopup(`<b>Starting Point</b><br/>${origin.name || 'Origin'}`);
      marker.addTo(markersGroup);
      boundsPoints.push([origin.lat, origin.lng]);
    }

    // 2. Destination Marker
    if (destination && typeof destination.lat === 'number' && typeof destination.lng === 'number') {
      const destIcon = L.divIcon({
        className: 'custom-map-icon',
        html: `
          <div style="display:flex;flex-direction:column;align-items:center;cursor:pointer;">
            <div style="background:#e11d48;color:white;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 14px rgba(225,29,72,0.5);border:2px solid white;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/></svg>
            </div>
            <div style="background:rgba(15,23,42,0.9);color:white;font-size:10px;font-weight:700;padding:2px 6px;border-radius:6px;margin-top:3px;white-space:nowrap;border:1px solid rgba(255,255,255,0.2);">
              ${destination.name || 'Destination'}
            </div>
          </div>
        `,
        iconSize: [30, 48],
        iconAnchor: [15, 30]
      });

      const marker = L.marker([destination.lat, destination.lng], { icon: destIcon });
      marker.bindPopup(`<b>Destination</b><br/>${destination.name || 'Destination'}`);
      marker.addTo(markersGroup);
      boundsPoints.push([destination.lat, destination.lng]);
    }

    // 3. Current Location Beacon
    if (currentLocation && typeof currentLocation.lat === 'number' && typeof currentLocation.lng === 'number') {
      const isEmergency = isSosActive || isDeviated;
      const beaconColor = isEmergency ? '#ef4444' : '#06b6d4';
      const beaconHtml = `
        <div style="position:relative;display:flex;align-items:center;justify-content:center;cursor:pointer;">
          <div style="position:absolute;width:36px;height:36px;border-radius:50%;background:${beaconColor};opacity:0.35;animation:ping 1.5s cubic-bezier(0,0,0.2,1) infinite;"></div>
          <div style="position:relative;width:18px;height:18px;border-radius:50%;background:${beaconColor};border:3px solid white;box-shadow:0 0 12px ${beaconColor};display:flex;align-items:center;justify-content:center;">
            <div style="width:5px;height:5px;border-radius:50%;background:white;"></div>
          </div>
          <div style="position:absolute;top:22px;background:rgba(15,23,42,0.9);color:${beaconColor};font-size:9px;font-weight:800;padding:1px 5px;border-radius:4px;white-space:nowrap;border:1px solid ${beaconColor};">
            ${isSosActive ? 'SOS ACTIVE' : isDeviated ? 'OFF ROUTE' : 'YOU'}
          </div>
        </div>
      `;

      const userIcon = L.divIcon({
        className: 'user-location-beacon',
        html: beaconHtml,
        iconSize: [36, 44],
        iconAnchor: [18, 18]
      });

      const userMarker = L.marker([currentLocation.lat, currentLocation.lng], { icon: userIcon, zIndexOffset: 1000 });
      userMarker.bindPopup(`<b>Your Live Location</b><br/>Accuracy: ±${Math.round(currentLocation.accuracy || 10)}m`);
      userMarker.addTo(markersGroup);
      boundsPoints.push([currentLocation.lat, currentLocation.lng]);
    }

    // 4. Safe Public Meeting Points
    meetingPoints.forEach((mp) => {
      const mpIcon = L.divIcon({
        className: 'meeting-point-icon',
        html: `
          <div style="display:flex;flex-direction:column;align-items:center;cursor:pointer;">
            <div style="background:#f59e0b;color:#0f172a;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 3px 10px rgba(245,158,11,0.5);border:2px solid white;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>
            </div>
            <div style="background:rgba(15,23,42,0.9);color:#fcd34d;font-size:9px;font-weight:700;padding:1px 5px;border-radius:4px;margin-top:2px;white-space:nowrap;border:1px solid rgba(245,158,11,0.4);">
              ${mp.name.split('-')[0].trim()}
            </div>
          </div>
        `,
        iconSize: [26, 40],
        iconAnchor: [13, 26]
      });

      const mpMarker = L.marker([mp.lat, mp.lng], { icon: mpIcon });
      mpMarker.on('click', () => {
        setSelectedMeeting(mp);
        if (onPointSelect) {
          onPointSelect({ lat: mp.lat, lng: mp.lng, name: mp.name });
        }
      });
      mpMarker.addTo(markersGroup);
      boundsPoints.push([mp.lat, mp.lng]);
    });

    // 5. Draw Route Polyline
    if (routePolylineRef.current) {
      routePolylineRef.current.remove();
      routePolylineRef.current = null;
    }

    if (waypoints.length > 1) {
      const latlngs: L.LatLngExpression[] = waypoints.map(w => [w.lat, w.lng]);
      
      const polyline = L.polyline(latlngs, {
        color: isDeviated ? '#ef4444' : '#4f46e5',
        weight: 5,
        opacity: 0.85,
        dashArray: isDeviated ? '8, 8' : undefined,
        lineCap: 'round',
        lineJoin: 'round'
      }).addTo(map);

      routePolylineRef.current = polyline;
      latlngs.forEach(pt => boundsPoints.push(pt));
    }

    // Auto fit bounds if points exist
    if (boundsPoints.length > 0) {
      try {
        const bounds = L.latLngBounds(boundsPoints);
        map.fitBounds(bounds, {
          padding: [50, 50],
          maxZoom: 16,
          animate: true
        });
      } catch (e) {
        console.warn('Error adjusting bounds:', e);
      }
    }
  }, [origin, destination, currentLocation, waypoints, meetingPoints, isDeviated, isSosActive]);

  const handleCenterOnUser = () => {
    if (onLocateMe) {
      onLocateMe();
    }
    if (currentLocation && mapInstanceRef.current) {
      mapInstanceRef.current.setView([currentLocation.lat, currentLocation.lng], 16, { animate: true });
    }
  };

  return (
    <div className="relative w-full rounded-2xl overflow-hidden bg-slate-900 border border-slate-700/60 shadow-xl select-none flex flex-col justify-between" style={{ height }}>
      {/* Map Header HUD */}
      <div className="absolute top-3 left-3 right-3 z-[1000] flex items-center justify-between pointer-events-none">
        {/* Status Chip */}
        <div className="flex items-center space-x-2 bg-slate-950/85 backdrop-blur-md px-3.5 py-1.5 rounded-xl border border-slate-700/60 shadow-lg pointer-events-auto">
          <div className={`w-2.5 h-2.5 rounded-full ${isSosActive ? 'bg-red-500 animate-ping' : isDeviated ? 'bg-rose-500 animate-pulse' : 'bg-emerald-500 animate-pulse'}`} />
          <span className="text-xs font-semibold tracking-wide text-slate-100 flex items-center gap-1.5">
            {isSosActive ? (
              <span className="text-red-400 font-bold flex items-center gap-1">
                <AlertOctagon className="w-3.5 h-3.5" /> SOS Emergency Active
              </span>
            ) : isDeviated ? (
              <span className="text-rose-400 font-bold flex items-center gap-1">
                <AlertTriangle className="w-3.5 h-3.5" /> Off-Corridor Deviation: {deviationDistance}m
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-slate-200">
                <Shield className="w-3.5 h-3.5 text-emerald-400" /> LocationIQ Safety Corridor
              </span>
            )}
          </span>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 pointer-events-auto">
          {/* Map Style Toggle */}
          <button
            type="button"
            onClick={() => setMapStyle(prev => prev === 'streets' ? 'dark' : 'streets')}
            className="bg-slate-950/85 hover:bg-slate-800 backdrop-blur-md p-2 rounded-xl border border-slate-700/60 text-slate-300 hover:text-white shadow-md transition"
            title={mapStyle === 'streets' ? "Switch to Night Safety Mode" : "Switch to Streets Mode"}
          >
            <Layers className="w-4 h-4" />
          </button>

          {/* Re-center User */}
          {currentLocation && (
            <button
              type="button"
              onClick={handleCenterOnUser}
              className="bg-indigo-600 hover:bg-indigo-500 text-white p-2 rounded-xl shadow-md transition flex items-center gap-1 text-xs font-semibold cursor-pointer"
              title="Center on my GPS location"
            >
              <Crosshair className="w-4 h-4" />
              <span className="hidden sm:inline">My Location</span>
            </button>
          )}
        </div>
      </div>

      {/* Actual Leaflet Map Canvas */}
      <div ref={mapContainerRef} className="w-full h-full z-0" />

      {/* Bottom Meeting Point Card */}
      {selectedMeeting && (
        <div className="absolute bottom-4 left-4 right-4 z-[1000] bg-slate-950/95 backdrop-blur-md p-3.5 rounded-xl border border-amber-500/40 shadow-2xl flex items-center justify-between">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-amber-500/20 text-amber-400 rounded-lg shrink-0 mt-0.5">
              <Coffee className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-semibold text-amber-400 flex items-center gap-1">
                Recommended Safe Checkpoint
              </div>
              <div className="text-white text-sm font-semibold">{selectedMeeting.name}</div>
              <div className="text-slate-400 text-xs">Public location with continuous lighting and active foot traffic.</div>
            </div>
          </div>
          <button
            onClick={() => setSelectedMeeting(null)}
            className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-600 cursor-pointer ml-3 shrink-0"
          >
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
};
