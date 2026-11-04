const API_BASE = '/api/v1';

export function getToken(): string | null {
  return localStorage.getItem('safira_token');
}

export function setToken(token: string) {
  localStorage.setItem('safira_token', token);
}

export function removeToken() {
  localStorage.removeItem('safira_token');
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

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return {} as T;
  }

  const data = await response.json();
  if (!response.ok) {
    const errorMsg = data.detail || 'An unexpected error occurred.';
    throw new Error(errorMsg);
  }

  return data;
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
  updateJourneyStatus: (id: number, status: string) => request<any>(`/journeys/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) }),

  // Tracking & Deviation
  recordLocation: (journeyId: number, body: any) => request<any>(`/tracking/${journeyId}/location`, { method: 'POST', body: JSON.stringify(body) }),
  resolveDeviation: (journeyId: number, body: any) => request<any>(`/tracking/${journeyId}/resolve-deviation`, { method: 'POST', body: JSON.stringify(body) }),
  getLocationHistory: (journeyId: number) => request<any[]>(`/tracking/${journeyId}/history`),

  // Companions
  getMatches: (journeyId: number) => request<any[]>(`/companions/matches/${journeyId}`),
  sendCompanionRequest: (body: any) => request<any>('/companions/requests', { method: 'POST', body: JSON.stringify(body) }),
  getMyRequests: () => request<any[]>('/companions/requests'),
  updateRequestStatus: (requestId: number, status: string) => request<any>(`/companions/requests/${requestId}`, { method: 'PATCH', body: JSON.stringify({ status }) }),
  getCompanionGroup: (groupId: number) => request<any>(`/companions/groups/${groupId}`),

  // Contacts
  getContacts: () => request<any[]>('/contacts/'),
  addContact: (body: any) => request<any>('/contacts/', { method: 'POST', body: JSON.stringify(body) }),
  deleteContact: (id: number) => request<void>(`/contacts/${id}`, { method: 'DELETE' }),

  // Emergency & SOS
  triggerSOS: (body: any) => request<any>('/alerts/sos', { method: 'POST', body: JSON.stringify(body) }),
  getAlerts: () => request<any[]>('/alerts/'),
  resolveAlert: (alertId: number, notes: string) => request<any>(`/alerts/${alertId}/resolve`, { method: 'POST', body: JSON.stringify({ resolution_notes: notes }) }),
};

