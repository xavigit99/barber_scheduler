/* ============================================================
   Axios instance with auth & tenant interceptors
   ============================================================ */

import axios from 'axios';
import { getToken, getTenantId, clearAuth } from './auth';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

/* ---------- request: attach auth + tenant headers ---------- */
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  const tenantId = getTenantId();
  if (tenantId) {
    config.headers['X-Tenant-Id'] = tenantId;
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
