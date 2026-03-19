import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import type { Barbershop } from '../../types';

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export default function BarbershopsListPage() {
  const navigate = useNavigate();
  const { user, selectTenant } = useAuth();
  const [barbershops, setBarbershops] = useState<Barbershop[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(`${BASE}/public/barbershops`)
      .then((r) => r.json())
      .then((data) => setBarbershops(Array.isArray(data) ? data : []))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  function handleSelectBarbershop(shop: Barbershop) {
    selectTenant(String(shop.tenant_id), shop.nome);
    if (user?.role.split(',').includes('client')) {
      navigate('/client');
      return;
    }
    navigate(`/book/${shop.tenant_id}`);
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex flex-col">
      {/* Hero */}
      <div className="relative flex flex-col items-center justify-center px-6 pt-20 pb-16 text-center overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(245,158,11,0.12)_0%,_transparent_65%)]" />

        <div className="relative z-10">
          {/* Scissors icon */}
          <div className="mb-6 flex justify-center">
            <div className="h-16 w-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-8 h-8 text-amber-400">
                <circle cx="6" cy="6" r="3" />
                <circle cx="6" cy="18" r="3" />
                <line x1="20" y1="4" x2="8.12" y2="15.88" />
                <line x1="14.47" y1="14.48" x2="20" y2="20" />
                <line x1="8.12" y1="8.12" x2="12" y2="12" />
              </svg>
            </div>
          </div>

          <h1 className="text-4xl font-bold text-white tracking-tight mb-3">
            Barber<span className="text-amber-400">Pro</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-xs mx-auto">
            Agenda servicos de barbearia, grooming e estetica complementar num so lugar
          </p>

          <div className="mt-6 flex items-center justify-center gap-3 text-slate-600">
            <div className="w-10 h-px bg-slate-800" />
            <span className="text-xs uppercase tracking-widest text-slate-600">Escolhe a tua barbearia</span>
            <div className="w-10 h-px bg-slate-800" />
          </div>
        </div>
      </div>

      {/* List */}
      <div className="flex-1 flex flex-col items-center px-4 pb-12">
        <div className="w-full max-w-sm space-y-3">
          {loading && (
            <div className="flex justify-center py-16">
              <div className="h-8 w-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {error && (
            <p className="text-center text-slate-500 py-16">Erro ao carregar barbearias.</p>
          )}

          {!loading && !error && barbershops.length === 0 && (
            <p className="text-center text-slate-500 py-16">Nenhuma barbearia disponivel.</p>
          )}

          {!loading && !error && barbershops.map((shop) => (
            <button
              key={shop.id}
              type="button"
              onClick={() => handleSelectBarbershop(shop)}
              className="flex items-center gap-4 w-full rounded-2xl border border-slate-800 bg-slate-900 p-5 hover:border-amber-500/40 hover:bg-slate-800/60 transition-all group text-left cursor-pointer"
            >
              {/* Avatar */}
              <div className="shrink-0 h-12 w-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 font-bold text-xl group-hover:bg-amber-500/20 transition-colors">
                {shop.nome.charAt(0).toUpperCase()}
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <p className="text-white font-semibold truncate group-hover:text-amber-400 transition-colors">
                  {shop.nome}
                </p>
                <p className="text-slate-500 text-sm mt-0.5">Clica para marcar</p>
              </div>

              {/* Arrow */}
              <div className="shrink-0 h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-500 group-hover:bg-amber-500 group-hover:border-amber-500 group-hover:text-slate-900 transition-all">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
