import { useState, useEffect } from 'react';
import api, { getApiError } from '../../lib/api';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';

interface ClientPack {
  id: string;
  pack_nome: string;
  service_nome: string;
  sessoes_restantes: number;
  expira_em: string | null;
}

export default function MyPacksPage() {
  const { toast } = useToast();
  const [packs, setPacks] = useState<ClientPack[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get('/packs/me');
        setPacks(Array.isArray(res.data) ? res.data : []);
      } catch (err) {
        toast(getApiError(err, 'Erro ao carregar packs'), 'error');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) return <Spinner />;

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Os Meus Packs</h1>

      {packs.length === 0 ? (
        <div className="rounded-xl bg-white p-8 shadow-sm border border-slate-200 text-center">
          <p className="text-slate-400">Nao tem packs ativos de momento.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {packs.map((p) => (
            <div key={p.id} className="rounded-xl bg-white p-6 shadow-sm border border-slate-200">
              <h3 className="text-lg font-semibold text-slate-800 mb-2">{p.pack_nome ?? 'Pack'}</h3>
              <p className="text-sm text-slate-500 mb-4">{p.service_nome ?? 'Servico'}</p>
              <div className="flex items-baseline gap-1 mb-2">
                <span className="text-3xl font-bold text-emerald-600">{p.sessoes_restantes}</span>
                <span className="text-sm text-slate-500">sessoes restantes</span>
              </div>
              {p.expira_em && (
                <p className="text-xs text-slate-400">
                  Expira em {new Date(p.expira_em).toLocaleDateString('pt-PT')}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
