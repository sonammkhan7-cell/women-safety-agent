import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, XCircle, CheckCircle2, Clock, UserCheck, AlertCircle } from 'lucide-react';

export const AdminVerificationPage: React.FC = () => {
  const { isAdmin } = useAuth();
  const [verifications, setVerifications] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [reviewingId, setReviewingId] = useState<number | null>(null);
  const [reviewNotes, setReviewNotes] = useState<string>('');
  const [msg, setMsg] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const fetchVerifications = async () => {
    try {
      const data = await api.getAdminVerifications();
      setVerifications(data);
    } catch (e: any) {
      setMsg({ text: e.message || 'Failed to fetch verifications.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      fetchVerifications();
    }
  }, [isAdmin]);

  const handleReview = async (id: number, status: 'verified' | 'rejected') => {
    setReviewingId(id);
    setMsg(null);
    try {
      await api.reviewVerification(id, {
        status,
        reviewer_notes: reviewNotes.trim() || `Marked ${status} by Administrator.`
      });
      setMsg({ text: `Application successfully marked as ${status.toUpperCase()}.`, type: 'success' });
      setReviewNotes('');
      await fetchVerifications();
    } catch (err: any) {
      setMsg({ text: err.message || 'Review failed.', type: 'error' });
    } finally {
      setReviewingId(null);
    }
  };

  if (!isAdmin) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center text-slate-700">
        <ShieldCheck className="w-12 h-12 text-slate-400 mx-auto mb-3" />
        <h2 className="text-xl font-bold">Admin Privileges Required</h2>
        <p className="text-sm text-slate-500 mt-1">Please sign in as an administrator to review eligibility.</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Manual Affiliation Review</h1>
        <p className="text-xs text-slate-500 mt-1">
          Check each stated affiliation or referral through an official institution or community channel before approval. Approval does not certify gender, character, or guarantee safety.
        </p>
      </div>

      {msg && (
        <div className={`mb-6 p-4 rounded-2xl text-xs flex items-center gap-2 ${
          msg.type === 'success' 
            ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' 
            : 'bg-rose-50 text-rose-800 border border-rose-200'
        }`}>
          {msg.type === 'success' ? <CheckCircle2 className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
          <span>{msg.text}</span>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12 text-slate-400 text-sm">Loading applications...</div>
      ) : verifications.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 text-slate-500">
          <UserCheck className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="font-semibold">No applications found.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {verifications.map((item) => (
            <div key={item.id} className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-xs ${
                    item.status === 'verified'
                      ? 'bg-emerald-100 text-emerald-700'
                      : item.status === 'pending'
                      ? 'bg-amber-100 text-amber-700'
                      : 'bg-rose-100 text-rose-700'
                  }`}>
                    #{item.id}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-900 text-sm">{item.user_name}</span>
                      <span className="font-mono text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                        {item.verification_reference}
                      </span>
                    </div>
                    <span className="text-[11px] text-slate-400 capitalize">
                      {item.user_email} • {item.document_type?.replace('_', ' ')} • Submitted on {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <span className={`text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider self-start sm:self-center ${
                  item.status === 'verified'
                    ? 'bg-emerald-100 text-emerald-800'
                    : item.status === 'pending'
                    ? 'bg-amber-100 text-amber-800'
                    : 'bg-rose-100 text-rose-800'
                }`}>
                  {item.status}
                </span>
              </div>

              {/* Data Details */}
              <div className="bg-slate-50 p-4 rounded-2xl text-xs space-y-2 mb-4">
                <div>
                  <strong className="text-slate-600">Masked Identifier:</strong>{' '}
                  <span className="font-mono text-slate-900 font-bold">{item.masked_identifier}</span>
                </div>
                {item.submission_notes && (
                  <div>
                    <strong className="text-slate-600">Applicant Notes:</strong>{' '}
                    <span className="text-slate-800">{item.submission_notes}</span>
                  </div>
                )}
                {item.reviewer_notes && (
                  <div>
                    <strong className="text-slate-600">Previous Reviewer Notes:</strong>{' '}
                    <span className="text-slate-700 italic">{item.reviewer_notes}</span>
                  </div>
                )}
              </div>

              {/* Review Actions */}
              <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
                <input
                  type="text"
                  placeholder="Record the official affiliation source checked and outcome..."
                  value={reviewNotes}
                  onChange={e => setReviewNotes(e.target.value)}
                  className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:border-rose-500 w-full"
                />
                <div className="flex items-center gap-2 w-full sm:w-auto">
                  <button
                    onClick={() => handleReview(item.id, 'verified')}
                    disabled={reviewingId === item.id}
                    className="flex-1 sm:flex-none px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Approve</span>
                  </button>

                  <button
                    onClick={() => handleReview(item.id, 'rejected')}
                    disabled={reviewingId === item.id}
                    className="flex-1 sm:flex-none px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    <span>Reject</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

