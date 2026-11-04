import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { 
  User, Shield, Phone, Mail, Trash2, Plus, AlertTriangle, CheckCircle2, FileText, Check, Lock 
} from 'lucide-react';

export const ProfileSettingsPage: React.FC = () => {
  const { user, refreshProfile } = useAuth();

  // Profile Edit State
  const [name, setName] = useState(user?.name || '');
  const [phoneNumber, setPhoneNumber] = useState(user?.phone_number || '');
  const [emergencyNote, setEmergencyNote] = useState(user?.emergency_note || '');
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileSaved, setProfileSaved] = useState(false);

  // Contacts State
  const [contacts, setContacts] = useState<any[]>([]);
  const [newContactName, setNewContactName] = useState('');
  const [newContactPhone, setNewContactPhone] = useState('');
  const [newContactEmail, setNewContactEmail] = useState('');
  const [newContactRel, setNewContactRel] = useState('Friend');
  const [newContactPrimary, setNewContactPrimary] = useState(false);
  const [addingContact, setAddingContact] = useState(false);

  // Alerts State
  const [alerts, setAlerts] = useState<any[]>([]);
  const [resolvingId, setResolvingId] = useState<number | null>(null);
  const [resolveNote, setResolveNote] = useState('');

  const loadData = async () => {
    try {
      const [contactsData, alertsData] = await Promise.all([
        api.getContacts(),
        api.getAlerts()
      ]);
      setContacts(contactsData);
      setAlerts(alertsData);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
    if (user) {
      setName(user.name);
      setPhoneNumber(user.phone_number || '');
      setEmergencyNote(user.emergency_note || '');
    }
  }, [user]);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileSaving(true);
    try {
      await api.updateProfile({
        name,
        phone_number: phoneNumber,
        emergency_note: emergencyNote
      });
      await refreshProfile();
      setProfileSaved(true);
      setTimeout(() => setProfileSaved(false), 3000);
    } catch (err: any) {
      alert(`Error updating profile: ${err.message}`);
    } finally {
      setProfileSaving(false);
    }
  };

  const handleAddContact = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddingContact(true);
    try {
      await api.addContact({
        contact_name: newContactName.trim(),
        contact_phone: newContactPhone.trim(),
        contact_email: newContactEmail.trim() || undefined,
        relationship: newContactRel,
        is_primary: newContactPrimary
      });
      setNewContactName('');
      setNewContactPhone('');
      setNewContactEmail('');
      setNewContactPrimary(false);
      await loadData();
    } catch (err: any) {
      alert(`Error adding contact: ${err.message}`);
    } finally {
      setAddingContact(false);
    }
  };

  const handleDeleteContact = async (id: number) => {
    if (window.confirm("Delete this emergency contact?")) {
      try {
        await api.deleteContact(id);
        await loadData();
      } catch (err: any) {
        alert(err.message);
      }
    }
  };

  const handleResolveAlert = async (alertId: number) => {
    if (!resolveNote.trim()) {
      alert("Please provide a brief resolution note explaining why the alert is safe/cleared.");
      return;
    }
    try {
      await api.resolveAlert(alertId, resolveNote);
      setResolveNote('');
      setResolvingId(null);
      await loadData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      
      <div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">
          Profile, Safety & Privacy Settings
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Manage your verified credentials, trusted emergency contacts, and alert resolution history.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Profile Info & Privacy (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-5">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <User className="w-5 h-5 text-rose-600" />
                <span>Account Profile</span>
              </h2>

              <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                user?.verification_status === 'verified' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
              }`}>
                {user?.verification_status}
              </span>
            </div>

            {profileSaved && (
              <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-600" />
                <span>Profile details updated successfully!</span>
              </div>
            )}

            <form onSubmit={handleUpdateProfile} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={e => setName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-rose-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label>
                <input
                  type="email"
                  disabled
                  value={user?.email || ''}
                  className="w-full px-3 py-2 bg-slate-100 border border-slate-200 rounded-xl text-xs text-slate-500 cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Phone Number</label>
                <input
                  type="tel"
                  placeholder="+1 555-0142"
                  value={phoneNumber}
                  onChange={e => setPhoneNumber(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-rose-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Emergency Medical / Safety Note
                </label>
                <textarea
                  rows={2}
                  placeholder="e.g. Inhaler in pocket, blood type, known allergies..."
                  value={emergencyNote}
                  onChange={e => setEmergencyNote(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-rose-500"
                />
              </div>

              <button
                type="submit"
                disabled={profileSaving}
                className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition cursor-pointer disabled:opacity-50"
              >
                {profileSaving ? 'Saving...' : 'Save Profile Changes'}
              </button>
            </form>
          </div>

          {/* Privacy Protections Box */}
          <div className="bg-slate-900 text-slate-100 p-6 rounded-3xl border border-slate-800 shadow-xl space-y-3 text-xs">
            <h3 className="font-bold flex items-center gap-2 text-rose-300">
              <Lock className="w-4 h-4" />
              <span>Data Protection & Privacy Policy</span>
            </h3>
            <p className="text-slate-400 leading-relaxed text-[11px]">
              Safira is engineered to protect women travellers against stalker attacks and unauthorized surveillance.
            </p>
            <ul className="text-slate-400 space-y-1.5 text-[11px] list-disc list-inside">
              <li>Home and work street addresses are never shown to prospective matches.</li>
              <li>Only coarse approximate corridors (~150m) are rendered before mutual connection.</li>
              <li>GPS location breadcrumbs are retained only during journey monitoring.</li>
            </ul>
          </div>
        </div>

        {/* Right Column: Trusted Contacts & Alerts (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          
          {/* Trusted Contacts Manager */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-5">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Shield className="w-5 h-5 text-emerald-600" />
                <span>Configured Trusted Contacts</span>
              </h2>
              <span className="text-xs text-slate-400">{contacts.length} Contact{contacts.length !== 1 ? 's' : ''}</span>
            </div>

            <p className="text-xs text-slate-500">
              When route deviations persist past timeout or when you tap <strong>SOS</strong>, automated dispatches are sent immediately to these contacts.
            </p>

            {/* List */}
            {contacts.length === 0 ? (
              <div className="p-4 bg-slate-50 rounded-2xl text-xs text-slate-400 text-center">
                No trusted contacts configured. Add a contact below.
              </div>
            ) : (
              <div className="space-y-2.5">
                {contacts.map((c) => (
                  <div key={c.id} className="p-3.5 bg-slate-50 rounded-2xl border border-slate-100 flex items-center justify-between">
                    <div>
                      <div className="text-xs font-bold text-slate-900 flex items-center gap-2">
                        <span>{c.contact_name}</span>
                        {c.is_primary && (
                          <span className="text-[9px] bg-emerald-100 text-emerald-800 px-2 py-0.2 rounded-full font-bold">
                            Primary
                          </span>
                        )}
                        <span className="text-[10px] text-slate-400 font-normal">({c.relationship})</span>
                      </div>
                      <div className="text-[11px] text-slate-500 mt-0.5">{c.contact_phone} {c.contact_email ? `• ${c.contact_email}` : ''}</div>
                    </div>

                    <button
                      onClick={() => handleDeleteContact(c.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-600 transition cursor-pointer"
                      title="Delete contact"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Add Contact Form */}
            <form onSubmit={handleAddContact} className="pt-4 border-t border-slate-100 space-y-3">
              <h3 className="text-xs font-bold text-slate-700">+ Add New Trusted Contact</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                <input
                  type="text"
                  required
                  placeholder="Contact Name (e.g. Mom, Sister)"
                  value={newContactName}
                  onChange={e => setNewContactName(e.target.value)}
                  className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs"
                />
                <input
                  type="tel"
                  required
                  placeholder="Phone Number (+1 555-0199)"
                  value={newContactPhone}
                  onChange={e => setNewContactPhone(e.target.value)}
                  className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs"
                />
                <input
                  type="email"
                  placeholder="Email Address (Optional)"
                  value={newContactEmail}
                  onChange={e => setNewContactEmail(e.target.value)}
                  className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs"
                />
                <select
                  value={newContactRel}
                  onChange={e => setNewContactRel(e.target.value)}
                  className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs"
                >
                  <option value="Family Guardian">Family Guardian</option>
                  <option value="Friend">Friend</option>
                  <option value="Roommate">Roommate</option>
                  <option value="Colleague">Colleague</option>
                </select>
              </div>

              <div className="flex items-center justify-between pt-1">
                <label className="flex items-center gap-2 text-xs text-slate-600 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={newContactPrimary}
                    onChange={e => setNewContactPrimary(e.target.checked)}
                    className="w-4 h-4 text-emerald-600 rounded"
                  />
                  <span>Designate as primary contact</span>
                </label>

                <button
                  type="submit"
                  disabled={addingContact}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs shadow-sm cursor-pointer disabled:opacity-50"
                >
                  {addingContact ? 'Adding...' : 'Save Contact'}
                </button>
              </div>
            </form>
          </div>

          {/* Emergency Alert Dispatch History */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-500" />
              <span>Emergency Alerts & SOS History</span>
            </h2>

            {alerts.length === 0 ? (
              <div className="p-4 bg-slate-50 rounded-2xl text-xs text-slate-400 text-center">
                No emergency alerts recorded. All journeys safe and sound.
              </div>
            ) : (
              <div className="space-y-3">
                {alerts.map((a) => (
                  <div key={a.id} className="p-4 bg-slate-50 rounded-2xl border border-slate-100 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900 uppercase tracking-wide">
                          {a.alert_type.replace('_', ' ')}
                        </span>
                        <span className="text-[10px] text-slate-400">Alert #{a.id}</span>
                      </div>

                      <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase ${
                        a.status === 'resolved' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800 animate-pulse'
                      }`}>
                        {a.status}
                      </span>
                    </div>

                    <div className="text-slate-600 text-[11px]">{a.address_text}</div>
                    <div className="text-[10px] text-slate-400">Triggered: {new Date(a.created_at).toLocaleString()}</div>

                    {a.status === 'active' && (
                      <div className="pt-2 border-t border-slate-200 flex items-center gap-2">
                        <input
                          type="text"
                          placeholder="Resolution note (e.g. Safe at home, false alarm)..."
                          value={resolvingId === a.id ? resolveNote : ''}
                          onFocus={() => setResolvingId(a.id)}
                          onChange={e => setResolveNote(e.target.value)}
                          className="flex-1 px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs"
                        />
                        <button
                          onClick={() => handleResolveAlert(a.id)}
                          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold cursor-pointer"
                        >
                          Resolve
                        </button>
                      </div>
                    )}
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

