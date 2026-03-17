import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../lib/api';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
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
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [barbers, setBarbers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
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
      } catch {
        toast('Erro ao carregar avaliações', 'error');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) return <Spinner />;

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Minhas Avaliações</h1>

      {feedback.length === 0 ? (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-8 text-center">
          <p className="text-slate-500 mb-4">Ainda não tens avaliações.</p>
          <Link
            to="/client/appointments"
            className="inline-block rounded-lg bg-emerald-600 px-4 py-2 text-sm text-white hover:bg-emerald-700 transition-colors"
          >
            Ver os meus agendamentos
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {feedback.map((f) => (
            <div
              key={f.id}
              className="rounded-lg border border-slate-200 bg-white p-4 space-y-2"
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
                <p className="text-sm text-slate-700 italic">"{f.comentario}"</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
