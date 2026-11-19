import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Shield, Compass, Users, Bell, User, LogOut, CheckCircle2, Clock, AlertTriangle, Menu, X 
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout, isVerified, isAdmin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const navLinks = [
    { label: 'Dashboard', path: '/dashboard', icon: Compass },
    { label: 'Create Journey', path: '/journeys/create', icon: Shield },
    { label: 'Journey Buddy', path: '/journey-buddy', icon: Users, verifiedOnly: true },
    { label: 'Requests', path: '/requests', icon: Bell },
    { label: 'Profile & Guardians', path: '/profile', icon: User },
  ];

  return (
    <nav className="bg-slate-900 border-b border-slate-800 text-slate-100 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <Link to={user ? "/dashboard" : "/"} className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-rose-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-rose-500/20 group-hover:scale-105 transition-transform">
              <Shield className="w-5 h-5 fill-white/20" />
            </div>
            <div>
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-rose-100 to-indigo-200 bg-clip-text text-transparent">
                Safira
              </span>
              <span className="text-[10px] block -mt-1 font-medium text-slate-400">
                Women's Travel Safety
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          {user && (
            <div className="hidden md:flex items-center space-x-1 lg:space-x-2">
              {navLinks.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                const isLocked = item.verifiedOnly && !isVerified;

                return (
                  <Link
                    key={item.path}
                    to={isLocked ? '/verification' : item.path}
                    className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                      isActive 
                        ? 'bg-rose-500/15 text-rose-300 border border-rose-500/30' 
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                    {isLocked && (
                      <span className="text-[9px] bg-slate-800 text-amber-300 px-1.5 py-0.2 rounded border border-amber-500/30 ml-1">
                        Locked
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          )}

          {/* User Status / Actions */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-2.5">
                {/* Verification Badge */}
                <Link to="/verification" className="group">
                  {user.verification_status === 'verified' ? (
                    <div className="flex items-center gap-1.5 bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-xs px-2.5 py-1 rounded-full font-medium">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Verified Woman</span>
                    </div>
                  ) : user.verification_status === 'pending' ? (
                    <div className="flex items-center gap-1.5 bg-amber-950/60 border border-amber-500/40 text-amber-300 text-xs px-2.5 py-1 rounded-full font-medium">
                      <Clock className="w-3.5 h-3.5 text-amber-400" />
                      <span>Verification Pending</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1.5 bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs px-2.5 py-1 rounded-full font-medium">
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                      <span>Verify Eligibility</span>
                    </div>
                  )}
                </Link>

                {isAdmin && (
                  <Link
                    to="/admin/verification"
                    className="text-xs bg-indigo-950/70 border border-indigo-500/40 text-indigo-300 px-2.5 py-1 rounded-full font-medium hover:bg-indigo-900/60 transition"
                  >
                    Admin Review
                  </Link>
                )}

                <button
                  onClick={handleLogout}
                  className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-xl transition cursor-pointer"
                  title="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link
                  to="/auth?mode=login"
                  className="text-xs font-semibold text-slate-300 hover:text-white px-3 py-2 rounded-xl transition"
                >
                  Log In
                </Link>
                <Link
                  to="/auth?mode=register"
                  className="text-xs font-bold bg-rose-600 hover:bg-rose-500 text-white px-4 py-2 rounded-xl shadow-md shadow-rose-600/30 transition"
                >
                  Get Verified
                </Link>
              </div>
            )}
          </div>

          {/* Mobile hamburger button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-slate-400 hover:text-white"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && user && (
        <div className="md:hidden border-t border-slate-800 bg-slate-900 px-4 pt-2 pb-4 space-y-1">
          {navLinks.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white"
              >
                <Icon className="w-4 h-4 text-slate-400" />
                <span>{item.label}</span>
              </Link>
            );
          })}
          <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
            <Link
              to="/verification"
              onClick={() => setMobileMenuOpen(false)}
              className="text-xs text-amber-300"
            >
              Status: {user.verification_status}
            </Link>
            <button
              onClick={handleLogout}
              className="text-xs text-rose-400 font-semibold flex items-center gap-1"
            >
              <LogOut className="w-3.5 h-3.5" /> Sign Out
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};

