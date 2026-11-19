import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import { 
  ShieldCheck, Clock, XCircle, FileBadge, Lock, AlertCircle, CheckCircle2, ArrowRight 
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const VerificationPage: React.FC = () => {
  const { user, refreshProfile } = useAuth();
  const [verification, setVerification] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const [documentType, setDocumentType] = useState('student_id');
  const [maskedIdentifier, setMaskedIdentifier] = useState('');
  const [submissionNotes, setSubmissionNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const loadVerification = async () => {
    try {
      const data = await api.getVerificationStatus();
      setVerification(data);
    } catch (e) {
      setVerification(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVerification();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      const data = await api.submitVerification({
        document_type: documentType,
        masked_identifier: maskedIdentifier.trim(),
        submission_notes: submissionNotes.trim() || undefined
      });
      setVerification(data);
      setSuccessMsg("Verification submitted successfully! Our manual review team will process your eligibility.");
      await refreshProfile();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to submit verification.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Title */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Eligibility Verification</h1>
        <p className="text-sm text-slate-500 mt-1">
          A human reviewer checks your stated institution or community affiliation before companion matching is enabled. This review does not certify gender, character, or personal safety.
        </p>
      </div>

      {/* Current Status Banner */}
      <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm mb-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            {user?.verification_status === 'verified' ? (
              <div className="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0">
                <ShieldCheck className="w-8 h-8" />
              </div>
            ) : user?.verification_status === 'pending' ? (
              <div className="w-14 h-14 rounded-2xl bg-amber-100 text-amber-600 flex items-center justify-center shrink-0">
                <Clock className="w-8 h-8" />
              </div>
            ) : (
              <div className="w-14 h-14 rounded-2xl bg-rose-100 text-rose-600 flex items-center justify-center shrink-0">
                <XCircle className="w-8 h-8" />
              </div>
            )}
            
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-slate-900">Current Verification Status</h2>
                <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider ${
                  user?.verification_status === 'verified'
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                    : user?.verification_status === 'pending'
                    ? 'bg-amber-100 text-amber-800 border border-amber-300'
                    : 'bg-rose-100 text-rose-800 border border-rose-300'
                }`}>
                  {user?.verification_status || 'Pending'}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {user?.verification_status === 'verified'
                  ? 'Your account is fully verified. You have full access to Travel Companion Matching.'
                  : user?.verification_status === 'pending'
                  ? 'Your submission is queued for manual review. Companion matching will unlock upon approval.'
                  : 'Eligibility verification requires a valid submission or resubmission.'}
              </p>
            </div>
          </div>

          {user?.verification_status === 'verified' && (
            <Link
              to="/journeys/create"
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-sm"
            >
              <span>Create Journey</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          )}
        </div>

        {verification && (
          <div className="mt-6 pt-5 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="bg-slate-50 p-3 rounded-xl">
              <span className="text-slate-400 block font-medium">Reference Code</span>
              <span className="font-mono font-bold text-slate-800">{verification.verification_reference || 'N/A'}</span>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl">
              <span className="text-slate-400 block font-medium">Document Proof Type</span>
              <span className="font-semibold text-slate-800 capitalize">{verification.document_type?.replace('_', ' ')}</span>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl">
              <span className="text-slate-400 block font-medium">Masked Identifier</span>
              <span className="font-mono text-slate-800">{verification.masked_identifier || 'Masked'}</span>
            </div>
          </div>
        )}
      </div>

      {/* Submission Form */}
      {user?.verification_status !== 'verified' && (
        <div className="bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <FileBadge className="w-5 h-5 text-rose-600" />
            <h3 className="text-base font-bold text-slate-900">
              {verification ? 'Update / Resubmit Verification' : 'Submit Eligibility Proof'}
            </h3>
          </div>
          <p className="text-xs text-slate-500 mb-6">
            Provide an affiliation or referral reference that a reviewer can check through an official institution or community channel. Do not submit full ID numbers or document photos.
          </p>

          {successMsg && (
            <div className="mb-6 p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {errorMsg && (
            <div className="mb-6 p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">Verification Method</label>
              <select
                value={documentType}
                onChange={e => setDocumentType(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 focus:outline-none focus:border-rose-500"
              >
                <option value="student_id">Student ID (University / College)</option>
                <option value="institutional_email">Institutional / Corporate Affiliate Reference</option>
                <option value="government_id">Government ID Masked Reference</option>
                <option value="community_referral">Verified Community / Club Referral</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">
                Masked Identifier / Reference Token
              </label>
              <input
                type="text"
                required
                placeholder="e.g. STU-***-4821 or REF-WOMEN-TECH-892"
                value={maskedIdentifier}
                onChange={e => setMaskedIdentifier(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 focus:outline-none focus:border-rose-500"
              />
              <span className="text-[11px] text-slate-400 mt-1 block">
                Never submit full unmasked numbers. Example: Only provide the last 4 digits (STU-***-1234).
              </span>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">
                Verification Details & Context (Optional)
              </label>
              <textarea
                rows={3}
                placeholder="Organization or community name, your affiliation, and a reference the reviewer can check..."
                value={submissionNotes}
                onChange={e => setSubmissionNotes(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 focus:outline-none focus:border-rose-500"
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3 bg-rose-600 hover:bg-rose-700 text-white font-bold rounded-xl text-sm shadow-md shadow-rose-600/20 transition cursor-pointer disabled:opacity-50"
              >
                {submitting ? 'Submitting...' : 'Submit Verification for Review'}
              </button>
            </div>
          </form>

          {/* Privacy Security Box */}
          <div className="mt-8 p-4 rounded-2xl bg-indigo-50/60 border border-indigo-100 flex items-start gap-3 text-xs text-indigo-950">
            <Lock className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
            <div>
              <strong className="block font-semibold">Privacy Safeguards:</strong>
              Reviewers should verify affiliation through official channels and record what they checked. Approval confirms eligibility under the review policy; it does not prove gender, character, or guarantee safety.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

