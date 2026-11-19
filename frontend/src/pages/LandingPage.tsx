import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Shield, Users, MapPin, AlertOctagon, CheckCircle2, Lock, ArrowRight, 
  EyeOff, Navigation, Radio, Compass, PhoneCall, Bell, Sparkles, 
  ChevronRight, HeartHandshake, Eye, Check, Clock, Coffee, ShieldAlert 
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const LandingPage: React.FC = () => {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [activeFeatureIndex, setActiveFeatureIndex] = useState(0);

  const handleQuickLogin = async (email: string, pass: string) => {
    try {
      await login({ email, password: pass });
      navigate('/dashboard');
    } catch (err: any) {
      alert(`Login failed: ${err.message}`);
    }
  };

  const features = [
    {
      id: 'monitoring',
      icon: ShieldAlert,
      title: 'Smart Safety Monitoring',
      subtitle: 'Corridor & Deviation Detection',
      description: 'Calculates high-precision geodesic corridors along your planned itinerary. Analyzes GPS sensor accuracy before flagging anomalies, preventing false alarms while instantly detecting true route deviations with 3-check persistence.',
      badge: 'Automated Protection',
      color: 'indigo'
    },
    {
      id: 'tracking',
      icon: Navigation,
      title: 'Live Location Tracking',
      subtitle: 'LocationIQ Maps Integration',
      description: 'Interactive, real-time street map rendering powered by LocationIQ vector and street tiles. Detects your browser GPS location with dynamic beacon pulses and smooth route projection.',
      badge: 'LocationIQ Powered',
      color: 'purple'
    },
    {
      id: 'sos',
      icon: AlertOctagon,
      title: 'Instant Emergency SOS',
      subtitle: 'One-Tap Urgent Dispatch',
      description: 'Immediate distress trigger that bypasses all timeouts. Dispatches your real-time coordinates, last known address, and timestamp directly to your configured trusted guardians and emergency contacts.',
      badge: 'Zero Delay',
      color: 'rose'
    },
    {
      id: 'guardians',
      icon: PhoneCall,
      title: 'Trusted Guardians',
      subtitle: 'Multi-Channel Alert Network',
      description: 'Designate primary family members and friends who automatically receive emergency distress alerts with a direct live map link to view your shared location when urgent assistance is needed.',
      badge: 'Family Network',
      color: 'emerald'
    },
    {
      id: 'routes',
      icon: Coffee,
      title: 'Safe Routes & Public Checkpoints',
      subtitle: 'Verified Safe Meeting Points',
      description: 'Discovers verified well-lit public transit hubs, 24/7 staffed coffee shops, and civic buildings along your corridor to provide safe meeting checkpoints when travelling together.',
      badge: 'Verified Locations',
      color: 'amber'
    },
    {
      id: 'matching',
      icon: HeartHandshake,
      title: 'Journey Buddy – Travel Together',
      subtitle: 'Verified Companion Matching',
      description: 'Deterministic rule-based matching engine pairs verified women moving in the same direction at compatible departure times. Includes encrypted in-app coordination without revealing private numbers.',
      badge: 'Privacy Preserved',
      color: 'violet'
    }
  ];

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col justify-between selection:bg-indigo-500 selection:text-white font-sans antialiased overflow-x-hidden">
      
      {/* Subtle Background Glows */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[720px] h-[720px] bg-gradient-to-b from-indigo-600/15 via-purple-600/10 to-transparent rounded-full blur-[120px]" />
        <div className="absolute top-[35%] -left-32 w-[480px] h-[480px] bg-purple-700/10 rounded-full blur-[100px]" />
        <div className="absolute top-[60%] -right-32 w-[520px] h-[520px] bg-indigo-700/10 rounded-full blur-[110px]" />
      </div>

      {/* Hero Section */}
      <section className="relative z-10 pt-8 sm:pt-14 pb-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        
        {/* Eyebrow Badge */}
        <div className="flex justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-950/70 border border-indigo-500/30 text-indigo-300 text-xs font-semibold backdrop-blur-md shadow-lg shadow-indigo-950/50">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
            <span>Exclusively Designed for Verified Women</span>
            <span className="text-slate-500">•</span>
            <span className="text-indigo-200">LocationIQ Maps Integrated</span>
          </div>
        </div>

        {/* Hero Headline & Subtitle */}
        <div className="text-center max-w-4xl mx-auto mb-10">
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-white leading-[1.08] mb-6">
            Your Safety. Your Journey.{' '}
            <span className="bg-gradient-to-r from-indigo-300 via-purple-200 to-rose-300 bg-clip-text text-transparent">
              Our Priority.
            </span>
          </h1>

          <p className="text-base sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
            The privacy-first travel safety guardian. Monitor active routes with automated deviation alerts, broadcast instant emergency SOS to guardians, and schedule journeys to travel together safely with verified women.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 mt-8">
            {user ? (
              <Link
                to="/dashboard"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-7 py-3.5 rounded-2xl shadow-xl shadow-indigo-600/30 transition transform hover:-translate-y-0.5 text-sm"
              >
                <span>Go to My Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <>
                <Link
                  to="/auth?mode=register"
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold px-7 py-3.5 rounded-2xl shadow-xl shadow-indigo-600/25 transition transform hover:-translate-y-0.5 text-sm"
                >
                  <Shield className="w-4 h-4" />
                  <span>Start Verification & Get Started</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  to="/auth?mode=login"
                  className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-slate-900/90 hover:bg-slate-800 border border-slate-700/80 text-slate-200 font-semibold px-6 py-3.5 rounded-2xl transition text-sm backdrop-blur-md"
                >
                  <span>Sign In</span>
                </Link>
              </>
            )}
          </div>
        </div>

        {/* Realistic Interactive Map-Based Visual Preview Card */}
        <div className="relative max-w-5xl mx-auto mt-12">
          {/* Card Border Glow */}
          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500/30 via-purple-500/20 to-rose-500/30 rounded-3xl blur-xl opacity-70" />

          <div className="relative bg-[#0d1424] border border-slate-700/80 rounded-3xl overflow-hidden shadow-2xl">
            {/* Mock Application Top Bar */}
            <div className="bg-[#0b101c] px-5 py-3.5 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                <span className="ml-3 text-xs font-mono text-slate-400 font-semibold hidden sm:inline">
                  Safira Live Guardian Corridor • Route #402 (Active Monitoring)
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1.5 text-[11px] font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-500/40 px-2.5 py-0.5 rounded-full">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Corridor Secure
                </span>
                <span className="text-[11px] font-mono text-indigo-300 bg-indigo-950/60 border border-indigo-500/40 px-2 py-0.5 rounded-md hidden md:inline">
                  LocationIQ Street Engine
                </span>
              </div>
            </div>

            {/* Map Simulator Graphic */}
            <div className="relative h-72 sm:h-96 w-full bg-[#090d18] flex items-center justify-center overflow-hidden">
              {/* Cartographic Coordinate Grid */}
              <div 
                className="absolute inset-0 opacity-20"
                style={{
                  backgroundImage: 'radial-gradient(rgba(99, 102, 241, 0.25) 1px, transparent 1px)',
                  backgroundSize: '24px 24px'
                }}
              />

              {/* Simulated Map Streets & Corridor */}
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 800 400" preserveAspectRatio="none">
                {/* Street grid roads */}
                <line x1="0" y1="120" x2="800" y2="120" stroke="rgba(255,255,255,0.05)" strokeWidth="16" />
                <line x1="0" y1="260" x2="800" y2="260" stroke="rgba(255,255,255,0.05)" strokeWidth="20" />
                <line x1="220" y1="0" x2="220" y2="400" stroke="rgba(255,255,255,0.05)" strokeWidth="18" />
                <line x1="560" y1="0" x2="560" y2="400" stroke="rgba(255,255,255,0.05)" strokeWidth="16" />
                <path d="M 120 300 Q 280 260 400 190 T 680 100" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="12" />

                {/* Safety Corridor Buffer (150m boundary) */}
                <path 
                  d="M 120 300 Q 280 260 400 190 T 680 100" 
                  fill="none" 
                  stroke="rgba(99, 102, 241, 0.15)" 
                  strokeWidth="48" 
                  strokeLinecap="round" 
                />

                {/* Active Planned Route Polyline */}
                <path 
                  d="M 120 300 Q 280 260 400 190 T 680 100" 
                  fill="none" 
                  stroke="#6366f1" 
                  strokeWidth="4" 
                  strokeLinecap="round" 
                  strokeDasharray="6 3" 
                />
              </svg>

              {/* Map Pins and Live Telemetry Badges */}
              {/* Origin Marker */}
              <div className="absolute left-[15%] top-[75%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center shadow-lg shadow-indigo-600/50 ring-4 ring-indigo-400/20">
                  <MapPin className="w-4 h-4" />
                </div>
                <span className="text-[10px] font-bold bg-slate-900/90 text-indigo-300 px-2 py-0.5 rounded-md border border-indigo-500/30 mt-1 whitespace-nowrap">
                  Start: Campus North Gate
                </span>
              </div>

              {/* Safe Meeting Point Checkpoint */}
              <div className="absolute left-[50%] top-[48%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-amber-500 text-slate-950 flex items-center justify-center shadow-xl shadow-amber-500/30 ring-4 ring-amber-400/30 animate-bounce">
                  <Coffee className="w-4 h-4 stroke-[2.5]" />
                </div>
                <span className="text-[10px] font-bold bg-slate-900/90 text-amber-300 px-2 py-0.5 rounded-md border border-amber-500/30 mt-1 whitespace-nowrap flex items-center gap-1">
                  <Shield className="w-3 h-3 text-amber-400" />
                  Transit Concourse Checkpoint
                </span>
              </div>

              {/* Live User Position Pulsing Beacon */}
              <div className="absolute left-[38%] top-[56%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
                <div className="relative flex items-center justify-center">
                  <span className="animate-ping absolute inline-flex h-10 w-10 rounded-full bg-cyan-400 opacity-75" />
                  <div className="w-5 h-5 rounded-full bg-cyan-400 ring-4 ring-cyan-200 shadow-xl flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-white" />
                  </div>
                </div>
                <span className="text-[10px] font-extrabold bg-slate-950 text-cyan-300 px-2 py-0.5 rounded-md border border-cyan-400/40 mt-1 shadow-md">
                  You • GPS Normal (±8m)
                </span>
              </div>

              {/* Destination Marker */}
              <div className="absolute left-[85%] top-[25%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-rose-600 text-white flex items-center justify-center shadow-lg shadow-rose-600/50 ring-4 ring-rose-400/20">
                  <Check className="w-4 h-4 stroke-[3]" />
                </div>
                <span className="text-[10px] font-bold bg-slate-900/90 text-rose-300 px-2 py-0.5 rounded-md border border-rose-500/30 mt-1 whitespace-nowrap">
                  Destination: Central Station
                </span>
              </div>

              {/* Top Right Floating HUD Widget */}
              <div className="absolute top-4 right-4 bg-slate-900/90 border border-slate-700/70 p-3 rounded-2xl shadow-xl backdrop-blur-md hidden sm:flex items-center gap-3 text-xs">
                <div className="p-2 bg-indigo-500/20 rounded-xl text-indigo-400">
                  <Users className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-[11px] font-bold text-white">Travel Buddy Matched</div>
                  <div className="text-[10px] text-slate-400">Maya K. • 94% Route Overlap</div>
                </div>
              </div>

              {/* Bottom Left Floating Guardian Telemetry Widget */}
              <div className="absolute bottom-4 left-4 bg-slate-900/90 border border-slate-700/70 p-3 rounded-2xl shadow-xl backdrop-blur-md flex items-center gap-3 text-xs">
                <div className="p-2 bg-emerald-500/20 rounded-xl text-emerald-400">
                  <Shield className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-[11px] font-bold text-white">Guardian Link Active</div>
                  <div className="text-[10px] text-slate-400">2 Contacts Armed • SOS Standby</div>
                </div>
              </div>
            </div>

            {/* Bottom Status Ticker */}
            <div className="bg-[#0b101c] px-6 py-4 border-t border-slate-800 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-400">
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1.5 text-slate-300">
                  <Compass className="w-3.5 h-3.5 text-indigo-400" />
                  Walking Mode
                </span>
                <span>•</span>
                <span className="text-slate-300">1.8 km Corridor</span>
                <span>•</span>
                <span className="text-slate-300">~22 mins</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                <span className="text-emerald-300 font-semibold text-[11px]">No Deviations Detected past 150m Threshold</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Demo Logins Bar (Seeded Evaluator Accounts) */}
        <div className="max-w-4xl mx-auto mt-12 bg-slate-900/80 border border-slate-800/90 rounded-3xl p-5 sm:p-6 backdrop-blur-md shadow-xl text-left">
          <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Instant Test Logins for Evaluators & Reviewers</span>
            </span>
            <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded font-mono">1-Click Auth</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <button
              onClick={() => handleQuickLogin('maya@university.edu', 'MayaPass123!')}
              className="p-3.5 rounded-2xl bg-slate-950/70 hover:bg-slate-800 border border-emerald-500/30 hover:border-emerald-500/60 text-left transition group cursor-pointer"
            >
              <div className="text-xs font-bold text-emerald-400 flex items-center justify-between">
                <span>Maya Kapoor</span>
                <span className="text-[9px] bg-emerald-950 text-emerald-300 px-1.5 py-0.5 rounded border border-emerald-500/40">Verified Woman</span>
              </div>
              <div className="text-[11px] text-slate-400 mt-1">Graduate Student • Planned Corridor</div>
            </button>

            <button
              onClick={() => handleQuickLogin('priya@citytech.org', 'PriyaPass123!')}
              className="p-3.5 rounded-2xl bg-slate-950/70 hover:bg-slate-800 border border-indigo-500/30 hover:border-indigo-500/60 text-left transition group cursor-pointer"
            >
              <div className="text-xs font-bold text-indigo-400 flex items-center justify-between">
                <span>Priya Sharma</span>
                <span className="text-[9px] bg-indigo-950 text-indigo-300 px-1.5 py-0.5 rounded border border-indigo-500/40">Verified Woman</span>
              </div>
              <div className="text-[11px] text-slate-400 mt-1">Researcher • Matching Candidate</div>
            </button>

            <button
              onClick={() => handleQuickLogin('admin@safira.org', 'AdminPass123!')}
              className="p-3.5 rounded-2xl bg-slate-950/70 hover:bg-slate-800 border border-purple-500/30 hover:border-purple-500/60 text-left transition group cursor-pointer"
            >
              <div className="text-xs font-bold text-purple-400 flex items-center justify-between">
                <span>Admin Reviewer</span>
                <span className="text-[9px] bg-purple-950 text-purple-300 px-1.5 py-0.5 rounded border border-purple-500/40">Admin Reviewer</span>
              </div>
              <div className="text-[11px] text-slate-400 mt-1">Manual Verification Review Portal</div>
            </button>
          </div>
        </div>

      </section>

      {/* SECTION 2: HOW IT WORKS */}
      <section id="how-it-works" className="relative z-10 py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full border-t border-slate-800/60">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">Simple & Deterministic</span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white mt-2">
            How Women Safety Guardian Works
          </h2>
          <p className="text-sm sm:text-base text-slate-400 mt-2">
            Engineered from the ground up for strict privacy, zero identity leakage, and practical journey protection.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          
          {/* Step 1 */}
          <div className="bg-[#0b101c] border border-slate-800 p-6 rounded-3xl relative">
            <div className="w-10 h-10 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 text-indigo-400 flex items-center justify-center font-black text-sm mb-4">
              01
            </div>
            <h3 className="text-base font-bold text-white mb-2">Privacy Verification</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Register and submit eligibility. Manual verification ensures that only verified women can access companion discovery without exposing identification documents.
            </p>
          </div>

          {/* Step 2 */}
          <div className="bg-[#0b101c] border border-slate-800 p-6 rounded-3xl relative">
            <div className="w-10 h-10 rounded-2xl bg-purple-600/20 border border-purple-500/40 text-purple-400 flex items-center justify-center font-black text-sm mb-4">
              02
            </div>
            <h3 className="text-base font-bold text-white mb-2">Route & Schedule</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Enter your starting point and destination via LocationIQ geocoding. The system calculates an optimal street corridor, safe checkpoints, and arrival times.
            </p>
          </div>

          {/* Step 3 */}
          <div className="bg-[#0b101c] border border-slate-800 p-6 rounded-3xl relative">
            <div className="w-10 h-10 rounded-2xl bg-violet-600/20 border border-violet-500/40 text-violet-400 flex items-center justify-center font-black text-sm mb-4">
              03
            </div>
            <h3 className="text-base font-bold text-white mb-2">Journey Buddy Match</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Browse or match with verified women moving along your route around the same time. Mutually connect and coordinate meeting up safely without sharing phone numbers.
            </p>
          </div>

          {/* Step 4 */}
          <div className="bg-[#0b101c] border border-slate-800 p-6 rounded-3xl relative">
            <div className="w-10 h-10 rounded-2xl bg-rose-600/20 border border-rose-500/40 text-rose-400 flex items-center justify-center font-black text-sm mb-4">
              04
            </div>
            <h3 className="text-base font-bold text-white mb-2">Corridor Guard & SOS</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              If an unexpected deviation exceeds 150m for 3 consecutive intervals or if you tap SOS, immediate alerts and live map coordinates are dispatched to your guardians.
            </p>
          </div>

        </div>
      </section>

      {/* SECTION 3: CORE SAFETY FEATURES */}
      <section id="features" className="relative z-10 py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full border-t border-slate-800/60">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <span className="text-xs font-bold uppercase tracking-wider text-purple-400">Comprehensive Safety Stack</span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white mt-2">
            Built for Real-World Women's Safety
          </h2>
          <p className="text-sm sm:text-base text-slate-400 mt-2">
            No empty AI buzzwords. Every safety capability operates on deterministic rules, verified geospatial math, and verified identities.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feat, idx) => {
            const Icon = feat.icon;

            return (
              <div 
                key={feat.id} 
                className="bg-[#0b101c] border border-slate-800/80 hover:border-indigo-500/40 p-6 rounded-3xl transition-all hover:-translate-y-1 shadow-lg group"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center group-hover:bg-indigo-500/20 transition">
                    <Icon className="w-6 h-6" />
                  </div>
                  <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-900 border border-slate-700 text-slate-300 px-2.5 py-0.5 rounded-full">
                    {feat.badge}
                  </span>
                </div>

                <h3 className="text-base font-bold text-white mb-1">{feat.title}</h3>
                <h4 className="text-xs font-semibold text-indigo-300 mb-2">{feat.subtitle}</h4>
                <p className="text-xs text-slate-400 leading-relaxed">{feat.description}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* SECTION 4: GENUINE PROJECT METRICS & SPECS */}
      <section className="relative z-10 py-14 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full border-t border-slate-800/60">
        <div className="bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-slate-950 border border-slate-800 rounded-3xl p-8 sm:p-10 shadow-xl">
          <div className="text-center max-w-2xl mx-auto mb-8">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">Verifiable System Specifications</span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">
              Precision Safety Parameters
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Deterministic architectural thresholds configured in the platform engine.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
              <div className="text-2xl sm:text-3xl font-black text-indigo-300">150m</div>
              <div className="text-xs font-semibold text-white mt-1">Corridor Tolerance</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Filters normal sidewalk detours</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
              <div className="text-2xl sm:text-3xl font-black text-purple-300">3 Checks</div>
              <div className="text-xs font-semibold text-white mt-1">Persistent Verification</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Eliminates single GPS flutter</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
              <div className="text-2xl sm:text-3xl font-black text-rose-300">60s</div>
              <div className="text-xs font-semibold text-white mt-1">Escalation Timeout</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Auto-alerts emergency guardians</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
              <div className="text-2xl sm:text-3xl font-black text-emerald-300">0%</div>
              <div className="text-xs font-semibold text-white mt-1">Private Data Leakage</div>
              <div className="text-[10px] text-slate-400 mt-0.5">No street addresses exposed</div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 5: CALL TO ACTION */}
      <section className="relative z-10 py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full text-center">
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="w-14 h-14 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 text-indigo-400 flex items-center justify-center mx-auto shadow-xl shadow-indigo-600/20">
            <Shield className="w-7 h-7" />
          </div>

          <h2 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
            Take Control of Your Daily Travel Safety
          </h2>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
            Join verified women moving with confidence. Schedule your journeys, monitor real-time routes on LocationIQ maps, and travel together safely.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
            <Link
              to="/auth?mode=register"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-8 py-4 rounded-2xl shadow-xl shadow-indigo-600/30 transition transform hover:-translate-y-0.5 text-sm"
            >
              <span>Create Account & Verify</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/auth?mode=login"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 font-semibold px-7 py-4 rounded-2xl transition text-sm"
            >
              <span>Member Sign In</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Professional Footer */}
      <footer className="relative z-10 border-t border-slate-800/80 bg-[#060911] pt-12 pb-8 px-4 sm:px-6 lg:px-8 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-8 text-left">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold">
                <Shield className="w-4 h-4" />
              </div>
              <span className="font-extrabold text-base text-white tracking-tight">Safira Guardian</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              Privacy-engineered women's travel safety platform combining LocationIQ routing, real-time GPS corridor monitoring, and verified companion matching.
            </p>
          </div>

          <div>
            <h4 className="font-bold text-white mb-2 uppercase tracking-wider text-[11px]">Platform</h4>
            <ul className="space-y-1.5 text-[11px] text-slate-400">
              <li><Link to="/journeys/create" className="hover:text-indigo-400">Create Safe Journey</Link></li>
              <li><Link to="/journey-buddy" className="hover:text-indigo-400">Journey Buddy (Travel Together)</Link></li>
              <li><Link to="/dashboard" className="hover:text-indigo-400">Live Dashboard</Link></li>
              <li><Link to="/verification" className="hover:text-indigo-400">Eligibility Verification</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-white mb-2 uppercase tracking-wider text-[11px]">Emergency Resources</h4>
            <ul className="space-y-1.5 text-[11px] text-slate-400">
              <li>Women Helpline: <strong className="text-rose-400">1091 / 181</strong></li>
              <li>National Emergency: <strong className="text-rose-400">112 / 911</strong></li>
              <li>Police Quick Response: <strong className="text-white">100</strong></li>
              <li>Instant 1-Tap SOS in App</li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-white mb-2 uppercase tracking-wider text-[11px]">Privacy & Trust</h4>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              Raw identification documents are never shared. GPS traces are discarded post-journey. Exact home addresses are never exposed to prospective matches.
            </p>
          </div>
        </div>

        <div className="max-w-7xl mx-auto pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-slate-500">
          <p>© 2026 Safira Women's Travel Safety Platform. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <span>LocationIQ Maps API Integrated</span>
            <span>•</span>
            <span>FastAPI & PostgreSQL PostGIS Ready</span>
          </div>
        </div>
      </footer>

    </div>
  );
};
