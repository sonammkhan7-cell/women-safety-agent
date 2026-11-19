import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { MapView } from '../components/MapView';
import { 
  MapPin, Clock, Navigation, Shield, ArrowRight, Eye, CheckCircle2, 
  AlertCircle, Crosshair, Search, Loader2, Sparkles 
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

  // Search / Autocomplete states
  const [originSearch, setOriginSearch] = useState('');
  const [originSuggestions, setOriginSuggestions] = useState<Array<{ display_name: string; lat: number; lon: number }>>([]);
  const [searchingOrigin, setSearchingOrigin] = useState(false);

  const [destSearch, setDestSearch] = useState('');
  const [destSuggestions, setDestSuggestions] = useState<Array<{ display_name: string; lat: number; lon: number }>>([]);
  const [searchingDest, setSearchingDest] = useState(false);

  // Current GPS state
  const [detectingGps, setDetectingGps] = useState(false);
  const [currentGps, setCurrentGps] = useState<{ lat: number; lng: number } | null>(null);

  // Route preview
  const [routePreview, setRoutePreview] = useState<any>(null);
  const [previewLoading, setPreviewLoading] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Detect GPS on initial mount if available
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setCurrentGps({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        },
        () => {},
        { timeout: 5000 }
      );
    }
  }, []);

  // Autocomplete debounce for Destination
  useEffect(() => {
    if (!destSearch || destSearch.trim().length < 3) {
      setDestSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      setSearchingDest(true);
      const res = await api.locationIQ.autocomplete(destSearch);
      setDestSuggestions(res);
      setSearchingDest(false);
    }, 350);

    return () => clearTimeout(timer);
  }, [destSearch]);

  // Autocomplete debounce for Origin
  useEffect(() => {
    if (!originSearch || originSearch.trim().length < 3) {
      setOriginSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      setSearchingOrigin(true);
      const res = await api.locationIQ.autocomplete(originSearch);
      setOriginSuggestions(res);
      setSearchingOrigin(false);
    }, 350);

    return () => clearTimeout(timer);
  }, [originSearch]);

  const handleUseCurrentLocationForOrigin = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      return;
    }

    setDetectingGps(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        setOriginLat(lat);
        setOriginLng(lng);
        setCurrentGps({ lat, lng });

        // Reverse geocode via LocationIQ
        const address = await api.locationIQ.reverseGeocode(lat, lng);
        setOriginName(address || `Current Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`);
        setDetectingGps(false);
      },
      (err) => {
        setDetectingGps(false);
        alert(`Location permission error: ${err.message}. Using default location.`);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

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
        <div className="flex items-center gap-2 mb-1">
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 border border-indigo-200 text-indigo-700">
            LocationIQ Maps Powered
          </span>
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 border border-emerald-200 text-emerald-700 flex items-center gap-1">
            <Shield className="w-3 h-3" /> Safety Corridors
          </span>
        </div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Plan Safe Journey & Route</h1>
        <p className="text-sm text-slate-500 mt-1">
          Search destinations via LocationIQ geocoding, preview real street routes, monitor deviations, and find verified travel companions.
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
          Quick Verified Safety Corridors
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSelectPreset(p)}
              className="p-3.5 rounded-2xl border text-left transition hover:border-indigo-400 bg-slate-50/70 hover:bg-indigo-50/30 cursor-pointer"
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
          <div className="space-y-2 relative">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-700">
                <MapPin className="w-4 h-4 text-indigo-600" />
                <span>1. Starting Location</span>
              </div>
              <button
                type="button"
                onClick={handleUseCurrentLocationForOrigin}
                disabled={detectingGps}
                className="text-[11px] font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 bg-indigo-50 px-2 py-1 rounded-lg border border-indigo-200 cursor-pointer"
              >
                {detectingGps ? <Loader2 className="w-3 h-3 animate-spin" /> : <Crosshair className="w-3 h-3" />}
                <span>{detectingGps ? 'Locating...' : 'Use My GPS'}</span>
              </button>
            </div>

            <div className="relative">
              <input
                type="text"
                placeholder="Search start address (LocationIQ geocoding)..."
                value={originSearch || originName}
                onChange={e => {
                  setOriginSearch(e.target.value);
                  setOriginName(e.target.value);
                }}
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:border-indigo-500 pl-9"
              />
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              {searchingOrigin && <Loader2 className="w-4 h-4 text-indigo-500 animate-spin absolute right-3 top-3" />}
            </div>

            {/* Origin Autocomplete Suggestions Dropdown */}
            {originSuggestions.length > 0 && (
              <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden max-h-48 overflow-y-auto">
                {originSuggestions.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      setOriginName(item.display_name);
                      setOriginLat(item.lat);
                      setOriginLng(item.lon);
                      setOriginSearch('');
                      setOriginSuggestions([]);
                    }}
                    className="w-full text-left px-3.5 py-2.5 hover:bg-indigo-50 text-xs border-b border-slate-100 last:border-b-0 flex items-center gap-2 text-slate-800"
                  >
                    <MapPin className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                    <span className="truncate">{item.display_name}</span>
                  </button>
                ))}
              </div>
            )}

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
          <div className="space-y-2 relative">
            <div className="flex items-center gap-1.5 text-xs font-bold text-rose-700">
              <MapPin className="w-4 h-4 text-rose-600" />
              <span>2. Destination Search</span>
            </div>

            <div className="relative">
              <input
                type="text"
                placeholder="Search destination via LocationIQ..."
                value={destSearch || destName}
                onChange={e => {
                  setDestSearch(e.target.value);
                  setDestName(e.target.value);
                }}
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:border-rose-500 pl-9"
              />
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              {searchingDest && <Loader2 className="w-4 h-4 text-rose-500 animate-spin absolute right-3 top-3" />}
            </div>

            {/* Destination Autocomplete Suggestions Dropdown */}
            {destSuggestions.length > 0 && (
              <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden max-h-48 overflow-y-auto">
                {destSuggestions.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      setDestName(item.display_name);
                      setDestLat(item.lat);
                      setDestLng(item.lon);
                      setDestSearch('');
                      setDestSuggestions([]);
                    }}
                    className="w-full text-left px-3.5 py-2.5 hover:bg-rose-50 text-xs border-b border-slate-100 last:border-b-0 flex items-center gap-2 text-slate-800"
                  >
                    <MapPin className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                    <span className="truncate">{item.display_name}</span>
                  </button>
                ))}
              </div>
            )}

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
              <span className="text-[11px] text-slate-500">Allow verified women to discover this route corridor.</span>
            </div>
            <input
              type="checkbox"
              checked={isPublic}
              onChange={e => setIsPublic(e.target.checked)}
              className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500 cursor-pointer"
            />
          </div>

          {/* Preview Route Action Button */}
          <button
            type="button"
            onClick={handlePreviewRoute}
            disabled={previewLoading}
            className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition cursor-pointer"
          >
            {previewLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Eye className="w-4 h-4" />}
            <span>{previewLoading ? 'Calculating LocationIQ Route...' : 'Preview Route on Map'}</span>
          </button>

          {/* Schedule / Start Buttons */}
          <div className="pt-2 border-t border-slate-100 space-y-2">
            <button
              type="button"
              onClick={() => handleCreateAndStart(true)}
              disabled={submitting}
              className="w-full py-3 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold shadow-md shadow-rose-600/30 flex items-center justify-center gap-2 transition cursor-pointer disabled:opacity-50"
            >
              <Navigation className="w-4 h-4" />
              <span>{submitting ? 'Creating Journey...' : 'Start Monitoring Now'}</span>
            </button>

            <button
              type="button"
              onClick={() => handleCreateAndStart(false)}
              disabled={submitting}
              className="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition cursor-pointer disabled:opacity-50"
            >
              <Clock className="w-4 h-4" />
              <span>Schedule For Later</span>
            </button>
          </div>

        </div>

        {/* Right Map Preview: 7 Cols */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-900">Interactive LocationIQ Map</h3>
                <p className="text-xs text-slate-500">Real-time street map rendering with GPS tracking</p>
              </div>

              {routePreview && (
                <div className="flex items-center gap-3 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-xl text-xs font-bold text-emerald-800">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>{(routePreview.distance_meters / 1000).toFixed(1)} km • {Math.round(routePreview.duration_seconds / 60)} mins</span>
                </div>
              )}
            </div>

            <MapView
              origin={{ name: originName, lat: originLat, lng: originLng }}
              destination={{ name: destName, lat: destLat, lng: destLng }}
              currentLocation={currentGps}
              waypoints={routePreview?.waypoints || []}
              interactive={true}
              height="480px"
              onLocateMe={handleUseCurrentLocationForOrigin}
            />

            {routePreview?.source && (
              <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
                <span className="flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
                  Routing Engine: {routePreview.source === 'locationiq_directions_api' ? 'LocationIQ Directions' : routePreview.source}
                </span>
                <span>Coordinates: {routePreview.waypoints?.length || 0} waypoints</span>
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
};
