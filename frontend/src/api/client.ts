const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || '/api/v1';

export function getToken(): string | null {
  return localStorage.getItem('safira_token');
}

export function setToken(token: string) {
  localStorage.setItem('safira_token', token);
}

export function removeToken() {
  localStorage.removeItem('safira_token');
}

function formatErrorMessage(data: any, status: number, statusText: string): string {
  if (!data) {
    return `HTTP ${status}: ${statusText || 'Unknown error'}`;
  }

  // Handle FastAPI detail field
  const detail = data.detail;
  if (typeof detail === 'string') {
    return detail;
  }

  // Handle FastAPI 422 validation error array
  if (Array.isArray(detail)) {
    const messages = detail.map((err: any) => {
      if (typeof err === 'string') return err;
      if (err?.msg) {
        const field = Array.isArray(err.loc) ? err.loc[err.loc.length - 1] : '';
        const fieldPrefix = field && field !== 'body' ? `${field}: ` : '';
        return `${fieldPrefix}${err.msg}`;
      }
      return JSON.stringify(err);
    });
    return messages.join('. ');
  }

  if (typeof detail === 'object' && detail !== null) {
    return detail.msg || detail.message || JSON.stringify(detail);
  }

  if (data.message && typeof data.message === 'string') {
    return data.message;
  }

  return `HTTP ${status}: ${statusText || 'Request failed'}`;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });
  } catch (err: any) {
    throw new Error(
      err?.message?.includes('Failed to fetch') || err?.name === 'TypeError'
        ? 'Unable to connect to the server. Please check your internet connection and ensure the backend is running.'
        : `Network request error: ${err.message}`
    );
  }

  if (response.status === 204) {
    return {} as T;
  }

  const rawText = await response.text();
  let data: any = null;
  if (rawText) {
    try {
      data = JSON.parse(rawText);
    } catch {
      data = null;
    }
  }

  if (!response.ok) {
    const errorMsg = formatErrorMessage(data, response.status, response.statusText);
    throw new Error(errorMsg);
  }

  return data as T;
}

export const api = {
  // Auth
  register: (body: any) => request<any>('/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  login: (body: any) => request<{ access_token: string; token_type: string }>('/auth/login', { method: 'POST', body: JSON.stringify(body) }),
  getProfile: () => request<any>('/auth/me'),
  updateProfile: (body: any) => request<any>('/auth/me', { method: 'PUT', body: JSON.stringify(body) }),

  // Verification
  submitVerification: (body: any) => request<any>('/verification/submit', { method: 'POST', body: JSON.stringify(body) }),
  getVerificationStatus: () => request<any>('/verification/status'),
  getAdminVerifications: () => request<any[]>('/verification/admin/all'),
  reviewVerification: (id: number, body: any) => request<any>(`/verification/admin/review/${id}`, { method: 'POST', body: JSON.stringify(body) }),

  // Journeys
  previewRoute: (body: any) => request<any>('/journeys/preview-route', { method: 'POST', body: JSON.stringify(body) }),
  createJourney: (body: any) => request<any>('/journeys/', { method: 'POST', body: JSON.stringify(body) }),
  getMyJourneys: () => request<any[]>('/journeys/'),
  getJourney: (id: number) => request<any>(`/journeys/${id}`),
  updateJourney: (id: number, body: any) => request<any>(`/journeys/${id}`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteJourney: (id: number) => request<void>(`/journeys/${id}`, { method: 'DELETE' }),
  updateJourneyStatus: (id: number, status: string) => request<any>(`/journeys/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) }),

  // Tracking & Deviation
  recordLocation: (journeyId: number, body: any) => request<any>(`/tracking/${journeyId}/location`, { method: 'POST', body: JSON.stringify(body) }),
  resolveDeviation: (journeyId: number, body: any) => request<any>(`/tracking/${journeyId}/resolve-deviation`, { method: 'POST', body: JSON.stringify(body) }),
  getLocationHistory: (journeyId: number) => request<any[]>(`/tracking/${journeyId}/history`),

  // Companions & Journey Buddy
  browseJourneys: (params: { travel_mode?: string; destination?: string; journey_date?: string } = {}) => {
    const q = new URLSearchParams();
    if (params.travel_mode) q.set('travel_mode', params.travel_mode);
    if (params.destination) q.set('destination', params.destination);
    if (params.journey_date) q.set('journey_date', params.journey_date);
    const queryString = q.toString() ? `?${q.toString()}` : '';
    return request<any[]>(`/companions/browse${queryString}`);
  },
  getMatches: (journeyId: number) => request<any[]>(`/companions/matches/${journeyId}`),
  sendCompanionRequest: (body: any) => request<any>('/companions/requests', { method: 'POST', body: JSON.stringify(body) }),
  getMyRequests: () => request<any[]>('/companions/requests'),
  updateRequestStatus: (requestId: number, status: string) => request<any>(`/companions/requests/${requestId}`, { method: 'PATCH', body: JSON.stringify({ status }) }),
  getCompanionGroups: () => request<any[]>('/companions/groups'),
  getCompanionGroup: (groupId: number) => request<any>(`/companions/groups/${groupId}`),
  getGroupMessages: (groupId: number) => request<any[]>(`/companions/groups/${groupId}/messages`),
  sendGroupMessage: (groupId: number, message: string) => request<any>(`/companions/groups/${groupId}/messages`, { method: 'POST', body: JSON.stringify({ message }) }),

  // Contacts
  getContacts: () => request<any[]>('/contacts/'),
  addContact: (body: any) => request<any>('/contacts/', { method: 'POST', body: JSON.stringify(body) }),
  deleteContact: (id: number) => request<void>(`/contacts/${id}`, { method: 'DELETE' }),

  // Emergency & SOS
  triggerSOS: (body: any) => request<any>('/alerts/sos', { method: 'POST', body: JSON.stringify(body) }),
  getAlerts: () => request<any[]>('/alerts/'),
  getActiveAlerts: () => request<any[]>('/alerts/active'),
  resolveAlert: (alertId: number, notes: string) => request<any>(`/alerts/${alertId}/resolve`, { method: 'POST', body: JSON.stringify({ resolution_notes: notes }) }),

  // LocationIQ Maps Client Helpers
  locationIQ: {
    getKey: () => {
      return (import.meta as any).env?.VITE_LOCATIONIQ_API_KEY || '';
    },
    autocomplete: async (query: string): Promise<Array<{ display_name: string; lat: number; lon: number }>> => {
      if (!query || query.trim().length < 2) return [];
      const key = (import.meta as any).env?.VITE_LOCATIONIQ_API_KEY || '';
      if (!key) return [];
      try {
        const resp = await fetch(`https://api.locationiq.com/v1/autocomplete?key=${key}&q=${encodeURIComponent(query)}&limit=5&format=json`);
        if (!resp.ok) return [];
        const data = await resp.json();
        return (data || []).map((item: any) => ({
          display_name: item.display_name,
          lat: parseFloat(item.lat),
          lon: parseFloat(item.lon),
        }));
      } catch (e) {
        console.warn('LocationIQ autocomplete failed:', e);
        return [];
      }
    },
    reverseGeocode: async (lat: number, lon: number): Promise<string> => {
      const key = (import.meta as any).env?.VITE_LOCATIONIQ_API_KEY || '';
      if (!key) return `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
      try {
        const resp = await fetch(`https://us1.locationiq.com/v1/reverse?key=${key}&lat=${lat}&lon=${lon}&format=json`);
        if (!resp.ok) return `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
        const data = await resp.json();
        return data.display_name || `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
      } catch {
        return `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
      }
    }
  }
};

