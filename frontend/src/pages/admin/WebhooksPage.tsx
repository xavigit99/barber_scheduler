import { useState, useEffect, useCallback, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import api, { getApiError } from '../../lib/api';
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

const EVENT_LABELS: Record<string, string> = {
  'appointment.created': 'Criado',
  'appointment.cancelled': 'Cancelado',
  'appointment.rescheduled': 'Remarcado',
};

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('pt-PT', { day: '2-digit', month: 'short', year: 'numeric' });
}

export default function WebhooksPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();

  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [loading, setLoading] = useState(true);
  const [testingId, setTestingId] = useState<number | null>(null);

  /* create modal */
  const [modalOpen, setModalOpen] = useState(false);
  const [url, setUrl] = useState('');
  const [secret, setSecret] = useState('');
  const [secretCopied, setSecretCopied] = useState(false);
  const [selectedEvents, setSelectedEvents] = useState<string[]>([]);

  const fetchWebhooks = useCallback(async () => {
    try {
      const res = await api.get('/admin/webhooks');
      setWebhooks(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      toast(getApiError(err, 'Erro ao carregar webhooks'), 'error');
    }
  }, [toast]);

  useEffect(() => {
    if (!tenantId) return;
    setLoading(true);
    fetchWebhooks().finally(() => setLoading(false));
  }, [tenantId, fetchWebhooks]);

  function toggleEvent(event: string) {
    setSelectedEvents((prev) =>
      prev.includes(event) ? prev.filter((e) => e !== event) : [...prev, event],
    );
  }

  function generateSecret() {
    const array = new Uint8Array(24);
    crypto.getRandomValues(array);
    const generated = Array.from(array, (b) => b.toString(16).padStart(2, '0')).join('');
    setSecret(generated);
    setSecretCopied(false);
  }

  async function copySecret() {
    try {
      await navigator.clipboard.writeText(secret);
      setSecretCopied(true);
      setTimeout(() => setSecretCopied(false), 2000);
    } catch (err) {
      toast(getApiError(err, 'Erro ao copiar'), 'error');
    }
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    try {
      await api.post('/admin/webhooks', { url, secret, events: selectedEvents });
      toast('Webhook criado', 'success');
      setModalOpen(false);
      setUrl('');
      setSecret('');
      setSecretCopied(false);
      setSelectedEvents([]);
      await fetchWebhooks();
    } catch (err) {
      toast(getApiError(err, 'Erro ao criar webhook'), 'error');
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('Remover webhook?')) return;
    try {
      await api.delete(`/admin/webhooks/${id}`);
      toast('Webhook removido', 'success');
      setWebhooks((prev) => prev.filter((w) => w.id !== id));
    } catch (err) {
      toast(getApiError(err, 'Erro ao remover webhook'), 'error');
    }
  }

  async function handleTest(id: number) {
    setTestingId(id);
    try {
      await api.post(`/admin/webhooks/${id}/test`);
      toast('Ping enviado com sucesso', 'success');
    } catch (err) {
      toast(getApiError(err, 'Erro ao testar webhook'), 'error');
    } finally {
      setTestingId(null);
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
          {
            key: 'events',
            header: 'Eventos',
            render: (w) =>
              w.events.map((evt) => EVENT_LABELS[evt] ?? evt).join(', '),
          },
          {
            key: 'secret',
            header: 'Secret',
            render: () => (
              <span className="text-xs text-slate-500 italic">Secret configurado</span>
            ),
          },
          {
            key: 'created_at',
            header: 'Criado em',
            render: (w) => formatDate(w.created_at),
          },
          {
            key: 'actions',
            header: 'Ações',
            render: (w) => (
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => handleTest(w.id)}
                  disabled={testingId === w.id}
                >
                  {testingId === w.id ? 'Enviando...' : 'Testar'}
                </Button>
                <Button size="sm" variant="danger" onClick={() => handleDelete(w.id)}>
                  Remover
                </Button>
              </div>
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

          {/* Secret with generate + copy */}
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Secret</label>
            <div className="flex items-center gap-2">
              <input
                type="text"
                readOnly
                value={secret}
                placeholder="Clique em Gerar para criar um secret"
                className="flex-1 rounded border border-slate-300 bg-slate-50 px-3 py-2 text-sm font-mono text-slate-700 focus:outline-none"
              />
              <Button type="button" size="sm" variant="secondary" onClick={generateSecret}>
                Gerar
              </Button>
              {secret && (
                <Button type="button" size="sm" variant="secondary" onClick={copySecret}>
                  {secretCopied ? 'Copiado!' : 'Copiar'}
                </Button>
              )}
            </div>
            {secret && (
              <p className="mt-1 text-xs text-amber-600">
                Guarde este secret — ele não será exibido novamente.
              </p>
            )}
          </div>

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
                {EVENT_LABELS[evt] ?? evt} <span className="text-xs text-slate-400">({evt})</span>
              </label>
            ))}
          </fieldset>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)} type="button">
              Cancelar
            </Button>
            <Button type="submit" disabled={!secret}>Criar</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
