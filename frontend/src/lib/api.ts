/* ============================================================
   Axios instance with auth & tenant interceptors
   ============================================================ */

import axios from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';
import { getToken, getTenantId, clearAuth } from './auth';

declare module 'axios' {
  interface AxiosRequestConfig {
    skipTenantHeader?: boolean;
  }
  interface InternalAxiosRequestConfig {
    skipTenantHeader?: boolean;
  }
}

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

/* ---------- request: attach auth + tenant headers ---------- */
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  if (!config.skipTenantHeader) {
    const tenantId = getTenantId();
    if (tenantId) {
      config.headers['X-Tenant-Id'] = tenantId;
    }
  }

  return config;
});

/* ---------- response: handle 401 → redirect to login ---------- */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      clearAuth();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export default api;

export function getApiError(error: unknown, fallback = 'Ocorreu um erro inesperado'): string {
  if (!axios.isAxiosError(error)) return fallback;
  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((d: { msg?: string }) => d.msg ?? String(d)).join('; ');
  }
  return fallback;
}
