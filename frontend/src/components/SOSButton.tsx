import React, { useState } from 'react';
import { AlertOctagon, CheckCircle2 } from 'lucide-react';
import { api } from '../api/client';

interface SOSButtonProps {
  journeyId?: number;
  currentLat?: number;
  currentLng?: number;
  onTriggered?: (alert: any) => void;
}

export const SOSButton: React.FC<SOSButtonProps> = ({
  journeyId,
  currentLat = 40.7580,
  currentLng = -73.9855,
  onTriggered
}) => {
  const [loading, setLoading] = useState(false);
  const [triggered, setTriggered] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);

  const handleSOS = async () => {
    if (!journeyId) {
      alert("No active journey selected. Please open or start a journey to broadcast SOS location.");
      return;
    }
    setLoading(true);
    try {
      const alertData = await api.triggerSOS({
        journey_id: journeyId,
        alert_type: 'sos',
        latitude: currentLat,
        longitude: currentLng,
        address_text: `Immediate user SOS triggered at (${currentLat.toFixed(4)}, ${currentLng.toFixed(4)})`,
        note: 'Emergency distress signal activated by user.'
      });
      setTriggered(true);
      setConfirmOpen(false);
      if (onTriggered) onTriggered(alertData);
    } catch (err: any) {
      alert(`SOS Dispatch Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setConfirmOpen(true)}
        className="flex items-center gap-2 bg-rose-600 hover:bg-rose-700 active:scale-95 text-white font-bold px-4 py-2 rounded-xl shadow-lg shadow-rose-600/30 transition-all cursor-pointer border border-rose-500"
        title="Immediate Emergency SOS"
      >
        <AlertOctagon className="w-5 h-5 animate-pulse" />
        <span>SOS HELP</span>
      </button>

      {/* Confirmation Modal */}
      {confirmOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border-2 border-rose-600/60 rounded-2xl max-w-md w-full p-6 shadow-2xl text-slate-100">
            <div className="flex items-center gap-3 text-rose-500 mb-4">
              <div className="p-3 bg-rose-950/60 rounded-xl border border-rose-800">
                <AlertOctagon className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Broadcast Emergency SOS?</h3>
                <p className="text-xs text-rose-400">Immediate action. No timeout delay.</p>
              </div>
            </div>

            <p className="text-sm text-slate-300 mb-5 leading-relaxed">
              This will instantly alert all your configured <strong>Trusted Contacts</strong> with your real-time GPS coordinates and timestamp, and flag this journey as requiring urgent attention.
            </p>

            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setConfirmOpen(false)}
                className="px-4 py-2.5 rounded-xl text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 text-sm font-medium transition cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleSOS}
                disabled={loading}
                className="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-sm shadow-lg shadow-rose-600/40 transition active:scale-95 cursor-pointer disabled:opacity-50"
              >
                {loading ? 'Dispatching...' : 'Confirm SOS Distress'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Triggered Success Toast */}
      {triggered && (
        <div className="fixed bottom-6 right-6 z-50 bg-rose-900 border border-rose-500 text-white p-4 rounded-xl shadow-2xl flex items-center gap-3">
          <CheckCircle2 className="w-6 h-6 text-rose-300 shrink-0" />
          <div>
            <div className="font-bold text-sm">Emergency Alert Dispatched!</div>
            <div className="text-xs text-rose-200">Trusted contacts notified with your last known location.</div>
          </div>
          <button onClick={() => setTriggered(false)} className="text-rose-300 hover:text-white ml-2 text-xs">✕</button>
        </div>
      )}
    </>
  );
};

