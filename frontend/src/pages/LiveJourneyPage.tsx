import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { MapView } from '../components/MapView';
import { DeviationModal } from '../components/DeviationModal';
import { SOSButton } from '../components/SOSButton';
import { 
  Navigation, Shield, AlertTriangle, CheckCircle2, Play, Square, Users, RefreshCw, Compass 
} from 'lucide-react';

export const LiveJourneyPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const journeyId = parseInt(id || '0');
  const navigate = useNavigate();

  const [journey, setJourney] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [currentLocation, setCurrentLocation] = useState<{ lat: number; lng: number; accuracy: number } | null>(null);
  const [waypoints, setWaypoints] = useState<any[]>([]);

  // Monitoring states
  const [isDeviated, setIsDeviated] = useState<boolean>(false);
  const [deviationDistance, setDeviationDistance] = useState<number>(0);
  const [showDeviationModal, setShowDeviationModal] = useState<boolean>(false);
  const [trackingActive, setTrackingActive] = useState<boolean>(false);
  const [watchId, setWatchId] = useState<number | null>(null);

  // Simulation controls for evaluation/demo
  const [simStepIndex, setSimStepIndex] = useState<number>(0);
  const [statusMessage, setStatusMessage] = useState<string>('Ready to monitor.');

  const fetchJourney = async () => {
    try {
      const data = await api.getJourney(journeyId);
      setJourney(data);
      if (data.route_data) {
        try {
          const parsed = JSON.parse(data.route_data);
          setWaypoints(parsed.waypoints || []);
        } catch (e) {
          console.error(e);
        }
      }
      if (data.status === 'in_progress') {
        setTrackingActive(true);
      }
    } catch (err: any) {
      alert(`Failed to load journey: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (journeyId) {
      fetchJourney();
    }
  }, [journeyId]);

  // Handle GPS coordinate update to backend
  const sendLocationUpdate = async (lat: number, lng: number, accuracy: number = 10.0) => {
    setCurrentLocation({ lat, lng, accuracy });
    try {
      const res = await api.recordLocation(journeyId, {
        latitude: lat,
        longitude: lng,
        accuracy: accuracy,
        speed: 1.4,
        heading: 0.0
      });

      setIsDeviated(res.is_deviation);
      setDeviationDistance(res.deviation_distance);

      if (res.prompt_user) {
        setShowDeviationModal(true);
      }

      if (res.journey_status === 'attention_required') {
        setStatusMessage('⚠️ Emergency Alert Active: Contacts notified.');
      } else if (res.is_deviation) {
        setStatusMessage(`Off-route: ${res.deviation_distance}m (${res.consecutive_deviations}/3 persistent checks)`);
      } else {
        setStatusMessage('On-path: Secure corridor normal.');
      }
    } catch (e: any) {
      console.error("Tracking update error:", e);
    }
  };

  // Browser Geolocation API integration
  const startBrowserGeolocation = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      return;
    }

    setTrackingActive(true);
    setStatusMessage("Browser Geolocation tracking activated.");

    const id = navigator.geolocation.watchPosition(
      (position) => {
        sendLocationUpdate(
          position.coords.latitude,
          position.coords.longitude,
          position.coords.accuracy || 15.0
        );
      },
      (err) => {
        console.warn("Geolocation watch warning:", err.message);
        setStatusMessage(`GPS notice: ${err.message}. You can use simulator below.`);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 5000
      }
    );
    setWatchId(id);
  };

  const stopTracking = () => {
    if (watchId !== null) {
      navigator.geolocation.clearWatch(watchId);
      setWatchId(null);
    }
    setTrackingActive(false);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (watchId !== null) {
        navigator.geolocation.clearWatch(watchId);
      }
    };
  }, [watchId]);

  // Realistic Simulation Handlers
  const handleSimulateNextStep = () => {
    if (waypoints.length === 0) return;
    const nextIdx = (simStepIndex + 1) % waypoints.length;
    setSimStepIndex(nextIdx);
    const pt = waypoints[nextIdx];
    sendLocationUpdate(pt.lat, pt.lng, 8.0);
  };

  const handleSimulateDeviation = () => {
    // Intentionally deviate ~300 meters perpendicular to route
    const basePt = currentLocation || waypoints[0] || { lat: journey.origin_lat, lng: journey.origin_lng };
    const deviatedLat = basePt.lat + 0.0035; // ~380 meters off
    const deviatedLng = basePt.lng + 0.0020;
    sendLocationUpdate(deviatedLat, deviatedLng, 10.0);
  };

  const handleEndJourney = async () => {
    stopTracking();
    try {
      await api.updateJourneyStatus(journeyId, 'completed');
      alert("Journey completed safely! Route monitoring ended.");
      navigate('/dashboard');
    } catch (err: any) {
      alert(`Error ending journey: ${err.message}`);
    }
  };

  const handleStartJourney = async () => {
    try {
      await api.updateJourneyStatus(journeyId, 'in_progress');
      setJourney({ ...journey, status: 'in_progress' });
      startBrowserGeolocation();
    } catch (err: any) {
      alert(`Error starting journey: ${err.message}`);
    }
  };

  if (loading || !journey) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-slate-500">
        Loading live route monitoring...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Top Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-5 rounded-3xl border border-slate-200/80 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
              journey.status === 'in_progress' ? 'bg-emerald-100 text-emerald-800' :
              journey.status === 'deviated' ? 'bg-amber-100 text-amber-800' :
              journey.status === 'attention_required' ? 'bg-rose-100 text-rose-800' :
              'bg-indigo-100 text-indigo-800'
            }`}>
              {journey.status.replace('_', ' ')}
            </span>
            <span className="text-xs text-slate-400 font-mono">Journey #{journey.id}</span>
          </div>
          <h1 className="text-xl font-black text-slate-900">
            {journey.origin_name} → {journey.destination_name}
          </h1>
        </div>

        <div className="flex items-center gap-2.5 w-full sm:w-auto">
          {/* Quick SOS Trigger */}
          <SOSButton
            journeyId={journey.id}
            currentLat={currentLocation?.lat || journey.origin_lat}
            currentLng={currentLocation?.lng || journey.origin_lng}
            onTriggered={() => fetchJourney()}
          />

          {journey.status !== 'in_progress' ? (
            <button
              onClick={handleStartJourney}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow cursor-pointer"
            >
              <Play className="w-4 h-4" />
              <span>Start Journey</span>
            </button>
          ) : (
            <button
              onClick={handleEndJourney}
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow cursor-pointer"
            >
              <Square className="w-3.5 h-3.5 fill-white" />
              <span>End Journey</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Grid: Interactive Map + Real-Time Telemetry */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left: Map Canvas (8 Cols) */}
        <div className="lg:col-span-8 bg-white p-4 rounded-3xl border border-slate-200/80 shadow-sm space-y-4">
          <MapView
            origin={{ name: journey.origin_name, lat: journey.origin_lat, lng: journey.origin_lng }}
            destination={{ name: journey.destination_name, lat: journey.destination_lat, lng: journey.destination_lng }}
            currentLocation={currentLocation || (waypoints[0] ? { lat: waypoints[0].lat, lng: waypoints[0].lng } : null)}
            waypoints={waypoints}
            isDeviated={isDeviated}
            deviationDistance={deviationDistance}
            height="520px"
          />

          {/* Telemetry Status Strip */}
          <div className="bg-slate-900 text-slate-100 p-4 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${isDeviated ? 'bg-rose-500 animate-ping' : 'bg-emerald-400'}`} />
              <span className="font-semibold">{statusMessage}</span>
            </div>

            <div className="flex items-center gap-4 text-slate-400 text-[11px]">
              <div>GPS Accuracy: <strong className="text-white">{currentLocation?.accuracy ? `±${Math.round(currentLocation.accuracy)}m` : 'Normal'}</strong></div>
              <div>Mode: <strong className="text-white capitalize">{journey.travel_mode}</strong></div>
            </div>
          </div>
        </div>

        {/* Right: Controls & Deviation Simulation Suite (4 Cols) */}
        <div className="lg:col-span-4 space-y-5">
          
          {/* Tracking Controls Box */}
          <div className="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Navigation className="w-4 h-4 text-rose-600" />
              <span>GPS Tracking Controls</span>
            </h3>

            <p className="text-xs text-slate-500 leading-relaxed">
              Real-time monitoring checks your GPS position against the planned route buffer. Minor variations are filtered out by GPS accuracy.
            </p>

            <div className="space-y-2">
              <button
                onClick={startBrowserGeolocation}
                className="w-full py-2.5 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 text-indigo-700 text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition cursor-pointer"
              >
                <Compass className="w-4 h-4 text-indigo-600" />
                <span>Sync Browser Geolocation API</span>
              </button>

              <button
                onClick={() => navigate(`/journeys/${journey.id}/matches`)}
                className="w-full py-2.5 bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-700 text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition cursor-pointer"
              >
                <Users className="w-4 h-4 text-rose-600" />
                <span>Search Travel Companions Along Path</span>
              </button>
            </div>
          </div>

          {/* Interactive Route Testing Simulator Box */}
          <div className="bg-slate-900 text-white p-5 rounded-3xl border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                <RefreshCw className="w-3.5 h-3.5 text-rose-400" />
                <span>Simulation / Testing Suite</span>
              </h3>
              <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded">Dev Mode</span>
            </div>

            <p className="text-xs text-slate-400">
              Easily simulate route progress or trigger persistent route deviations to test automated detection and safety escalation:
            </p>

            <div className="space-y-2.5">
              <button
                onClick={handleSimulateNextStep}
                className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-emerald-400 border border-emerald-500/30 text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition cursor-pointer"
              >
                <span>Step Forward Along Planned Route</span>
                <span className="text-[10px] text-slate-400">({simStepIndex + 1}/{waypoints.length})</span>
              </button>

              <button
                onClick={handleSimulateDeviation}
                className="w-full py-2.5 bg-rose-950/80 hover:bg-rose-900 border border-rose-500/50 text-rose-300 text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition cursor-pointer shadow-md"
              >
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <span>Simulate 350m Off-Route Deviation</span>
              </button>
            </div>

            <div className="text-[11px] text-slate-400 pt-2 border-t border-slate-800 leading-normal">
              💡 <em>Rule logic:</em> 3 persistent off-route readings trigger the safety confirmation check-in modal. If unanswered in 60s, emergency contacts are alerted.
            </div>
          </div>

        </div>

      </div>

      {/* Route Deviation Check-in Modal */}
      <DeviationModal
        journeyId={journey.id}
        isOpen={showDeviationModal}
        deviationDistance={deviationDistance}
        timeoutSeconds={60}
        onResolved={(action) => {
          setShowDeviationModal(false);
          setIsDeviated(false);
          setStatusMessage(`Deviation resolved via: ${action}. Route monitoring normal.`);
          fetchJourney();
        }}
      />
    </div>
  );
};

