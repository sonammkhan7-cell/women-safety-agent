import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { MapView } from '../components/MapView';
import { 
  MapPin, Clock, Navigation, Shield, ArrowRight, Eye, CheckCircle2, AlertCircle 
} from 'lucide-react';

interface RoutePreset {
  label: string;
  origName: string;
  origLat: number;
  origLng: number;
  destName: string;
  destLat: number;
  destLng: number;
  mode: string;
}

const PRESETS: RoutePreset[] = [
  {
    label: "Times Square → Columbus Circle (Campus Corridor)",
    origName: "Times Square North Station",
    origLat: 40.7580,
    origLng: -73.9855,
    destName: "Columbus Circle & 59th St",
    destLat: 40.7681,
    destLng: -73.9819,
    mode: "walking"
  },
  {
    label: "Broadway & 44th → Central Park South",
    origName: "Broadway & 44th St (Well-Lit Corner)",
    origLat: 40.7585,
    origLng: -73.9850,
    destName: "Central Park South & 7th Ave",
    destLat: 40.7685,
    destLng: -73.9815,
    mode: "walking"
  },
  {
    label: "Grand Central Terminal → Bryant Park Concourse",
    origName: "Grand Central Terminal - Main Concourse",
    origLat: 40.7527,
    origLng: -73.9772,
    destName: "Bryant Park Public Library Pavilion",
    destLat: 40.7536,
    destLng: -73.9832,
    mode: "walking"
  }
];

export const CreateJourneyPage: React.FC = () => {
  const navigate = useNavigate();

  const [originName, setOriginName] = useState(PRESETS[0].origName);
  const [originLat, setOriginLat] = useState(PRESETS[0].origLat);
  const [originLng, setOriginLng] = useState(PRESETS[0].origLng);

  const [destName, setDestName] = useState(PRESETS[0].destName);
  const [destLat, setDestLat] = useState(PRESETS[0].destLat);
  const [destLng, setDestLng] = useState(PRESETS[0].destLng);

  const [travelMode, setTravelMode] = useState<string>('walking');
  const [departureTime, setDepartureTime] = useState<string>(
    new Date(Date.now() + 15 * 60000).toISOString().slice(0, 16)
  );
  const [isPublic, setIsPublic] = useState<boolean>(true);

  const [routePreview, setRoutePreview] = useState<any>(null);
  const [previewLoading, setPreviewLoading] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSelectPreset = (preset: RoutePreset) => {
    setOriginName(preset.origName);
    setOriginLat(preset.origLat);
    setOriginLng(preset.origLng);
    setDestName(preset.destName);
    setDestLat(preset.destLat);
    setDestLng(preset.destLng);
    setTravelMode(preset.mode);
    setRoutePreview(null);
  };

  const handlePreviewRoute = async () => {
    setPreviewLoading(true);
    setErrorMsg(null);
    try {
      const data = await api.previewRoute({
        origin_lat: originLat,
        origin_lng: originLng,
        destination_lat: destLat,
        destination_lng: destLng,
        travel_mode: travelMode
      });
      setRoutePreview(data);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to calculate route preview.");
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleCreateAndStart = async (startImmediately: boolean = false) => {
    setSubmitting(true);
    setErrorMsg(null);
    try {
      const journey = await api.createJourney({
        origin_name: originName,
        origin_lat: originLat,
        origin_lng: originLng,
        destination_name: destName,
        destination_lat: destLat,
        destination_lng: destLng,
        travel_mode: travelMode,
        departure_time: new Date(departureTime).toISOString(),
        is_public_for_matching: isPublic
      });

      if (startImmediately) {
        await api.updateJourneyStatus(journey.id, 'in_progress');
      }

      navigate(`/journeys/${journey.id}/live`);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to create journey.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      <div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Plan Safe Journey</h1>
        <p className="text-sm text-slate-500 mt-1">
          Configure origin, destination, and departure time to monitor route deviations and find verified companions.
        </p>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Preset Quick Chooser */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm">
        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
          Quick Preset Routes (Verified Safety Corridors)
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSelectPreset(p)}
              className="p-3.5 rounded-2xl border text-left transition hover:border-rose-400 bg-slate-50/70 hover:bg-rose-50/30 cursor-pointer"
            >
              <div className="text-xs font-bold text-slate-900">{p.label}</div>
              <div className="text-[11px] text-slate-500 mt-1 capitalize">{p.mode} corridor</div>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Form: 5 Cols */}
        <div className="lg:col-span-5 bg-white rounded-3xl p-6 sm:p-7 border border-slate-200/80 shadow-sm space-y-5">
          
          {/* Origin */}
          <div className="space-y-2">
            <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-700">
              <MapPin className="w-4 h-4 text-indigo-600" />
              <span>1. Starting Location</span>
            </div>
            <input
              type="text"
              required
              placeholder="e.g. Times Square North Concourse"
              value={originName}
              onChange={e => setOriginName(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:border-rose-500"
            />
            <div className="grid grid-cols-2 gap-2 text-xs">
              <input
                type="number"
                step="0.0001"
                placeholder="Lat"
                value={originLat}
                onChange={e => setOriginLat(parseFloat(e.target.value) || 0)}
                className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-600 text-[11px]"
              />
              <input
                type="number"
                step="0.0001"
                placeholder="Lng"
                value={originLng}
                onChange={e => setOriginLng(parseFloat(e.target.value) || 0)}
                className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-600 text-[11px]"
              />
            </div>
          </div>

          {/* Destination */}
          <div className="space-y-2">
            <div className="flex items-center gap-1.5 text-xs font-bold text-rose-700">
              <MapPin className="w-4 h-4 text-rose-600" />
              <span>2. Destination</span>
            </div>
            <input
              type="text"
              required
              placeholder="e.g. Columbus Circle & 59th St"
              value={destName}
              onChange={e => setDestName(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:border-rose-500"
            />
            <div className="grid grid-cols-2 gap-2 text-xs">
              <input
                type="number"
                step="0.0001"
                placeholder="Lat"
                value={destLat}
                onChange={e => setDestLat(parseFloat(e.target.value) || 0)}
                className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-600 text-[11px]"
              />
              <input
                type="number"
                step="0.0001"
                placeholder="Lng"
                value={destLng}
                onChange={e => setDestLng(parseFloat(e.target.value) || 0)}
                className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-600 text-[11px]"
              />
            </div>
          </div>

          {/* Travel Mode & Departure Time */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Travel Mode</label>
              <select
                value={travelMode}
                onChange={e => setTravelMode(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-rose-500"
              >
                <option value="walking">Walking</option>
                <option value="transit">Public Transit</option>
                <option value="bicycling">Bicycling</option>
                <option value="driving">Driving / Cab</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Departure Time</label>
              <input
                type="datetime-local"
                value={departureTime}
                onChange={e => setDepartureTime(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-rose-500"
              />
            </div>
          </div>

          {/* Companion Discovery Visibility Toggle */}
          <div className="p-3.5 rounded-2xl bg-indigo-50/60 border border-indigo-100 flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-slate-900 block">Allow Companion Matching</span>
              <span className="text-[11px] text-slate-500">Allow other verified women to discover this route corridor.</span>
            </div>
            <input
              type="checkbox"
              checked={isPublic}
              onChange={e => setIsPublic(e.target.checked)}
              className="w-4 h-4 text-rose-600 rounded focus:ring-rose-500"
            />
          </div>

          {/* Preview Route Action Button */}
          <button
            type="button"
            onClick={handlePreviewRoute}
            disabled={previewLoading}
            className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition cursor-pointer"
          >
            <Eye className="w-4 h-4" />
            <span>{previewLoading ? 'Calculating Route...' : 'Preview Route on Map'}</span>
          </button>

          {/* Schedule / Start Buttons */}
          <div className="pt-2 border-t border-slate-100 space-y-2">
            <button
              type="button"
              onClick={() => handleCreateAndStart(true)}
              disabled={submitting}
              className="w-full py-3.5 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl text-sm shadow-lg shadow-rose-600/30 flex items-center justify-center gap-2 cursor-pointer transition active:scale-98 disabled:opacity-50"
            >
              <Navigation className="w-4 h-4" />
              <span>{submitting ? 'Creating...' : 'Start Journey Now (Live Tracking)'}</span>
            </button>

            <button
              type="button"
              onClick={() => handleCreateAndStart(false)}
              disabled={submitting}
              className="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs flex items-center justify-center gap-1.5 transition cursor-pointer"
            >
              <Clock className="w-3.5 h-3.5" />
              <span>Save as Planned Journey</span>
            </button>
          </div>
        </div>

        {/* Right Map Canvas: 7 Cols */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-white rounded-3xl p-4 border border-slate-200/80 shadow-sm">
            <MapView
              origin={{ name: originName, lat: originLat, lng: originLng }}
              destination={{ name: destName, lat: destLat, lng: destLng }}
              waypoints={routePreview?.waypoints || []}
              height="480px"
            />

            {routePreview && (
              <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                <div className="p-2.5 bg-slate-50 rounded-xl">
                  <span className="text-slate-400 block text-[10px]">Estimated Distance</span>
                  <span className="font-bold text-slate-800 text-sm">
                    {(routePreview.distance_meters / 1000).toFixed(2)} km
                  </span>
                </div>
                <div className="p-2.5 bg-slate-50 rounded-xl">
                  <span className="text-slate-400 block text-[10px]">Estimated Duration</span>
                  <span className="font-bold text-slate-800 text-sm">
                    {Math.round(routePreview.duration_seconds / 60)} minutes
                  </span>
                </div>
                <div className="p-2.5 bg-slate-50 rounded-xl col-span-2 sm:col-span-1">
                  <span className="text-slate-400 block text-[10px]">Route Calculation</span>
                  <span className="font-semibold text-indigo-600 text-xs capitalize">
                    {routePreview.source?.replace('_', ' ') || 'Secure Path'}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

