import { useState, useEffect } from 'react';
import ClientEmptyState from '../../components/ClientEmptyState';
import ClientPageHeader from '../../components/ClientPageHeader';
import api, { getApiError } from '../../lib/api';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../contexts/AuthContext';

interface ClientPack {
  id: string;
  pack_nome: string;
  service_nome: string;
  sessoes_restantes: number;
  expira_em: string | null;
}

export default function MyPacksPage() {
  const { toast } = useToast();
  const { tenantId } = useAuth();
  const [packs, setPacks] = useState<ClientPack[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!tenantId) {
      setPacks([]);
      setLoading(false);
      return;
    }

    async function load() {
      setLoading(true);
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
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) return <Spinner />;

  if (!tenantId) {
    return (
      <ClientEmptyState
        message="Escolhe primeiro a barbearia onde queres consultar os teus packs."
        linkTo="/barbershops"
        linkLabel="Ver barbearias"
      />
    );
  }

  return (
    <div>
      <ClientPageHeader
        title="Os Meus Packs"
        description="Consulta rapidamente os packs ativos e quantas sessões ainda tens disponíveis nesta barbearia."
      />

      {packs.length === 0 ? (
        <ClientEmptyState message="Nao tens packs ativos de momento." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {packs.map((p) => (
            <div key={p.id} className="rounded-2xl bg-white p-6 shadow-sm border border-slate-200">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">Pack Ativo</p>
              <h3 className="mt-3 text-lg font-semibold text-slate-800">{p.pack_nome ?? 'Pack'}</h3>
              <p className="mt-1 text-sm text-slate-500">{p.service_nome ?? 'Servico'}</p>
              <div className="flex items-baseline gap-1 mb-2">
                <span className="mt-5 text-3xl font-bold text-emerald-600">{p.sessoes_restantes}</span>
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
