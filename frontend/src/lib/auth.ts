/* ============================================================
   Auth helpers — localStorage-based token & tenant management
   ============================================================ */

import type { User } from '../types';

const TOKEN_KEY = 'barber_token';
const TENANT_KEY = 'barber_tenant_id';
const TENANT_NAME_KEY = 'barber_tenant_name';
const USER_KEY = 'barber_user';

export function saveAuth(token: string, user: User, tenantId?: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  if (tenantId) {
    localStorage.setItem(TENANT_KEY, tenantId);
  }
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function getUser(): User | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function getTenantId(): string | null {
  return localStorage.getItem(TENANT_KEY);
}

export function setTenantId(id: string): void {
  localStorage.setItem(TENANT_KEY, id);
}

export function getTenantName(): string | null {
  return localStorage.getItem(TENANT_NAME_KEY);
}

export function setTenantName(name: string): void {
  localStorage.setItem(TENANT_NAME_KEY, name);
}

export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(TENANT_KEY);
  localStorage.removeItem(TENANT_NAME_KEY);
}
