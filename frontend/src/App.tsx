import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';

import { LandingPage } from './pages/LandingPage';
import { AuthPage } from './pages/AuthPage';
import { VerificationPage } from './pages/VerificationPage';
import { AdminVerificationPage } from './pages/AdminVerificationPage';
import { DashboardPage } from './pages/DashboardPage';
import { CreateJourneyPage } from './pages/CreateJourneyPage';
import { LiveJourneyPage } from './pages/LiveJourneyPage';
import { CompanionDiscoveryPage } from './pages/CompanionDiscoveryPage';
import { CompanionRequestsPage } from './pages/CompanionRequestsPage';
import { ActiveCompanionJourneyPage } from './pages/ActiveCompanionJourneyPage';
import { ProfileSettingsPage } from './pages/ProfileSettingsPage';

// Protected Route Guard
const ProtectedRoute: React.FC<{ children: React.ReactNode; verifiedOnly?: boolean }> = ({ 
  children, 
  verifiedOnly = false 
}) => {
  const { user, loading, isVerified } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-slate-400">
        Authenticating session...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/auth?mode=login" replace />;
  }

  if (verifiedOnly && !isVerified) {
    return <Navigate to="/verification" replace />;
  }

  return <>{children}</>;
};

export const AppContent: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <Navbar />
      <main className="flex-1">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth" element={<AuthPage />} />

          {/* Authenticated Routes */}
          <Route path="/verification" element={
            <ProtectedRoute>
              <VerificationPage />
            </ProtectedRoute>
          } />

          <Route path="/admin/verification" element={
            <ProtectedRoute>
              <AdminVerificationPage />
            </ProtectedRoute>
          } />

          <Route path="/dashboard" element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          } />

          <Route path="/journeys/create" element={
            <ProtectedRoute>
              <CreateJourneyPage />
            </ProtectedRoute>
          } />

          <Route path="/journeys/:id/live" element={
            <ProtectedRoute>
              <LiveJourneyPage />
            </ProtectedRoute>
          } />

          {/* Verified-Only Companion Routes */}
          <Route path="/journeys/:id/matches" element={
            <ProtectedRoute verifiedOnly>
              <CompanionDiscoveryPage />
            </ProtectedRoute>
          } />

          <Route path="/companions" element={
            <ProtectedRoute verifiedOnly>
              <DashboardPage />
            </ProtectedRoute>
          } />

          <Route path="/requests" element={
            <ProtectedRoute>
              <CompanionRequestsPage />
            </ProtectedRoute>
          } />

          <Route path="/companion-journey/:id" element={
            <ProtectedRoute verifiedOnly>
              <ActiveCompanionJourneyPage />
            </ProtectedRoute>
          } />

          <Route path="/profile" element={
            <ProtectedRoute>
              <ProfileSettingsPage />
            </ProtectedRoute>
          } />

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
};

export default App;
