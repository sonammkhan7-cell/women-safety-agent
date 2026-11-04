import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { MapView } from '../components/MapView';
import { 
  ShieldCheck, Users, MapPin, Coffee, CheckCircle2, AlertOctagon, Phone, Ban, ArrowLeft 
} from 'lucide-react';

export const ActiveCompanionJourneyPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const requestId = parseInt(id || '0');
  const navigate = useNavigate();
  const { user } = useAuth();

  const [request, setRequest] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [partnerStatus, setPartnerStatus] = useState<string>('En route to meeting point');
  const [myCheckin, setMyCheckin] = useState<string>('En route');

  const fetchCompanionData = async () => {
    try {
      const allRequests = await api.getMyRequests();
      const current = allRequests.find(r => r.id === requestId);
      if (!current || current.status !== 'accepted') {
        alert("Companion connection is not active or mutual consent was revoked.");
        navigate('/requests');
        return;
      }
      setRequest(current);
    } catch (err: any) {
      alert(`Failed to load companion journey: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (requestId) {
      fetchCompanionData();
    }
  }, [requestId]);

  const handleDisconnect = async () => {
    if (window.confirm("Are you sure you want to disconnect from this companion journey? Both users' shared route view will be closed.")) {
      try {
        await api.updateRequestStatus(requestId, 'cancelled');
        alert("Companion connection disconnected.");
        navigate('/dashboard');
      } catch (e: any) {
        alert(e.message);
      }
    }
  };

  if (loading || !request) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-slate-500">
        Loading shared companion room...
      </div>
    );
  }

  const partnerName = request.sender_id === user?.id ? request.receiver_name : request.sender_name;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <button
            onClick={() => navigate('/requests')}
            className="text-xs text-slate-400 hover:text-slate-700 flex items-center gap-1 mb-2 font-medium"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Requests
          </button>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">
              Active Companion Journey
            </h1>
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
              Mutually Connected
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Travelling together with verified companion <strong>{partnerName}</strong>.
          </p>
        </div>

        <button
          onClick={handleDisconnect}
          className="px-4 py-2 bg-rose-50 hover:bg-rose-100 border border-rose-300 text-rose-700 font-bold rounded-xl text-xs flex items-center gap-1.5 transition cursor-pointer"
        >
          <Ban className="w-3.5 h-3.5" />
          <span>Disconnect / End Sharing</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left: Shared Map (7 Cols) */}
        <div className="lg:col-span-7 bg-white p-5 rounded-3xl border border-slate-200/80 shadow-sm space-y-4">
          <MapView
            origin={{ name: "Agreed Public Meeting Hub", lat: 40.7580, lng: -73.9855 }}
            destination={{ name: "Campus Corridor", lat: 40.7681, lng: -73.9819 }}
            meetingPoints={[
              { name: "Well-Lit Transit Concourse (Agreed Meeting Point)", lat: 40.7580, lng: -73.9855, place_type: "transit_station" }
            ]}
            height="440px"
          />

          <div className="p-3 bg-amber-50 rounded-2xl border border-amber-200/60 flex items-center gap-2.5 text-xs text-amber-900">
            <Coffee className="w-4 h-4 text-amber-600 shrink-0" />
            <span><strong>Designated Meeting Spot:</strong> Times Square North Concourse (Well-Lit Security Checkpoint).</span>
          </div>
        </div>

        {/* Right: Companion Telemetry & Coordination (5 Cols) */}
        <div className="lg:col-span-5 space-y-5">
          
          {/* Partner Status Card */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-rose-500 to-indigo-500 text-white flex items-center justify-center font-bold text-lg shadow-md">
                {partnerName?.[0] || 'C'}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold text-slate-900">{partnerName}</h3>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.2 rounded-full font-bold flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3 text-emerald-600" /> Verified
                  </span>
                </div>
                <div className="text-xs text-slate-400">Coordinated Travel Partner</div>
              </div>
            </div>

            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Partner Safety Status:</span>
                <span className="font-bold text-emerald-700 flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  {partnerStatus}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Mutual Verification Code:</span>
                <span className="font-mono font-bold text-slate-800">SAFE-{requestId * 137}</span>
              </div>
            </div>

            {/* Check-in Status Quick Toggle */}
            <div className="space-y-2">
              <label className="block text-xs font-bold text-slate-700">Update Your Coordinated Status:</label>
              <div className="grid grid-cols-3 gap-2">
                {['En route', 'At Meeting Point', 'Walking Together'].map((statusOption) => (
                  <button
                    key={statusOption}
                    onClick={() => setMyCheckin(statusOption)}
                    className={`p-2 rounded-xl text-[11px] font-bold border transition cursor-pointer ${
                      myCheckin === statusOption
                        ? 'bg-rose-600 text-white border-rose-600 shadow-sm'
                        : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {statusOption}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Privacy & Safety Protocols */}
          <div className="bg-slate-900 text-slate-200 p-5 rounded-3xl border border-slate-800 shadow-lg text-xs space-y-3">
            <h4 className="font-bold text-white flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Safety Guidelines For Meeting Up:</span>
            </h4>
            <ul className="space-y-1.5 text-slate-400 text-[11px] list-disc list-inside">
              <li>Always meet at the designated public well-lit station or cafe.</li>
              <li>Confirm the 4-digit mutual code (SAFE-{requestId * 137}) verbally.</li>
              <li>You can disconnect or report at any time using the button above.</li>
              <li>Independent GPS route monitoring remains continuously active.</li>
            </ul>
          </div>

        </div>

      </div>
    </div>
  );
};

