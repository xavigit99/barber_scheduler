import { useState, useEffect } from 'react';
import api, { getApiError } from '../../lib/api';
import ClientEmptyState from '../../components/ClientEmptyState';
import ClientPageHeader from '../../components/ClientPageHeader';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../contexts/AuthContext';
import type { Feedback } from '../../types';

function StarDisplay({ rating }: { rating: number }) {
  const r = Math.round(rating);
  return (
    <span className="text-amber-400">
      {'★'.repeat(r)}{'☆'.repeat(5 - r)}
    </span>
  );
}

export default function MyFeedbackPage() {
  const { toast } = useToast();
  const { tenantId } = useAuth();
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [barbers, setBarbers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!tenantId) {
      setFeedback([]);
      setBarbers({});
      setLoading(false);
      return;
    }

    async function load() {
      setLoading(true);
      try {
        const [fRes, bRes] = await Promise.all([
          api.get('/feedback/me'),
          api.get('/barbers/'),
        ]);
        setFeedback(Array.isArray(fRes.data) ? fRes.data : []);
        const bMap: Record<string, string> = {};
        (Array.isArray(bRes.data) ? bRes.data : []).forEach((b: { id: string; nome: string }) => {
          bMap[String(b.id)] = b.nome;
        });
        setBarbers(bMap);
      } catch (err) {
        toast(getApiError(err, 'Erro ao carregar avaliações'), 'error');
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
        message="Escolhe primeiro a barbearia onde queres consultar as tuas avaliacoes."
        linkTo="/barbershops"
        linkLabel="Ver barbearias"
      />
    );
  }

  return (
    <div>
      <ClientPageHeader
        title="Minhas Avaliações"
        description="Revê os comentários e classificações que já deixaste aos teus atendimentos."
      />

      {feedback.length === 0 ? (
        <ClientEmptyState
          message="Ainda não tens avaliações."
          linkTo="/client/appointments"
          linkLabel="Ver os meus agendamentos"
        />
      ) : (
        <div className="space-y-3">
          {feedback.map((f) => (
            <div
              key={f.id}
              className="rounded-2xl border border-slate-200 bg-white p-5 space-y-3 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <StarDisplay rating={f.rating} />
                <span className="text-xs text-slate-400">
                  {new Date(f.created_at).toLocaleDateString('pt-PT')}
                </span>
              </div>
              <div className="text-sm text-slate-500">
                Barbeiro: <span className="font-medium text-slate-700">{barbers[String(f.barber_id)] ?? `#${f.barber_id}`}</span>
              </div>
              {f.comentario && (
                <p className="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-700 italic">"{f.comentario}"</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
