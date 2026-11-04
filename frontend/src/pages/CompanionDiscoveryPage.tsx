import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api/client';
import { MapView } from '../components/MapView';
import { 
  Users, ShieldCheck, Clock, MapPin, Send, CheckCircle2, AlertCircle, Coffee, ArrowRight, EyeOff 
} from 'lucide-react';

export const CompanionDiscoveryPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const journeyId = parseInt(id || '0');

  const [matches, setMatches] = useState<any[]>([]);
  const [journey, setJourney] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const [requestMsg, setRequestMsg] = useState<string>('Hi! I am travelling along this corridor around the same time. Would you like to walk together?');
  const [submittingReq, setSubmittingReq] = useState<boolean>(false);
  const [successInfo, setSuccessInfo] = useState<string | null>(null);

  const fetchMatches = async () => {
    try {
      const [jData, matchesData] = await Promise.all([
        api.getJourney(journeyId),
        api.getMatches(journeyId)
      ]);
      setJourney(jData);
      setMatches(matchesData);
      if (matchesData.length > 0) {
        setSelectedCandidate(matchesData[0]);
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (journeyId) {
      fetchMatches();
    }
  }, [journeyId]);

  const handleSendRequest = async (candidate: any) => {
    setSubmittingReq(true);
    setSuccessInfo(null);
    try {
      await api.sendCompanionRequest({
        receiver_journey_id: candidate.journey_id,
        initial_message: requestMsg
      });
      setSuccessInfo(`Companion request sent to ${candidate.user_display_name}! Awaiting mutual confirmation.`);
    } catch (err: any) {
      alert(`Error sending companion request: ${err.message}`);
    } finally {
      setSubmittingReq(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-slate-500">
        Searching compatible verified women travelling along your corridor...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Title */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-rose-950/80 border border-rose-500/40 text-rose-300 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-rose-400" />
              Verified Women Matching
            </span>
            <span className="text-xs text-slate-400">Journey #{journeyId}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Compatible Travel Companions
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Deterministic rule-based matching based on route overlap, departure proximity, and safe public meeting hubs.
          </p>
        </div>

        <Link
          to={`/journeys/${journeyId}/live`}
          className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-xl text-xs transition"
        >
          Back to Live Map
        </Link>
      </div>

      {/* Privacy Guarantee Pill */}
      <div className="bg-indigo-50/80 border border-indigo-200/80 rounded-2xl p-4 flex items-center gap-3 text-xs text-indigo-950">
        <EyeOff className="w-5 h-5 text-indigo-600 shrink-0" />
        <div>
          <strong>Privacy Preserving Route Sharing:</strong> Exact home addresses and raw GPS feeds are protected. You see approximate corridors until both parties mutually accept the companion connection.
        </div>
      </div>

      {successInfo && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{successInfo}</span>
        </div>
      )}

      {matches.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 text-slate-500 space-y-3">
          <Users className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-800">No Active Compatible Matches Right Now</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            No other verified women are currently scheduled along this exact corridor within your departure time window. Your route remains private and monitored.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Candidates List: 5 Cols */}
          <div className="lg:col-span-5 space-y-3">
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
              Found {matches.length} Verified Match{matches.length > 1 ? 'es' : ''}
            </label>

            {matches.map((c, idx) => {
              const isSelected = selectedCandidate?.journey_id === c.journey_id;
              return (
                <div
                  key={idx}
                  onClick={() => setSelectedCandidate(c)}
                  className={`bg-white rounded-3xl p-5 border transition cursor-pointer shadow-sm ${
                    isSelected ? 'border-rose-500 ring-2 ring-rose-500/20' : 'border-slate-200/80 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-bold text-slate-900">{c.user_display_name}</h4>
                        <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.2 rounded-full font-bold">
                          Verified
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-400 capitalize">
                        Mode: {c.travel_mode} • Departure diff: ±{c.departure_time_diff_minutes} mins
                      </span>
                    </div>

                    <div className="text-right">
                      <span className="text-base font-black text-rose-600 block">
                        {c.compatibility_score}%
                      </span>
                      <span className="text-[10px] text-slate-400 font-medium">Compatibility</span>
                    </div>
                  </div>

                  {/* Metrics Bar */}
                  <div className="grid grid-cols-2 gap-2 text-[11px] bg-slate-50 p-2.5 rounded-xl mb-3">
                    <div>
                      <span className="text-slate-400 block text-[10px]">Route Overlap</span>
                      <span className="font-bold text-slate-800">{c.route_overlap_percentage}% shared</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[10px]">Dest. Proximity</span>
                      <span className="font-bold text-slate-800">within {(c.destination_proximity_meters / 1000).toFixed(1)} km</span>
                    </div>
                  </div>

                  {/* Public Meeting Hub */}
                  <div className="flex items-center gap-2 text-xs text-amber-800 bg-amber-50/70 p-2.5 rounded-xl border border-amber-200/60">
                    <Coffee className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                    <span className="truncate"><strong>Meeting Spot:</strong> {c.suggested_meeting_point?.name}</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Candidate Detailed Corridor View: 7 Cols */}
          {selectedCandidate && (
            <div className="lg:col-span-7 bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-5">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    Shared Corridor with {selectedCandidate.user_display_name}
                  </h3>
                  <p className="text-xs text-slate-500">
                    High-level corridor alignment and recommended well-lit public checkpoint.
                  </p>
                </div>
                <div className="px-3 py-1 bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold rounded-xl">
                  {selectedCandidate.compatibility_score}% Match Score
                </div>
              </div>

              {/* Map Preview */}
              <MapView
                origin={{ name: "Meeting Checkpoint", lat: selectedCandidate.suggested_meeting_point?.lat, lng: selectedCandidate.suggested_meeting_point?.lng }}
                waypoints={selectedCandidate.approx_shared_route || []}
                meetingPoints={[selectedCandidate.suggested_meeting_point]}
                height="340px"
              />

              {/* Request Message Box */}
              <div className="space-y-3 pt-2">
                <label className="block text-xs font-bold text-slate-700">
                  Optional Message with Companion Request
                </label>
                <textarea
                  rows={2}
                  value={requestMsg}
                  onChange={e => setRequestMsg(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:border-rose-500"
                />

                <button
                  type="button"
                  onClick={() => handleSendRequest(selectedCandidate)}
                  disabled={submittingReq}
                  className="w-full py-3 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl text-xs shadow-md shadow-rose-600/30 flex items-center justify-center gap-2 cursor-pointer transition active:scale-98 disabled:opacity-50"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{submittingReq ? 'Sending Request...' : `Send Companion Request to ${selectedCandidate.user_display_name}`}</span>
                </button>
              </div>
            </div>
          )}

        </div>
      )}
    </div>
  );
};

