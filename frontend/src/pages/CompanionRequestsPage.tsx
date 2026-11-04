import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { 
  Users, Check, X, Shield, Clock, ArrowRight, MessageSquare, AlertCircle, Ban 
} from 'lucide-react';

export const CompanionRequestsPage: React.FC = () => {
  const { user } = useAuth();
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [tab, setTab] = useState<'incoming' | 'outgoing'>('incoming');

  const fetchRequests = async () => {
    try {
      const data = await api.getMyRequests();
      setRequests(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleUpdateStatus = async (requestId: number, status: string) => {
    setActionLoading(requestId);
    try {
      await api.updateRequestStatus(requestId, status);
      await fetchRequests();
    } catch (err: any) {
      alert(`Error updating request: ${err.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  const incomingRequests = requests.filter(r => r.receiver_id === user?.id);
  const outgoingRequests = requests.filter(r => r.sender_id === user?.id);
  const displayedRequests = tab === 'incoming' ? incomingRequests : outgoingRequests;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Companion Matching Requests
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Review incoming companion invitations and manage your travel partner connections.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex p-1 bg-slate-200/80 rounded-2xl max-w-sm">
        <button
          onClick={() => setTab('incoming')}
          className={`flex-1 py-2 text-xs font-bold rounded-xl transition cursor-pointer flex items-center justify-center gap-1.5 ${
            tab === 'incoming' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <span>Incoming</span>
          {incomingRequests.filter(r => r.status === 'pending').length > 0 && (
            <span className="w-2 h-2 rounded-full bg-rose-500 inline-block" />
          )}
        </button>

        <button
          onClick={() => setTab('outgoing')}
          className={`flex-1 py-2 text-xs font-bold rounded-xl transition cursor-pointer ${
            tab === 'outgoing' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <span>Sent Requests</span>
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400 text-sm">Loading companion requests...</div>
      ) : displayedRequests.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 text-slate-500 space-y-2">
          <Users className="w-10 h-10 text-slate-300 mx-auto" />
          <p className="font-semibold text-sm">No {tab} requests found.</p>
          <p className="text-xs text-slate-400">
            {tab === 'incoming' 
              ? 'When other verified women find your journey corridor, requests will appear here.'
              : 'You haven’t sent any companion requests yet.'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {displayedRequests.map((req) => (
            <div key={req.id} className="bg-white rounded-3xl border border-slate-200/80 p-5 shadow-sm space-y-4">
              
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-rose-500 to-indigo-500 text-white flex items-center justify-center font-bold text-sm shadow-md">
                    {(tab === 'incoming' ? req.sender_name : req.receiver_name)?.[0] || 'U'}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-bold text-slate-900">
                        {tab === 'incoming' ? req.sender_name : req.receiver_name}
                      </h4>
                      <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.2 rounded-full font-bold">
                        Verified Woman
                      </span>
                    </div>
                    <span className="text-[11px] text-slate-400">
                      Request #{req.id} • Sent on {new Date(req.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <span className={`text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider self-start sm:self-center ${
                  req.status === 'accepted' ? 'bg-emerald-100 text-emerald-800' :
                  req.status === 'rejected' ? 'bg-rose-100 text-rose-800' :
                  req.status === 'cancelled' ? 'bg-slate-100 text-slate-600' :
                  'bg-amber-100 text-amber-800'
                }`}>
                  {req.status}
                </span>
              </div>

              {/* Message Note */}
              {req.initial_message && (
                <div className="bg-slate-50 p-3 rounded-2xl border border-slate-100 text-xs text-slate-700 flex items-start gap-2">
                  <MessageSquare className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                  <span>"{req.initial_message}"</span>
                </div>
              )}

              {/* Action Buttons */}
              <div className="pt-2 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100">
                
                {/* When Accepted: Link to Shared Journey Room */}
                {req.status === 'accepted' ? (
                  <div className="flex items-center justify-between w-full">
                    <span className="text-xs text-emerald-700 font-semibold flex items-center gap-1.5">
                      <Shield className="w-4 h-4 text-emerald-600" /> Mutual connection active
                    </span>
                    <div className="flex items-center gap-2">
                      <Link
                        to={`/companion-journey/${req.id}`}
                        className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow"
                      >
                        <span>Open Shared Journey</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                      <button
                        onClick={() => handleUpdateStatus(req.id, 'cancelled')}
                        disabled={actionLoading === req.id}
                        className="px-3 py-2 text-slate-400 hover:text-rose-600 text-xs font-semibold cursor-pointer"
                      >
                        Disconnect
                      </button>
                    </div>
                  </div>
                ) : req.status === 'pending' ? (
                  tab === 'incoming' ? (
                    <div className="flex items-center gap-2 w-full sm:w-auto ml-auto">
                      <button
                        onClick={() => handleUpdateStatus(req.id, 'accepted')}
                        disabled={actionLoading === req.id}
                        className="flex-1 sm:flex-none px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-1.5 shadow cursor-pointer"
                      >
                        <Check className="w-4 h-4" />
                        <span>Accept Companion</span>
                      </button>

                      <button
                        onClick={() => handleUpdateStatus(req.id, 'rejected')}
                        disabled={actionLoading === req.id}
                        className="flex-1 sm:flex-none px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs flex items-center justify-center gap-1 cursor-pointer"
                      >
                        <X className="w-3.5 h-3.5" />
                        <span>Decline</span>
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between w-full">
                      <span className="text-xs text-slate-400 italic">Awaiting response from companion...</span>
                      <button
                        onClick={() => handleUpdateStatus(req.id, 'cancelled')}
                        disabled={actionLoading === req.id}
                        className="px-3 py-1.5 text-rose-600 hover:bg-rose-50 rounded-xl text-xs font-semibold cursor-pointer border border-rose-200"
                      >
                        Cancel Request
                      </button>
                    </div>
                  )
                ) : (
                  <span className="text-xs text-slate-400 italic">This connection was {req.status}.</span>
                )}
              </div>

            </div>
          ))}
        </div>
      )}
    </div>
  );
};

