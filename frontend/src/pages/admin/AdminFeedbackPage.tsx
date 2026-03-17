import { useState, useEffect } from 'react';
import api from '../../lib/api';
import Spinner from '../../components/Spinner';
import Table from '../../components/Table';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../contexts/AuthContext';
import type { Feedback } from '../../types';

const STARS = ['', '★', '★★', '★★★', '★★★★', '★★★★★'];

export default function AdminFeedbackPage() {
  const { toast } = useToast();
  const { tenantId } = useAuth();
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!tenantId) return;
    api
      .get('/admin/feedback')
      .then((res) => setFeedback(Array.isArray(res.data) ? res.data : []))
      .catch(() => toast('Erro ao carregar avaliações', 'error'))
      .finally(() => setLoading(false));
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!tenantId) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
        Seleciona uma barbearia para ver as avaliações.
      </div>
    );
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Avaliações</h1>
      {loading ? (
        <Spinner />
      ) : (
        <Table
          columns={[
            {
              key: 'date',
              header: 'Data',
              render: (f) => new Date(f.created_at).toLocaleDateString('pt-PT'),
            },
            {
              key: 'rating',
              header: 'Classificação',
              render: (f) => (
                <span className="text-amber-400 font-medium">{STARS[f.rating] ?? f.rating}</span>
              ),
            },
            {
              key: 'barber',
              header: 'Barbeiro ID',
              render: (f) => <span className="font-mono text-xs">{String(f.barber_id).slice(0, 8)}</span>,
            },
            {
              key: 'client',
              header: 'Cliente ID',
              render: (f) => <span className="font-mono text-xs">{String(f.client_id).slice(0, 8)}</span>,
            },
            {
              key: 'comentario',
              header: 'Comentário',
              render: (f) => f.comentario ?? <span className="text-slate-400 italic">—</span>,
            },
          ]}
          data={feedback}
          keyExtractor={(f) => f.id}
          emptyMessage="Nenhuma avaliação encontrada."
        />
      )}
    </div>
  );
}
