import { useState, useEffect, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import api from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';
import Table from '../../components/Table';
import Button from '../../components/Button';
import Modal from '../../components/Modal';
import Input from '../../components/Input';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';

interface Webhook {
  id: number;
  tenant_id: number;
  url: string;
  events: string[];
  created_at: string;
}

const AVAILABLE_EVENTS = [
  'appointment.created',
  'appointment.cancelled',
  'appointment.rescheduled',
];

export default function WebhooksPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();

  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [loading, setLoading] = useState(true);

  /* create modal */
  const [modalOpen, setModalOpen] = useState(false);
  const [url, setUrl] = useState('');
  const [secret, setSecret] = useState('');
  const [selectedEvents, setSelectedEvents] = useState<string[]>([]);

  useEffect(() => {
    if (!tenantId) return;
    setLoading(true);
    api
      .get('/admin/webhooks')
      .then((res) => setWebhooks(Array.isArray(res.data) ? res.data : []))
      .catch(() => toast('Erro ao carregar webhooks', 'error'))
      .finally(() => setLoading(false));
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  function toggleEvent(event: string) {
    setSelectedEvents((prev) =>
      prev.includes(event) ? prev.filter((e) => e !== event) : [...prev, event],
    );
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    try {
      await api.post('/admin/webhooks', { url, secret, events: selectedEvents });
      toast('Webhook criado', 'success');
      setModalOpen(false);
      setUrl('');
      setSecret('');
      setSelectedEvents([]);
      const res = await api.get('/admin/webhooks');
      setWebhooks(Array.isArray(res.data) ? res.data : []);
    } catch (err: unknown) {
      const detail =
        typeof err === 'object' && err !== null && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      toast(detail ?? 'Erro ao criar webhook', 'error');
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('Remover webhook?')) return;
    try {
      await api.delete(`/admin/webhooks/${id}`);
      toast('Webhook removido', 'success');
      setWebhooks((prev) => prev.filter((w) => w.id !== id));
    } catch {
      toast('Erro ao remover webhook', 'error');
    }
  }

  if (!tenantId) {
    return (
      <div className="py-12 text-center text-slate-500">
        <p className="mb-2 rounded bg-amber-50 px-4 py-3 text-amber-700 inline-block">
          Selecione um tenant em{' '}
          <Link to="/admin/barbershops" className="text-emerald-600 underline">
            Barbearias
          </Link>{' '}
          primeiro.
        </p>
      </div>
    );
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-800">Webhooks</h1>
        <Button onClick={() => setModalOpen(true)}>+ Novo Webhook</Button>
      </div>

      <Table
        columns={[
          { key: 'url', header: 'URL', render: (w) => w.url },
          { key: 'events', header: 'Eventos', render: (w) => w.events.join(', ') },
          {
            key: 'actions',
            header: 'Acoes',
            render: (w) => (
              <Button size="sm" variant="danger" onClick={() => handleDelete(w.id)}>
                Remover
              </Button>
            ),
          },
        ]}
        data={webhooks}
        keyExtractor={(w) => String(w.id)}
        emptyMessage="Nenhum webhook configurado."
      />

      {/* Create modal */}
      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Novo Webhook">
        <form onSubmit={handleCreate} className="space-y-4">
          <Input
            label="URL"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
            placeholder="https://example.com/webhook"
          />
          <Input
            label="Secret"
            type="password"
            value={secret}
            onChange={(e) => setSecret(e.target.value)}
            required
          />
          <fieldset>
            <legend className="mb-2 text-sm font-medium text-slate-700">Eventos</legend>
            {AVAILABLE_EVENTS.map((evt) => (
              <label key={evt} className="flex items-center gap-2 py-1 text-sm text-slate-600">
                <input
                  type="checkbox"
                  checked={selectedEvents.includes(evt)}
                  onChange={() => toggleEvent(evt)}
                  className="rounded border-slate-300"
                />
                {evt}
              </label>
            ))}
          </fieldset>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)} type="button">
              Cancelar
            </Button>
            <Button type="submit">Criar</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
