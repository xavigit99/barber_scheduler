/* ============================================================
   Domain types — mirrors the backend API entities
   ============================================================ */

export type Role = 'admin' | 'barber' | 'client';

export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Barbershop {
  id: string;
  nome: string;
  owner_user_id: string;
  tenant_id: string;
}

export interface Barber {
  id: string;
  nome: string;
  email: string;
  telefone: string;
  tenant_id: string;
}

export interface Client {
  id: string;
  nome: string;
  email: string;
  telefone: string;
  tenant_id: string;
}

export interface Service {
  id: string;
  nome: string;
  duracao_minutos: number;
  preco: number;
  tenant_id: string;
}

export interface Appointment {
  id: string;
  barber_id: string;
  client_id: string;
  service_id: string;
  tenant_id: string;
  start_at: string;
  end_at: string;
  created_at: string;
  updated_at: string;
}

export interface AvailabilityWindow {
  id: string;
  barber_id: string;
  weekday: number;
  start_time: string;
  end_time: string;
}

export interface BarberBlock {
  id: string;
  barber_id: string;
  kind: string;
  start_at: string;
  end_at: string;
  reason: string | null;
}

export interface AvailableSlot {
  inicio: string;
  fim: string;
}

export interface PublicFeedback {
  id: string;
  barber_id: string;
  rating: number;
  comentario: string | null;
  created_at: string;
}

export interface Membership {
  id: number;
  barber_id: number;
  barbershop_id: number;
  role: string;
}

export interface Feedback {
  id: string;
  appointment_id: string;
  client_id: string;
  barber_id: string;
  tenant_id: string;
  rating: number;
  comentario: string | null;
  created_at: string;
}
