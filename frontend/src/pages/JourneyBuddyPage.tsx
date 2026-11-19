import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { MapView } from '../components/MapView';
import { 
  Users, Calendar, Clock, MapPin, Navigation, Shield, MessageSquare, 
  Send, CheckCircle2, XCircle, Search, Filter, AlertCircle, Plus, 
  ArrowRight, Sparkles, Check, Trash2, Edit3, Loader2, Coffee 
} from 'lucide-react';

export const JourneyBuddyPage: React.FC = () => {
  const { user, isVerified } = useAuth();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState<'find' | 'schedule' | 'requests' | 'confirmed'>('find');

  // Browse Buddies State
  const [buddies, setBuddies] = useState<any[]>([]);
  const [loadingBuddies, setLoadingBuddies] = useState(false);
  const [filterMode, setFilterMode] = useState<string>('');
  const [filterDest, setFilterDest] = useState<string>('');
  const [filterDate, setFilterDate] = useState<string>('');
  const [selectedBuddyJourney, setSelectedBuddyJourney] = useState<any | null>(null);

  // Request modal
  const [requestModalOpen, setRequestModalOpen] = useState(false);
  const [targetJourneyId, setTargetJourneyId] = useState<number | null>(null);
  const [initialMsg, setInitialMsg] = useState('Hi! I am travelling along a similar route. Would you like to travel together for extra safety?');
  const [sendingRequest, setSendingRequest] = useState(false);

  // My Scheduled Journeys
  const [myJourneys, setMyJourneys] = useState<any[]>([]);
  const [loadingMyJourneys, setLoadingMyJourneys] = useState(false);

  // Schedule Form State
  const [schedOriginName, setSchedOriginName] = useState('');
  const [schedOriginLat, setSchedOriginLat] = useState(40.7580);
  const [schedOriginLng, setSchedOriginLng] = useState(-73.9855);
  const [schedDestName, setSchedDestName] = useState('');
  const [schedDestLat, setSchedDestLat] = useState(40.7681);
  const [schedDestLng, setSchedDestLng] = useState(-73.9819);
  const [schedTravelMode, setSchedTravelMode] = useState('walking');
  const [schedDate, setSchedDate] = useState(new Date().toISOString().slice(0, 10));
  const [schedTime, setSchedTime] = useState('17:30');
  const [schedSubmitting, setSchedSubmitting] = useState(false);
  const [schedOriginSearch, setSchedOriginSearch] = useState('');
  const [schedDestSearch, setSchedDestSearch] = useState('');
  const [originSuggestions, setOriginSuggestions] = useState<any[]>([]);
  const [destSuggestions, setDestSuggestions] = useState<any[]>([]);

  // Requests State
  const [requests, setRequests] = useState<any[]>([]);
  const [loadingRequests, setLoadingRequests] = useState(false);

  // Confirmed Groups & Chat State
  const [confirmedGroups, setConfirmedGroups] = useState<any[]>([]);
  const [activeGroupId, setActiveGroupId] = useState<number | null>(null);
  const [groupMessages, setGroupMessages] = useState<any[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [sendingChat, setSendingChat] = useState(false);

  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 4000);
  };

  // Load Browse Data
  const loadBrowseData = async () => {
    setLoadingBuddies(true);
    try {
      const data = await api.browseJourneys({
        travel_mode: filterMode || undefined,
        destination: filterDest || undefined,
        journey_date: filterDate || undefined
      });
      setBuddies(data);
      if (data.length > 0 && !selectedBuddyJourney) {
        setSelectedBuddyJourney(data[0]);
      }
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoadingBuddies(false);
    }
  };

  // Load My Journeys
  const loadMyJourneys = async () => {
    setLoadingMyJourneys(true);
    try {
      const data = await api.getMyJourneys();
      setMyJourneys(data);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoadingMyJourneys(false);
    }
  };

  // Load Requests
  const loadRequests = async () => {
    setLoadingRequests(true);
    try {
      const data = await api.getMyRequests();
      setRequests(data);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoadingRequests(false);
    }
  };

  // Load Confirmed Groups
  const loadConfirmedGroups = async () => {
    try {
      const groups = await api.getCompanionGroups();
      setConfirmedGroups(groups);
      if (groups.length > 0 && !activeGroupId) {
        setActiveGroupId(groups[0].id);
      }
    } catch (e: any) {
      console.error(e);
    }
  };

  // Load Chat Messages
  const loadChatMessages = async (groupId: number) => {
    try {
      const msgs = await api.getGroupMessages(groupId);
      setGroupMessages(msgs);
    } catch (e: any) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (activeTab === 'find') {
      loadBrowseData();
    } else if (activeTab === 'schedule') {
      loadMyJourneys();
    } else if (activeTab === 'requests') {
      loadRequests();
    } else if (activeTab === 'confirmed') {
      loadConfirmedGroups();
    }
  }, [activeTab]);

  useEffect(() => {
    if (activeGroupId && activeTab === 'confirmed') {
      loadChatMessages(activeGroupId);
      const interval = setInterval(() => loadChatMessages(activeGroupId), 5000);
      return () => clearInterval(interval);
    }
  }, [activeGroupId, activeTab]);

  // Autocomplete debounces
  useEffect(() => {
    if (!schedOriginSearch || schedOriginSearch.trim().length < 3) {
      setOriginSuggestions([]);
      return;
    }
    const t = setTimeout(async () => {
      const res = await api.locationIQ.autocomplete(schedOriginSearch);
      setOriginSuggestions(res);
    }, 300);
    return () => clearTimeout(t);
  }, [schedOriginSearch]);

  useEffect(() => {
    if (!schedDestSearch || schedDestSearch.trim().length < 3) {
      setDestSuggestions([]);
      return;
    }
    const t = setTimeout(async () => {
      const res = await api.locationIQ.autocomplete(schedDestSearch);
      setDestSuggestions(res);
    }, 300);
    return () => clearTimeout(t);
  }, [schedDestSearch]);

  // Handle Schedule Journey Submit
  const handleScheduleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!schedOriginName || !schedDestName) {
      showNotification('error', 'Please specify both starting location and destination.');
      return;
    }

    setSchedSubmitting(true);
    try {
      const departureDateTime = new Date(`${schedDate}T${schedTime}:00`).toISOString();
      await api.createJourney({
        origin_name: schedOriginName,
        origin_lat: schedOriginLat,
        origin_lng: schedOriginLng,
        destination_name: schedDestName,
        destination_lat: schedDestLat,
        destination_lng: schedDestLng,
        travel_mode: schedTravelMode,
        departure_time: departureDateTime,
        is_public_for_matching: true
      });

      showNotification('success', 'Journey scheduled successfully! Visible to verified travel buddies.');
      setSchedOriginName('');
      setSchedDestName('');
      setSchedOriginSearch('');
      setSchedDestSearch('');
      await loadMyJourneys();
      setActiveTab('find');
    } catch (err: any) {
      showNotification('error', err.message || 'Failed to schedule journey.');
    } finally {
      setSchedSubmitting(false);
    }
  };

  // Handle Delete/Cancel Journey
  const handleDeleteJourney = async (id: number) => {
    if (!window.confirm('Are you sure you want to cancel this scheduled journey?')) return;
    try {
      await api.deleteJourney(id);
      showNotification('success', 'Scheduled journey cancelled.');
      await loadMyJourneys();
    } catch (err: any) {
      showNotification('error', err.message || 'Failed to cancel journey.');
    }
  };

  // Handle Send Travel Buddy Request
  const handleSendBuddyRequest = async () => {
    if (!targetJourneyId) return;
    setSendingRequest(true);
    try {
      await api.sendCompanionRequest({
        receiver_journey_id: targetJourneyId,
        initial_message: initialMsg
      });
      showNotification('success', 'Travel Together request sent! The other traveller will be notified.');
      setRequestModalOpen(false);
      setActiveTab('requests');
    } catch (err: any) {
      showNotification('error', err.message || 'Failed to send request. Ensure you have a scheduled journey first.');
    } finally {
      setSendingRequest(false);
    }
  };

  // Handle Request Status Update (Accept/Reject)
  const handleRequestStatusChange = async (requestId: number, newStatus: string) => {
    try {
      await api.updateRequestStatus(requestId, newStatus);
      showNotification('success', `Request ${newStatus}!`);
      await loadRequests();
      if (newStatus === 'accepted') {
        await loadConfirmedGroups();
        setActiveTab('confirmed');
      }
    } catch (err: any) {
      showNotification('error', err.message || 'Failed to update request.');
    }
  };

  // Handle Send Chat Message
  const handleSendChatMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeGroupId || !chatInput.trim()) return;

    setSendingChat(true);
    try {
      await api.sendGroupMessage(activeGroupId, chatInput.trim());
      setChatInput('');
      await loadChatMessages(activeGroupId);
    } catch (err: any) {
      showNotification('error', err.message || 'Failed to send message.');
    } finally {
      setSendingChat(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Toast Notification */}
      {notification && (
        <div className={`fixed top-20 right-6 z-50 p-4 rounded-2xl shadow-xl flex items-center gap-3 text-xs font-bold text-white transition-all ${
          notification.type === 'success' ? 'bg-emerald-600 border border-emerald-500' : 'bg-rose-600 border border-rose-500'
        }`}>
          {notification.type === 'success' ? <CheckCircle2 className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
          <span>{notification.message}</span>
        </div>
      )}

      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-3xl p-6 sm:p-8 text-white border border-slate-800 shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 text-xs font-bold uppercase tracking-wider mb-3">
            <Users className="w-3.5 h-3.5 text-indigo-400" />
            <span>Journey Buddy • Travel Together</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black tracking-tight">
            Never Travel Alone. Connect & Walk Together.
          </h1>
          <p className="text-sm text-slate-300 mt-2 leading-relaxed">
            Schedule your upcoming trips and discover verified women travelling along similar corridors at approximately the same time. Connect safely with zero exposure of your private personal contact details.
          </p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 overflow-x-auto pb-2">
        <button
          onClick={() => setActiveTab('find')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition whitespace-nowrap cursor-pointer ${
            activeTab === 'find' 
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30' 
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <Search className="w-4 h-4" />
          <span>Find Travel Buddies</span>
          {buddies.length > 0 && (
            <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${activeTab === 'find' ? 'bg-indigo-800 text-white' : 'bg-slate-200 text-slate-700'}`}>
              {buddies.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('schedule')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition whitespace-nowrap cursor-pointer ${
            activeTab === 'schedule' 
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30' 
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <Calendar className="w-4 h-4" />
          <span>Schedule My Journey</span>
          {myJourneys.length > 0 && (
            <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${activeTab === 'schedule' ? 'bg-indigo-800 text-white' : 'bg-slate-200 text-slate-700'}`}>
              {myJourneys.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('requests')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition whitespace-nowrap cursor-pointer ${
            activeTab === 'requests' 
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30' 
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>My Requests</span>
          {requests.filter(r => r.status === 'pending').length > 0 && (
            <span className="text-[10px] bg-rose-500 text-white px-1.5 py-0.2 rounded-full font-bold">
              {requests.filter(r => r.status === 'pending').length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('confirmed')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition whitespace-nowrap cursor-pointer ${
            activeTab === 'confirmed' 
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30' 
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          <span>Confirmed Buddies & Safe Chat</span>
          {confirmedGroups.length > 0 && (
            <span className="text-[10px] bg-emerald-500 text-white px-1.5 py-0.2 rounded-full font-bold">
              {confirmedGroups.length}
            </span>
          )}
        </button>
      </div>

      {/* TAB 1: FIND TRAVEL BUDDIES */}
      {activeTab === 'find' && (
        <div className="space-y-6">
          {/* Filter Bar */}
          <div className="bg-white p-4 rounded-3xl border border-slate-200/80 shadow-sm flex flex-col sm:flex-row items-center gap-3">
            <div className="relative flex-1 w-full">
              <input
                type="text"
                placeholder="Filter destination (e.g. Central Park, Columbus Circle)..."
                value={filterDest}
                onChange={e => setFilterDest(e.target.value)}
                className="w-full pl-9 pr-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-indigo-500"
              />
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            </div>

            <div className="w-full sm:w-auto flex items-center gap-2">
              <select
                value={filterMode}
                onChange={e => setFilterMode(e.target.value)}
                className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Travel Modes</option>
                <option value="walking">Walking</option>
                <option value="transit">Public Transit</option>
                <option value="bicycling">Bicycling</option>
                <option value="driving">Driving / Cab</option>
              </select>

              <input
                type="date"
                value={filterDate}
                onChange={e => setFilterDate(e.target.value)}
                className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-indigo-500"
              />

              <button
                onClick={loadBrowseData}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl shadow cursor-pointer"
              >
                Apply
              </button>
            </div>
          </div>

          {/* Results Grid: Cards + LocationIQ Map */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            
            {/* Left: Buddy Cards List (5 Cols) */}
            <div className="lg:col-span-5 space-y-3">
              {loadingBuddies ? (
                <div className="p-8 text-center bg-white rounded-3xl border border-slate-200 text-xs text-slate-400">
                  <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-500" />
                  Searching available travel buddies...
                </div>
              ) : buddies.length === 0 ? (
                <div className="p-8 text-center bg-white rounded-3xl border border-slate-200 text-xs text-slate-500 space-y-3">
                  <Users className="w-8 h-8 text-slate-300 mx-auto" />
                  <p className="font-semibold text-slate-700">No scheduled journeys found for the chosen filters.</p>
                  <p className="text-[11px] text-slate-400">Try clearing filters or schedule your own journey so others can discover and match with you!</p>
                  <button
                    onClick={() => setActiveTab('schedule')}
                    className="px-4 py-2 bg-indigo-600 text-white font-bold rounded-xl text-xs cursor-pointer inline-flex items-center gap-1.5"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Schedule My Journey</span>
                  </button>
                </div>
              ) : (
                buddies.map((buddy) => {
                  const isSelected = selectedBuddyJourney?.journey_id === buddy.journey_id;
                  const depDate = new Date(buddy.departure_time);

                  return (
                    <div
                      key={buddy.journey_id}
                      onClick={() => setSelectedBuddyJourney(buddy)}
                      className={`p-4 rounded-2xl border transition cursor-pointer text-left ${
                        isSelected 
                          ? 'bg-indigo-50/70 border-indigo-400 shadow-md ring-2 ring-indigo-500/20' 
                          : 'bg-white border-slate-200/80 hover:border-slate-300 shadow-sm'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-xs text-slate-900">{buddy.user_display_name}</span>
                          <span className="text-[9px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                            <Shield className="w-2.5 h-2.5" /> Verified
                          </span>
                        </div>
                        <span className="text-[10px] text-slate-500 capitalize bg-slate-100 px-2 py-0.5 rounded-md font-medium">
                          {buddy.travel_mode}
                        </span>
                      </div>

                      <div className="space-y-1 text-xs text-slate-600 mb-3">
                        <div className="flex items-center gap-1.5">
                          <MapPin className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                          <span className="truncate">From: <strong>{buddy.origin_name}</strong></span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <MapPin className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                          <span className="truncate">To: <strong>{buddy.destination_name}</strong></span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-[11px] text-slate-500">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5 text-slate-400" />
                          <span>{depDate.toLocaleDateString()} at {depDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                        </div>

                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setTargetJourneyId(buddy.journey_id);
                            setRequestModalOpen(true);
                          }}
                          className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg text-xs cursor-pointer flex items-center gap-1 transition"
                        >
                          <span>Connect</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Right: Map Preview of Selected Corridor (7 Cols) */}
            <div className="lg:col-span-7 bg-white p-5 rounded-3xl border border-slate-200/80 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-900">
                    {selectedBuddyJourney ? `Route Preview: ${selectedBuddyJourney.user_display_name}` : 'Safety Route Corridor'}
                  </h3>
                  <p className="text-xs text-slate-400">LocationIQ street map with suggested public meeting checkpoints</p>
                </div>

                {selectedBuddyJourney && (
                  <button
                    onClick={() => {
                      setTargetJourneyId(selectedBuddyJourney.journey_id);
                      setRequestModalOpen(true);
                    }}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs flex items-center gap-1.5 shadow cursor-pointer"
                  >
                    <Users className="w-3.5 h-3.5" />
                    <span>Request to Travel Together</span>
                  </button>
                )}
              </div>

              {selectedBuddyJourney ? (
                <MapView
                  origin={{ name: selectedBuddyJourney.origin_name, lat: selectedBuddyJourney.origin_lat, lng: selectedBuddyJourney.origin_lng }}
                  destination={{ name: selectedBuddyJourney.destination_name, lat: selectedBuddyJourney.destination_lat, lng: selectedBuddyJourney.destination_lng }}
                  interactive={true}
                  height="450px"
                />
              ) : (
                <div className="h-[450px] rounded-2xl bg-slate-900 flex items-center justify-center text-slate-500 text-xs">
                  Select a journey on the left to preview route on the map
                </div>
              )}
            </div>

          </div>
        </div>
      )}

      {/* TAB 2: SCHEDULE MY JOURNEY */}
      {activeTab === 'schedule' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Schedule Form (5 Cols) */}
          <div className="lg:col-span-5 bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-indigo-600" />
              <span>Schedule Upcoming Journey</span>
            </h2>
            <p className="text-xs text-slate-500">
              Enter your planned journey details. Other verified travellers moving along your route will be able to discover and request to accompany you.
            </p>

            <form onSubmit={handleScheduleSubmit} className="space-y-3.5">
              
              {/* Origin with Autocomplete */}
              <div className="space-y-1.5 relative">
                <label className="block text-xs font-bold text-slate-700">Starting Location</label>
                <div className="relative">
                  <input
                    type="text"
                    required
                    placeholder="Search start point (LocationIQ geocoded)..."
                    value={schedOriginSearch || schedOriginName}
                    onChange={e => {
                      setSchedOriginSearch(e.target.value);
                      setSchedOriginName(e.target.value);
                    }}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-indigo-500 pl-8"
                  />
                  <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-3" />
                </div>

                {originSuggestions.length > 0 && (
                  <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden max-h-40 overflow-y-auto">
                    {originSuggestions.map((item, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => {
                          setSchedOriginName(item.display_name);
                          setSchedOriginLat(item.lat);
                          setSchedOriginLng(item.lon);
                          setSchedOriginSearch('');
                          setOriginSuggestions([]);
                        }}
                        className="w-full text-left px-3 py-2 hover:bg-indigo-50 text-[11px] border-b border-slate-100 last:border-b-0 text-slate-800 truncate"
                      >
                        {item.display_name}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Destination with Autocomplete */}
              <div className="space-y-1.5 relative">
                <label className="block text-xs font-bold text-slate-700">Destination</label>
                <div className="relative">
                  <input
                    type="text"
                    required
                    placeholder="Search destination via LocationIQ..."
                    value={schedDestSearch || schedDestName}
                    onChange={e => {
                      setSchedDestSearch(e.target.value);
                      setSchedDestName(e.target.value);
                    }}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-rose-500 pl-8"
                  />
                  <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-3" />
                </div>

                {destSuggestions.length > 0 && (
                  <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden max-h-40 overflow-y-auto">
                    {destSuggestions.map((item, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => {
                          setSchedDestName(item.display_name);
                          setSchedDestLat(item.lat);
                          setSchedDestLng(item.lon);
                          setSchedDestSearch('');
                          setDestSuggestions([]);
                        }}
                        className="w-full text-left px-3 py-2 hover:bg-rose-50 text-[11px] border-b border-slate-100 last:border-b-0 text-slate-800 truncate"
                      >
                        {item.display_name}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Travel Mode */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Travel Mode</label>
                <select
                  value={schedTravelMode}
                  onChange={e => setSchedTravelMode(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-indigo-500"
                >
                  <option value="walking">Walking</option>
                  <option value="transit">Public Transit</option>
                  <option value="bicycling">Bicycling</option>
                  <option value="driving">Driving / Cab</option>
                </select>
              </div>

              {/* Date & Time */}
              <div className="grid grid-cols-2 gap-2.5">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Date</label>
                  <input
                    type="date"
                    required
                    value={schedDate}
                    onChange={e => setSchedDate(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Departure Time</label>
                  <input
                    type="time"
                    required
                    value={schedTime}
                    onChange={e => setSchedTime(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={schedSubmitting}
                className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-600/30 flex items-center justify-center gap-1.5 transition cursor-pointer disabled:opacity-50"
              >
                {schedSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Calendar className="w-4 h-4" />}
                <span>{schedSubmitting ? 'Scheduling...' : 'Save Scheduled Journey'}</span>
              </button>
            </form>
          </div>

          {/* Scheduled Journeys List (7 Cols) */}
          <div className="lg:col-span-7 bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-slate-900">My Scheduled Journeys</h2>
              <span className="text-xs text-slate-400">{myJourneys.length} Planned</span>
            </div>

            {loadingMyJourneys ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading your journeys...</div>
            ) : myJourneys.length === 0 ? (
              <div className="p-8 text-center bg-slate-50 rounded-2xl text-xs text-slate-400">
                You haven't scheduled any journeys yet. Use the form on the left to schedule your first trip.
              </div>
            ) : (
              <div className="space-y-3">
                {myJourneys.map((j) => (
                  <div key={j.id} className="p-4 rounded-2xl border border-slate-200 bg-slate-50/60 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
                    <div className="space-y-1">
                      <div className="font-bold text-slate-900 flex items-center gap-2">
                        <span>{j.origin_name} → {j.destination_name}</span>
                        <span className={`text-[10px] px-2 py-0.2 rounded-full font-bold uppercase ${
                          j.status === 'in_progress' ? 'bg-emerald-100 text-emerald-800' : 'bg-indigo-100 text-indigo-800'
                        }`}>
                          {j.status}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-500 flex items-center gap-3">
                        <span>Departure: {new Date(j.departure_time).toLocaleString()}</span>
                        <span className="capitalize">• {j.travel_mode}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 w-full sm:w-auto">
                      <button
                        onClick={() => navigate(`/journeys/${j.id}/live`)}
                        className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold cursor-pointer"
                      >
                        Open Live
                      </button>
                      <button
                        onClick={() => handleDeleteJourney(j.id)}
                        className="p-1.5 text-slate-400 hover:text-rose-600 transition cursor-pointer"
                        title="Cancel Journey"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      )}

      {/* TAB 3: REQUESTS & INVITES */}
      {activeTab === 'requests' && (
        <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900">Travel Companion Requests</h2>
              <p className="text-xs text-slate-400">Incoming requests from other verified women and invitations you have sent</p>
            </div>
            <button
              onClick={loadRequests}
              className="text-xs text-indigo-600 font-bold hover:underline cursor-pointer"
            >
              Refresh
            </button>
          </div>

          {loadingRequests ? (
            <div className="p-8 text-center text-xs text-slate-400">Loading requests...</div>
          ) : requests.length === 0 ? (
            <div className="p-8 text-center bg-slate-50 rounded-2xl text-xs text-slate-400">
              No companion requests active. Browse journeys to find a companion or schedule a journey to receive invitations.
            </div>
          ) : (
            <div className="space-y-3">
              {requests.map((req) => {
                const isIncoming = req.receiver_id === user?.id;

                return (
                  <div key={req.id} className="p-4 rounded-2xl border border-slate-200 bg-slate-50/70 text-xs space-y-2.5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900">
                          {isIncoming ? `Request from: ${req.sender_name}` : `Invitation sent to: ${req.receiver_name}`}
                        </span>
                        <span className="text-[10px] text-slate-400">Req #{req.id}</span>
                      </div>

                      <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase ${
                        req.status === 'accepted' ? 'bg-emerald-100 text-emerald-800' :
                        req.status === 'rejected' ? 'bg-rose-100 text-rose-800' :
                        'bg-amber-100 text-amber-800'
                      }`}>
                        {req.status}
                      </span>
                    </div>

                    {req.initial_message && (
                      <div className="bg-white p-3 rounded-xl border border-slate-200/60 text-slate-700 italic text-[11px]">
                        "{req.initial_message}"
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-2 border-t border-slate-200 text-[11px] text-slate-400">
                      <span>Date: {new Date(req.created_at).toLocaleString()}</span>

                      {isIncoming && req.status === 'pending' && (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleRequestStatusChange(req.id, 'accepted')}
                            className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg cursor-pointer"
                          >
                            Accept to Travel Together
                          </button>
                          <button
                            onClick={() => handleRequestStatusChange(req.id, 'rejected')}
                            className="px-3 py-1 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold rounded-lg cursor-pointer"
                          >
                            Decline
                          </button>
                        </div>
                      )}

                      {!isIncoming && req.status === 'pending' && (
                        <button
                          onClick={() => handleRequestStatusChange(req.id, 'cancelled')}
                          className="px-3 py-1 bg-slate-200 hover:bg-rose-100 hover:text-rose-700 text-slate-700 font-bold rounded-lg cursor-pointer"
                        >
                          Cancel Request
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* TAB 4: CONFIRMED BUDDIES & SAFE CHAT */}
      {activeTab === 'confirmed' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* Confirmed Groups List (4 Cols) */}
          <div className="lg:col-span-4 bg-white p-5 rounded-3xl border border-slate-200/80 shadow-sm space-y-3">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Confirmed Travel Pairs</span>
            </h2>

            {confirmedGroups.length === 0 ? (
              <div className="p-6 text-center bg-slate-50 rounded-2xl text-xs text-slate-400">
                No confirmed travel buddies yet. Once you mutually accept a request, you can coordinate securely here.
              </div>
            ) : (
              confirmedGroups.map((g) => (
                <div
                  key={g.id}
                  onClick={() => setActiveGroupId(g.id)}
                  className={`p-3.5 rounded-2xl border text-left cursor-pointer transition ${
                    activeGroupId === g.id
                      ? 'bg-indigo-50 border-indigo-400 shadow-sm'
                      : 'bg-slate-50/70 border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="text-xs font-bold text-slate-900 flex items-center justify-between">
                    <span>Travel Pair #{g.id}</span>
                    <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold">
                      Confirmed
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1 flex items-center gap-1">
                    <Coffee className="w-3 h-3 text-amber-500" />
                    <span className="truncate">{g.meeting_point_name || 'Central Transit Station'}</span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Secure In-App Coordination Chat (8 Cols) */}
          <div className="lg:col-span-8 bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm space-y-4 flex flex-col justify-between min-h-[480px]">
            <div>
              <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-3">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                    <Shield className="w-4 h-4 text-emerald-600" />
                    <span>Secure Coordination Chat</span>
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    Encrypted coordination for meeting up. Private phone numbers are never shared without permission.
                  </p>
                </div>
                <span className="text-[10px] bg-indigo-50 border border-indigo-200 text-indigo-700 px-2.5 py-1 rounded-full font-bold">
                  Pair #{activeGroupId || 'N/A'}
                </span>
              </div>

              {/* Messages Container */}
              <div className="space-y-2.5 max-h-[320px] overflow-y-auto p-2">
                {groupMessages.length === 0 ? (
                  <div className="text-center py-12 text-xs text-slate-400">
                    No messages yet. Say hello and coordinate your meeting point!
                  </div>
                ) : (
                  groupMessages.map((m) => {
                    const isMe = m.sender_id === user?.id;
                    return (
                      <div key={m.id} className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}>
                        <div className="text-[10px] text-slate-400 mb-0.5 px-1">{isMe ? 'You' : m.sender_name}</div>
                        <div className={`px-3.5 py-2 rounded-2xl max-w-sm text-xs ${
                          isMe 
                            ? 'bg-indigo-600 text-white rounded-br-none shadow-sm' 
                            : 'bg-slate-100 text-slate-800 rounded-bl-none'
                        }`}>
                          {m.message}
                        </div>
                        <div className="text-[9px] text-slate-400 mt-0.5 px-1">
                          {new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Chat Input Bar */}
            <form onSubmit={handleSendChatMessage} className="pt-3 border-t border-slate-100 flex items-center gap-2">
              <input
                type="text"
                placeholder={activeGroupId ? "Type coordination message (e.g. I am by the north exit)..." : "Select a confirmed pair first"}
                disabled={!activeGroupId || sendingChat}
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                className="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-indigo-500"
              />
              <button
                type="submit"
                disabled={!activeGroupId || !chatInput.trim() || sendingChat}
                className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs flex items-center gap-1.5 transition cursor-pointer disabled:opacity-50"
              >
                {sendingChat ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                <span>Send</span>
              </button>
            </form>
          </div>

        </div>
      )}

      {/* Request Modal */}
      {requestModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-4 border border-slate-200">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Users className="w-5 h-5 text-indigo-600" />
                <span>Request to Travel Together</span>
              </h3>
              <button onClick={() => setRequestModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-500 leading-relaxed">
              Send an invitation to this traveller. If accepted, you will both be able to see suggested safe public meeting checkpoints and coordinate securely.
            </p>

            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-slate-700">Introductory Message</label>
              <textarea
                rows={3}
                value={initialMsg}
                onChange={e => setInitialMsg(e.target.value)}
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setRequestModalOpen(false)}
                className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSendBuddyRequest}
                disabled={sendingRequest}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl shadow cursor-pointer disabled:opacity-50"
              >
                {sendingRequest ? 'Sending Invitation...' : 'Send Invitation'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

