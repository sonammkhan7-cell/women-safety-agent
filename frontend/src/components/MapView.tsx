import React, { useRef, useState } from 'react';
import { Shield, MapPin, AlertTriangle, Coffee } from 'lucide-react';

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
  interactive?: boolean;
  height?: string;
  onPointSelect?: (point: { lat: number; lng: number; name: string }) => void;
}

export const MapView: React.FC<MapViewProps> = ({
  origin,
  destination,
  currentLocation,
  waypoints = [],
  meetingPoints = [],
  isDeviated = false,
  deviationDistance = 0,
  height = '420px',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedMeeting, setSelectedMeeting] = useState<MeetingPoint | null>(null);

  // Compute bounding box for projection
  const allLats = [
    origin?.lat,
    destination?.lat,
    currentLocation?.lat,
    ...waypoints.map(w => w.lat),
    ...meetingPoints.map(m => m.lat)
  ].filter((v): v is number => typeof v === 'number');

  const allLngs = [
    origin?.lng,
    destination?.lng,
    currentLocation?.lng,
    ...waypoints.map(w => w.lng),
    ...meetingPoints.map(m => m.lng)
  ].filter((v): v is number => typeof v === 'number');

  const minLat = allLats.length ? Math.min(...allLats) : 40.7500;
  const maxLat = allLats.length ? Math.max(...allLats) : 40.7700;
  const minLng = allLngs.length ? Math.min(...allLngs) : -73.9900;
  const maxLng = allLngs.length ? Math.max(...allLngs) : -73.9700;

  // Projection helper: maps (lat, lng) to canvas percentage coordinates (x: 5% - 95%, y: 5% - 95%)
  const project = (lat: number, lng: number) => {
    const latSpan = Math.max(0.002, maxLat - minLat);
    const lngSpan = Math.max(0.002, maxLng - minLng);
    
    // Invert Y because latitude increases northward while SVG/screen Y increases downward
    const yPct = 90 - ((lat - minLat) / latSpan) * 80;
    const xPct = 10 + ((lng - minLng) / lngSpan) * 80;
    return { x: xPct, y: yPct };
  };

  const polylineSvgPoints = waypoints.map(w => {
    const pt = project(w.lat, w.lng);
    return `${pt.x},${pt.y}`;
  }).join(' ');

  return (
    <div 
      ref={containerRef}
      style={{ height }}
      className="relative w-full rounded-2xl overflow-hidden bg-slate-900 border border-slate-700/60 shadow-lg flex flex-col justify-between select-none"
    >
      {/* Top Map HUD Bar */}
      <div className="absolute top-3 left-3 right-3 z-20 flex items-center justify-between pointer-events-none">
        <div className="flex items-center space-x-2 bg-slate-950/85 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-700/50 shadow-md pointer-events-auto">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs font-semibold text-slate-200 tracking-wide">
            {isDeviated ? (
              <span className="text-rose-400 font-bold flex items-center gap-1">
                <AlertTriangle className="w-3.5 h-3.5" /> Route Deviation: {deviationDistance}m
              </span>
            ) : (
              'Live Secure Corridor Monitoring'
            )}
          </span>
        </div>

        {/* Legend */}
        <div className="hidden sm:flex items-center space-x-3 bg-slate-950/85 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-700/50 text-[11px] text-slate-300 pointer-events-auto">
          <div className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 inline-block" />
            <span>Origin</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block" />
            <span>Destination</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" />
            <span>Safe Meeting</span>
          </div>
        </div>
      </div>

      {/* SVG Canvas Map Surface */}
      <svg className="w-full h-full absolute inset-0" viewBox="0 0 100 100" preserveAspectRatio="none">
        <defs>
          {/* Subtle Grid Pattern for cartographic realism */}
          <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
            <path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255, 255, 255, 0.04)" strokeWidth="0.5" />
          </pattern>
          {/* Neon Route Glow */}
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="1.5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        <rect width="100" height="100" fill="#0f172a" />
        <rect width="100" height="100" fill="url(#grid)" />

        {/* Coarse Route Corridor Buffer */}
        {polylineSvgPoints && (
          <polyline
            points={polylineSvgPoints}
            fill="none"
            stroke="rgba(99, 102, 241, 0.15)"
            strokeWidth="10"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}

        {/* Primary Planned Route Polyline */}
        {polylineSvgPoints && (
          <polyline
            points={polylineSvgPoints}
            fill="none"
            stroke={isDeviated ? "#f43f5e" : "#6366f1"}
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray={isDeviated ? "4, 2" : "none"}
            filter="url(#glow)"
          />
        )}

        {/* Off-route trajectory line if deviated */}
        {isDeviated && currentLocation && waypoints.length > 0 && (() => {
          const currPt = project(currentLocation.lat, currentLocation.lng);
          const firstPt = project(waypoints[0].lat, waypoints[0].lng);
          return (
            <line
              x1={firstPt.x}
              y1={firstPt.y}
              x2={currPt.x}
              y2={currPt.y}
              stroke="#fb7185"
              strokeWidth="1.2"
              strokeDasharray="2, 2"
            />
          );
        })()}
      </svg>

      {/* Render Markers via CSS Percentages for Crisp Icons */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Origin Marker */}
        {origin && (() => {
          const pt = project(origin.lat, origin.lng);
          return (
            <div 
              style={{ left: `${pt.x}%`, top: `${pt.y}%` }}
              className="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center pointer-events-auto group cursor-pointer"
            >
              <div className="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center shadow-lg ring-4 ring-indigo-500/30">
                <MapPin className="w-3.5 h-3.5" />
              </div>
              <span className="opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 text-white text-[10px] px-2 py-0.5 rounded shadow mt-1 whitespace-nowrap">
                {origin.name || 'Origin'}
              </span>
            </div>
          );
        })()}

        {/* Destination Marker */}
        {destination && (() => {
          const pt = project(destination.lat, destination.lng);
          return (
            <div 
              style={{ left: `${pt.x}%`, top: `${pt.y}%` }}
              className="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center pointer-events-auto group cursor-pointer"
            >
              <div className="w-6 h-6 rounded-full bg-rose-600 text-white flex items-center justify-center shadow-lg ring-4 ring-rose-500/30">
                <MapPin className="w-3.5 h-3.5" />
              </div>
              <span className="opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 text-white text-[10px] px-2 py-0.5 rounded shadow mt-1 whitespace-nowrap">
                {destination.name || 'Destination'}
              </span>
            </div>
          );
        })()}

        {/* Suggested Safe Meeting Points */}
        {meetingPoints.map((mp, idx) => {
          const pt = project(mp.lat, mp.lng);
          return (
            <div
              key={idx}
              style={{ left: `${pt.x}%`, top: `${pt.y}%` }}
              onClick={() => setSelectedMeeting(mp)}
              className="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center pointer-events-auto cursor-pointer group"
            >
              <div className="w-7 h-7 rounded-full bg-amber-500 text-slate-950 flex items-center justify-center shadow-xl ring-4 ring-amber-400/40 hover:scale-110 transition-transform">
                <Coffee className="w-3.5 h-3.5 stroke-[2.5]" />
              </div>
              <span className="bg-slate-950/90 text-amber-300 font-medium text-[10px] px-2 py-0.5 rounded-md shadow mt-1 whitespace-nowrap border border-amber-500/30">
                {mp.name.split('-')[0]}
              </span>
            </div>
          );
        })}

        {/* Live Current Location Pulsing Beacon */}
        {currentLocation && (() => {
          const pt = project(currentLocation.lat, currentLocation.lng);
          return (
            <div 
              style={{ left: `${pt.x}%`, top: `${pt.y}%` }}
              className="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center pointer-events-auto"
            >
              <div className="relative flex items-center justify-center">
                <span className={`animate-ping absolute inline-flex h-9 w-9 rounded-full opacity-75 ${isDeviated ? 'bg-rose-500' : 'bg-cyan-400'}`} />
                <div className={`w-4 h-4 rounded-full ${isDeviated ? 'bg-rose-500 ring-rose-300' : 'bg-cyan-400 ring-cyan-200'} ring-4 shadow-xl flex items-center justify-center`}>
                  <div className="w-1.5 h-1.5 rounded-full bg-white" />
                </div>
              </div>
              <span className="bg-slate-950/80 text-cyan-300 text-[10px] font-semibold px-1.5 py-0.5 rounded mt-1 shadow border border-cyan-500/30">
                You
              </span>
            </div>
          );
        })()}
      </div>

      {/* Selected Meeting Point Info Card Modal */}
      {selectedMeeting && (
        <div className="absolute bottom-3 left-3 right-3 z-30 bg-slate-950/95 backdrop-blur-md p-3.5 rounded-xl border border-amber-500/40 shadow-2xl flex items-center justify-between">
          <div>
            <div className="flex items-center gap-1.5 text-amber-400 text-xs font-semibold">
              <Shield className="w-3.5 h-3.5" /> Recommended Public Checkpoint
            </div>
            <div className="text-white text-sm font-medium">{selectedMeeting.name}</div>
            <div className="text-slate-400 text-xs">Well-lit transit hub with active foot traffic & security.</div>
          </div>
          <button
            onClick={() => setSelectedMeeting(null)}
            className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1.5 rounded-lg border border-slate-600 cursor-pointer"
          >
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
};
