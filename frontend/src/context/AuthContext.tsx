import React, { createContext, useContext, useState, useEffect } from 'react';
import { api, getToken, setToken, removeToken } from '../api/client';

export interface User {
  id: number;
  name: string;
  email: string;
  verification_status: 'pending' | 'verified' | 'rejected';
  role: 'user' | 'admin';
  phone_number?: string;
  emergency_note?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: any) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
  isVerified: boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchProfile = async () => {
    try {
      const data = await api.getProfile();
      setUser(data);
    } catch (err) {
      removeToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (getToken()) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials: any) => {
    const res = await api.login(credentials);
    setToken(res.access_token);
    await fetchProfile();
  };

  const register = async (data: any) => {
    await api.register(data);
    await login({ email: data.email, password: data.password });
  };

  const logout = () => {
    removeToken();
    setUser(null);
  };

  const isVerified = user?.verification_status === 'verified';
  const isAdmin = user?.role === 'admin';

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      register,
      logout,
      refreshProfile: fetchProfile,
      isVerified,
      isAdmin,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

