/* ============================================================
   AuthContext — provides user, tenantId, clientId, barberId, login/logout globally
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
  clientId: number | null;
  barberId: number | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<User>;
  logout: () => void;
  selectTenant: (id: string) => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

async function resolveClientProfile(): Promise<{ clientId: number; tenantId: string } | null> {
  try {
    const res = await api.get('/clients/me');
    return { clientId: res.data.id, tenantId: String(res.data.tenant_id) };
  } catch {
    return null;
  }
}

async function resolveBarberProfile(): Promise<{ barberId: number; tenantId: string } | null> {
  try {
    const res = await api.get('/barbers/me');
    return { barberId: res.data.id, tenantId: String(res.data.tenant_id) };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(getUser);
  const [tenantId, setTenantId] = useState<string | null>(getTenantId);
  const [clientId, setClientId] = useState<number | null>(null);
  const [barberId, setBarberId] = useState<number | null>(null);
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
      .then(async (res) => {
        const u: User = res.data;
        setUser(u);
        if (u.role === 'client') {
          const profile = await resolveClientProfile();
          if (profile) {
            setClientId(profile.clientId);
            if (!getTenantId()) {
              storeTenantId(profile.tenantId);
              setTenantId(profile.tenantId);
            }
          }
        } else if (u.role === 'barber') {
          const profile = await resolveBarberProfile();
          if (profile) {
            setBarberId(profile.barberId);
            if (!getTenantId()) {
              storeTenantId(profile.tenantId);
              setTenantId(profile.tenantId);
            }
          }
        }
      })
      .catch(() => {
        clearAuth();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const login = useCallback(async (username: string, password: string): Promise<User> => {
    const res = await api.post('/auth/login', { username, password });
    const { access_token, user: userData } = res.data;
    saveAuth(access_token, userData);
    setUser(userData);

    if (userData.role === 'client') {
      const profile = await resolveClientProfile();
      if (profile) {
        setClientId(profile.clientId);
        storeTenantId(profile.tenantId);
        setTenantId(profile.tenantId);
      }
    } else if (userData.role === 'barber') {
      const profile = await resolveBarberProfile();
      if (profile) {
        setBarberId(profile.barberId);
        storeTenantId(profile.tenantId);
        setTenantId(profile.tenantId);
      }
    }

    return userData;
  }, []);

  const logout = useCallback(() => {
    clearAuth();
    setUser(null);
    setTenantId(null);
    setClientId(null);
    setBarberId(null);
  }, []);

  const selectTenant = useCallback((id: string) => {
    storeTenantId(id);
    setTenantId(id);
  }, []);

  return (
    <AuthContext.Provider value={{ user, tenantId, clientId, barberId, loading, login, logout, selectTenant }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
