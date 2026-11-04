import React, { useState, useEffect } from 'react';
import { AlertTriangle, ShieldCheck, RefreshCw, PhoneCall, Clock } from 'lucide-react';
import { api } from '../api/client';

interface DeviationModalProps {
  journeyId: number;
  isOpen: boolean;
  deviationDistance: number;
  timeoutSeconds?: number;
  onResolved: (action: string) => void;
}

export const DeviationModal: React.FC<DeviationModalProps> = ({
  journeyId,
  isOpen,
  deviationDistance,
  timeoutSeconds = 60,
  onResolved
}) => {
  const [secondsRemaining, setSecondsRemaining] = useState(timeoutSeconds);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setSecondsRemaining(timeoutSeconds);
      return;
    }

    const timer = setInterval(() => {
      setSecondsRemaining(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          handleTimeoutEscalation();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isOpen, timeoutSeconds]);

  const handleTimeoutEscalation = async () => {
    // Automatically called when countdown hits 0
    try {
      await api.resolveDeviation(journeyId, {
        action: 'request_help',
        note: `No response within ${timeoutSeconds}s countdown. Persistent route deviation: ${deviationDistance}m.`
      });
      onResolved('timeout_help');
    } catch (e) {
      console.error(e);
    }
  };

  const handleAction = async (action: 'safe_dismiss' | 'update_route' | 'request_help') => {
    setSubmitting(true);
    try {
      await api.resolveDeviation(journeyId, { action });
      onResolved(action);
    } catch (err: any) {
      alert(`Error resolving deviation: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  const progressPct = ((timeoutSeconds - secondsRemaining) / timeoutSeconds) * 100;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 backdrop-blur-md p-4 animate-in fade-in">
      <div className="bg-slate-900 border-2 border-amber-500/70 rounded-2xl max-w-lg w-full p-6 shadow-2xl text-slate-100">
        
        {/* Header with Countdown Bar */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-amber-500/20 text-amber-400 rounded-xl border border-amber-500/30">
              <AlertTriangle className="w-7 h-7 animate-bounce" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Route Deviation Detected</h3>
              <p className="text-xs text-amber-300">
                You are approx <strong>{deviationDistance} meters</strong> off your planned route.
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-1.5 bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-xl text-xs font-mono font-bold text-amber-400">
            <Clock className="w-3.5 h-3.5" />
            <span>{secondsRemaining}s</span>
          </div>
        </div>

        {/* Progress Timeout Bar */}
        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden mb-5">
          <div 
            className="h-full bg-amber-500 transition-all duration-1000 ease-linear"
            style={{ width: `${100 - progressPct}%` }}
          />
        </div>

        <p className="text-sm text-slate-300 mb-6 leading-relaxed">
          Did you intentionally take a detour? Please verify your safety. If you do not respond within <strong>{secondsRemaining} seconds</strong>, an emergency alert will be dispatched to your trusted contacts.
        </p>

        {/* Response Action Buttons */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <button
            onClick={() => handleAction('safe_dismiss')}
            disabled={submitting}
            className="flex flex-col items-center justify-center p-3 rounded-xl bg-emerald-950/40 hover:bg-emerald-900/60 border border-emerald-600/50 text-emerald-300 font-semibold text-xs gap-1.5 transition active:scale-95 cursor-pointer disabled:opacity-50"
          >
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <span>I'm Safe</span>
            <span className="text-[10px] text-emerald-400/70 font-normal">Intentional detour</span>
          </button>

          <button
            onClick={() => handleAction('update_route')}
            disabled={submitting}
            className="flex flex-col items-center justify-center p-3 rounded-xl bg-indigo-950/40 hover:bg-indigo-900/60 border border-indigo-600/50 text-indigo-300 font-semibold text-xs gap-1.5 transition active:scale-95 cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className="w-5 h-5 text-indigo-400" />
            <span>Update Route</span>
            <span className="text-[10px] text-indigo-400/70 font-normal">Adopt current path</span>
          </button>

          <button
            onClick={() => handleAction('request_help')}
            disabled={submitting}
            className="flex flex-col items-center justify-center p-3 rounded-xl bg-rose-950/60 hover:bg-rose-900 border border-rose-600 text-rose-300 font-bold text-xs gap-1.5 transition active:scale-95 cursor-pointer disabled:opacity-50 shadow-lg shadow-rose-950"
          >
            <PhoneCall className="w-5 h-5 text-rose-400" />
            <span>Request Help</span>
            <span className="text-[10px] text-rose-300/80 font-normal">Notify contacts</span>
          </button>
        </div>
      </div>
    </div>
  );
};

