import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import { 
  Compass, Shield, Users, AlertTriangle, ArrowRight, Clock, Plus, MapPin, CheckCircle2, ChevronRight 
} from 'lucide-react';
import { SOSButton } from '../components/SOSButton';

export const DashboardPage: React.FC = () => {
  const { user, isVerified } = useAuth();
  const [journeys, setJourneys] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [contacts, setContacts] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchDashboardData = async () => {
    try {
      const [journeysData, alertsData, contactsData] = await Promise.all([
        api.getMyJourneys(),
        api.getAlerts(),
        api.getContacts()
      ]);
      setJourneys(journeysData);
      setAlerts(alertsData);
      setContacts(contactsData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const activeJourney = journeys.find(j => j.status === 'in_progress' || j.status === 'deviated' || j.status === 'attention_required');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Welcome Banner */}
      <div className="bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-800 text-white relative overflow-hidden shadow-xl">
        <div className="absolute right-0 top-0 w-80 h-80 bg-rose-600/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
                Member Dashboard
              </span>
              {isVerified ? (
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Verified Woman
                </span>
              ) : (
                <Link to="/verification" className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-950/80 border border-amber-500/40 text-amber-300 hover:underline">
                  Verification Pending • Complete Profile
                </Link>
              )}
            </div>

            <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
              Hello, {user?.name.split(' ')[0]}
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Your personal travel safety corridor and companion matching hub.
            </p>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            {activeJourney && (
              <SOSButton
                journeyId={activeJourney.id}
                currentLat={activeJourney.origin_lat}
                currentLng={activeJourney.origin_lng}
                onTriggered={() => fetchDashboardData()}
              />
            )}
            <Link
              to="/journeys/create"
              className="flex-1 sm:flex-none flex items-center justify-center gap-2 bg-rose-600 hover:bg-rose-500 text-white font-bold px-5 py-3 rounded-xl shadow-lg shadow-rose-600/30 transition active:scale-95 text-xs sm:text-sm"
            >
              <Plus className="w-4 h-4" />
              <span>Create Journey</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Active Ongoing Journey Alert Card */}
      {activeJourney && (
        <div className="bg-gradient-to-r from-slate-900 to-indigo-950/70 border-2 border-indigo-500/40 rounded-3xl p-6 shadow-xl text-white">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                  Live Journey in Progress
                </span>
                <span className="text-xs bg-slate-800 px-2 py-0.5 rounded text-slate-300 font-mono">
                  #{activeJourney.id}
                </span>
              </div>
              <h3 className="text-lg font-bold">
                {activeJourney.origin_name} → {activeJourney.destination_name}
              </h3>
              <p className="text-xs text-slate-400">
                Mode: <span className="text-slate-200 capitalize font-medium">{activeJourney.travel_mode}</span> • 
                Departure: <span className="text-slate-200 font-medium">{new Date(activeJourney.departure_time).toLocaleTimeString()}</span>
              </p>
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              {isVerified && (
                <Link
                  to={`/journeys/${activeJourney.id}/matches`}
                  className="px-4 py-2.5 bg-indigo-600/80 hover:bg-indigo-600 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5 transition"
                >
                  <Users className="w-3.5 h-3.5" />
                  <span>Find Companions</span>
                </Link>
              )}
              <Link
                to={`/journeys/${activeJourney.id}/live`}
                className="px-4 py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl text-xs flex items-center gap-1.5 shadow-md shadow-rose-600/30 transition"
              >
                <span>Open Live Map</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Grid: Journey History & Quick Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: My Journeys */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Compass className="w-5 h-5 text-rose-600" />
              <span>Your Journeys</span>
            </h2>
            <Link to="/journeys/create" className="text-xs font-bold text-rose-600 hover:text-rose-700">
              + Plan Route
            </Link>
          </div>

          {loading ? (
            <div className="bg-white rounded-3xl p-8 text-center text-slate-400 text-sm border border-slate-200">
              Loading journeys...
            </div>
          ) : journeys.length === 0 ? (
            <div className="bg-white rounded-3xl p-10 text-center border border-slate-200/80 shadow-sm text-slate-500">
              <Shield className="w-10 h-10 text-slate-300 mx-auto mb-2" />
              <p className="font-semibold text-sm">No journeys scheduled yet.</p>
              <p className="text-xs text-slate-400 mt-1 mb-4">Create your first route to test route monitoring and companion matching.</p>
              <Link
                to="/journeys/create"
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-rose-600 text-white font-bold rounded-xl text-xs shadow"
              >
                Create Journey
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {journeys.map((j) => (
                <div key={j.id} className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm hover:shadow-md transition">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                          j.status === 'in_progress' ? 'bg-emerald-100 text-emerald-800' :
                          j.status === 'completed' ? 'bg-slate-100 text-slate-600' :
                          j.status === 'deviated' ? 'bg-amber-100 text-amber-800' :
                          'bg-indigo-100 text-indigo-800'
                        }`}>
                          {j.status.replace('_', ' ')}
                        </span>
                        <span className="text-xs text-slate-400 font-mono">
                          {new Date(j.departure_time).toLocaleDateString()} at {new Date(j.departure_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>

                      <h4 className="text-sm font-bold text-slate-900">
                        {j.origin_name} <span className="text-slate-400 font-normal">→</span> {j.destination_name}
                      </h4>
                      <p className="text-xs text-slate-500">
                        Mode: <span className="capitalize font-medium">{j.travel_mode}</span>
                      </p>
                    </div>

                    <div className="flex items-center gap-2 self-start sm:self-center">
                      {isVerified && j.status !== 'completed' && j.status !== 'cancelled' && (
                        <Link
                          to={`/journeys/${j.id}/matches`}
                          className="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold rounded-xl text-xs flex items-center gap-1 border border-indigo-200 transition"
                        >
                          <Users className="w-3.5 h-3.5" />
                          <span>Companions</span>
                        </Link>
                      )}
                      <Link
                        to={`/journeys/${j.id}/live`}
                        className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-xl text-xs flex items-center gap-1 transition"
                      >
                        <span>View Live</span>
                        <ChevronRight className="w-3 h-3" />
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Safety Status & Trusted Contacts */}
        <div className="space-y-6">
          
          {/* Trusted Contacts Quick Box */}
          <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Shield className="w-4 h-4 text-emerald-600" />
                <span>Emergency Contacts</span>
              </h3>
              <Link to="/profile" className="text-xs text-rose-600 font-semibold hover:underline">
                Manage
              </Link>
            </div>

            {contacts.length === 0 ? (
              <div className="text-center py-4 text-xs text-slate-500 bg-slate-50 rounded-2xl p-4">
                <p className="mb-2">No trusted contacts configured yet.</p>
                <Link to="/profile" className="text-rose-600 font-bold hover:underline">
                  + Add Contact for SOS
                </Link>
              </div>
            ) : (
              <div className="space-y-2.5">
                {contacts.map((c) => (
                  <div key={c.id} className="p-3 bg-slate-50 rounded-xl flex items-center justify-between text-xs">
                    <div>
                      <div className="font-bold text-slate-900 flex items-center gap-1.5">
                        <span>{c.contact_name}</span>
                        {c.is_primary && (
                          <span className="text-[9px] bg-emerald-100 text-emerald-800 px-1.5 py-0.2 rounded font-semibold">
                            Primary
                          </span>
                        )}
                      </div>
                      <div className="text-slate-500">{c.contact_phone} • {c.relationship}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Alert History Card */}
          <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              <span>Recent Safety Dispatches</span>
            </h3>

            {alerts.length === 0 ? (
              <div className="text-xs text-slate-400 py-3 text-center bg-slate-50 rounded-xl">
                No emergency alerts recorded. All journeys safe.
              </div>
            ) : (
              <div className="space-y-2">
                {alerts.slice(0, 3).map((a) => (
                  <div key={a.id} className="p-3 rounded-xl border border-slate-100 bg-slate-50 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-800 uppercase text-[10px]">
                        {a.alert_type.replace('_', ' ')}
                      </span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                        a.status === 'resolved' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                      }`}>
                        {a.status}
                      </span>
                    </div>
                    <div className="text-slate-500 text-[11px] truncate">{a.address_text}</div>
                    <div className="text-[10px] text-slate-400">{new Date(a.created_at).toLocaleString()}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
};

