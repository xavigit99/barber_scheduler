/* ============================================================
   AuthContext — provides user, tenantId, login/logout globally
   ============================================================ */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react';
import api from '../lib/api';
import {
  saveAuth,
  clearAuth,
  getUser,
  getToken,
  getTenantId,
  setTenantId as storeTenantId,
} from '../lib/auth';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  tenantId: string | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<User>;
  logout: () => void;
  selectTenant: (id: string) => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(getUser);
  const [tenantId, setTenantId] = useState<string | null>(getTenantId);
  const [loading, setLoading] = useState(true);

  /* On mount, verify token is still valid */
  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get('/auth/me')
      .then((res) => setUser(res.data))
      .catch(() => {
        clearAuth();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (username: string, password: string): Promise<User> => {
    const res = await api.post('/auth/login', { username, password });
    const { access_token, user: userData } = res.data;
    saveAuth(access_token, userData);
    setUser(userData);
    return userData;
  }, []);

  const logout = useCallback(() => {
    clearAuth();
    setUser(null);
    setTenantId(null);
  }, []);

  const selectTenant = useCallback((id: string) => {
    storeTenantId(id);
    setTenantId(id);
  }, []);

  return (
    <AuthContext.Provider value={{ user, tenantId, loading, login, logout, selectTenant }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
