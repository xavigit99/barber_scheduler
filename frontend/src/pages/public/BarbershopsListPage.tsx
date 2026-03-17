import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import type { Barbershop } from '../../types';

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export default function BarbershopsListPage() {
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

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center px-4 py-10">
      <div className="w-full max-w-sm">
        {/* Brand */}
        <div className="mb-2 flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-amber-500 flex items-center justify-center text-slate-900 font-bold text-sm">
            B
          </div>
          <span className="text-white font-semibold text-lg">BarberPro</span>
        </div>

        <div className="mb-8 flex items-center justify-between">
          <p className="text-sm text-slate-400">Escolhe a tua barbearia</p>
          <Link to="/login" className="text-sm text-slate-400 hover:text-amber-400 transition-colors">
            Área profissional →
          </Link>
        </div>

        {loading && (
          <div className="flex justify-center py-16">
            <div className="h-8 w-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {error && (
          <p className="text-center text-slate-500 py-16">Erro ao carregar barbearias.</p>
        )}

        {!loading && !error && barbershops.length === 0 && (
          <p className="text-center text-slate-500 py-16">Nenhuma barbearia registada.</p>
        )}

        {!loading && !error && barbershops.length > 0 && (
          <div className="space-y-3">
            {barbershops.map((shop) => (
              <Link
                key={shop.id}
                to={`/book/${shop.tenant_id}`}
                className="flex items-center justify-between w-full rounded-xl border border-slate-700 bg-slate-800 p-5 hover:border-amber-500/60 transition-colors group"
              >
                <div className="flex items-center gap-4">
                  <div className="h-10 w-10 rounded-full bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 font-bold text-lg">
                    {shop.nome.charAt(0).toUpperCase()}
                  </div>
                  <span className="text-white font-medium group-hover:text-amber-400 transition-colors">
                    {shop.nome}
                  </span>
                </div>
                <span className="text-slate-500 group-hover:text-amber-400 transition-colors text-xl">→</span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
