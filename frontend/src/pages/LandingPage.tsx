import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Users, MapPin, AlertOctagon, CheckCircle2, Lock, ArrowRight, EyeOff } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const LandingPage: React.FC = () => {
  const { user, login } = useAuth();
  const navigate = useNavigate();

  const handleQuickLogin = async (email: string, pass: string) => {
    try {
      await login({ email, password: pass });
      navigate('/dashboard');
    } catch (err: any) {
      alert(`Login failed: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-rose-500 selection:text-white">
      {/* Hero Section */}
      <div className="relative overflow-hidden pt-12 pb-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        {/* Glow Effects */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-rose-600/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-1/3 right-1/4 w-80 h-80 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />

        <div className="text-center relative z-10 max-w-3xl mx-auto">
          {/* Eyebrow badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs font-semibold uppercase tracking-wider mb-6">
            <Shield className="w-3.5 h-3.5 text-rose-400" />
            <span>Exclusively for Verified Women</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">
            Safe Journeys.<br />
            <span className="bg-gradient-to-r from-rose-400 via-purple-300 to-indigo-400 bg-clip-text text-transparent">
              Trusted Companions.
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-300 mb-8 leading-relaxed">
            Monitor your travel routes in real-time, get alerted on persistent unexpected deviations, and voluntarily connect with verified women travelling along compatible corridors.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-14">
            {user ? (
              <Link
                to="/dashboard"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-rose-600 hover:bg-rose-500 text-white font-bold px-6 py-3.5 rounded-xl shadow-lg shadow-rose-600/30 transition transform hover:-translate-y-0.5"
              >
                <span>Go to Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <>
                <Link
                  to="/auth?mode=register"
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-rose-600 hover:bg-rose-500 text-white font-bold px-6 py-3.5 rounded-xl shadow-lg shadow-rose-600/30 transition transform hover:-translate-y-0.5"
                >
                  <span>Start Verification & Sign Up</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  to="/auth?mode=login"
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 font-semibold px-6 py-3.5 rounded-xl transition"
                >
                  <span>Sign In</span>
                </Link>
              </>
            )}
          </div>

          {/* Quick Demo Logins Bar for Testing / MVP Evaluation */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 backdrop-blur-md shadow-xl text-left">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Instant Test Logins (Development Data Seeded)</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
              <button
                onClick={() => handleQuickLogin('maya@university.edu', 'MayaPass123!')}
                className="p-3 rounded-xl bg-slate-950/70 hover:bg-slate-800 border border-emerald-500/30 hover:border-emerald-500/60 text-left transition group cursor-pointer"
              >
                <div className="text-xs font-bold text-emerald-400 flex items-center justify-between">
                  <span>Maya Kapoor</span>
                  <span className="text-[10px] bg-emerald-950 px-1.5 py-0.5 rounded border border-emerald-500/40">Verified</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Graduate Student • Active Corridor</div>
              </button>

              <button
                onClick={() => handleQuickLogin('priya@citytech.org', 'PriyaPass123!')}
                className="p-3 rounded-xl bg-slate-950/70 hover:bg-slate-800 border border-indigo-500/30 hover:border-indigo-500/60 text-left transition group cursor-pointer"
              >
                <div className="text-xs font-bold text-indigo-400 flex items-center justify-between">
                  <span>Priya Sharma</span>
                  <span className="text-[10px] bg-indigo-950 px-1.5 py-0.5 rounded border border-indigo-500/40">Verified</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Researcher • Compatible Match</div>
              </button>

              <button
                onClick={() => handleQuickLogin('admin@safira.org', 'AdminPass123!')}
                className="p-3 rounded-xl bg-slate-950/70 hover:bg-slate-800 border border-purple-500/30 hover:border-purple-500/60 text-left transition group cursor-pointer"
              >
                <div className="text-xs font-bold text-purple-400 flex items-center justify-between">
                  <span>Admin Reviewer</span>
                  <span className="text-[10px] bg-purple-950 px-1.5 py-0.5 rounded border border-purple-500/40">Admin</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-1">Verification Reviewer Portal</div>
              </button>
            </div>
          </div>
        </div>

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
          <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
            <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center mb-4">
              <MapPin className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white mb-2">Smart Route Deviation Detection</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Considers GPS accuracy before flagging anomalies. Detects persistent route deviations with automated check-in and escalating timeouts to trusted contacts.
            </p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mb-4">
              <Users className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white mb-2">Deterministic Companion Matching</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Finds verified women with compatible route overlaps, similar departure times, and safe public meeting spots. Mutual request acceptance required.
            </p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4">
              <EyeOff className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white mb-2">Privacy-First Architecture</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              No home addresses or exact live GPS coordinates are ever exposed to potential matches. Only coarse approximate corridors until mutual consent.
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-6 px-4 text-center text-xs text-slate-500">
        <p>Safira Women's Travel Safety & Companion Matching • Built with privacy, dignity, and deterministic safety algorithms.</p>
      </footer>
    </div>
  );
};

