import { useState, useEffect, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import api, { getApiError } from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';
import Table from '../../components/Table';
import Button from '../../components/Button';
import Modal from '../../components/Modal';
import Input from '../../components/Input';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';

interface Campaign {
  id: string;
  nome: string;
  subject: string;
  body_template: string;
  segment_filters: Record<string, unknown> | null;
  status: string;
  total_sent: number;
  created_at: string;
  sent_at: string | null;
}

export default function CampaignsPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();

  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({
    nome: '',
    subject: '',
    body_template: '',
    segment_filters: '',
  });

  async function load() {
    try {
      const res = await api.get('/campaigns');
      setCampaigns(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      toast(getApiError(err, 'Erro ao carregar campanhas'), 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    try {
      let filters = null;
      if (form.segment_filters.trim()) {
        filters = JSON.parse(form.segment_filters);
      }
      await api.post('/campaigns', {
        nome: form.nome,
        subject: form.subject,
        body_template: form.body_template,
        segment_filters: filters,
      });
      toast('Campanha criada', 'success');
      setModalOpen(false);
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao criar campanha'), 'error');
    }
  }

  async function handleSend(id: string) {
    if (!confirm('Enviar esta campanha? Esta acao nao pode ser desfeita.')) return;
    try {
      await api.post(`/campaigns/${id}/send`);
      toast('Campanha enviada', 'success');
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao enviar campanha'), 'error');
    }
  }

  function statusBadge(status: string) {
    if (status === 'sent') {
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">Enviada</span>;
    }
    return <span className="px-2 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-700">Rascunho</span>;
  }

  if (!tenantId) {
    return (
      <div className="py-12 text-center text-slate-500">
        Selecione um tenant em <Link to="/admin/barbershops" className="text-emerald-600 underline">Barbearias</Link> primeiro.
      </div>
    );
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-800">Campanhas</h1>
        <Button onClick={() => { setForm({ nome: '', subject: '', body_template: '', segment_filters: '' }); setModalOpen(true); }}>
          + Nova Campanha
        </Button>
      </div>

      <Table
        columns={[
          { key: 'nome', header: 'Nome', render: (c) => c.nome },
          { key: 'status', header: 'Estado', render: (c) => statusBadge(c.status) },
          { key: 'total_sent', header: 'Enviados', render: (c) => c.total_sent },
          { key: 'created_at', header: 'Criado em', render: (c) => new Date(c.created_at).toLocaleDateString('pt-PT') },
          { key: 'sent_at', header: 'Enviado em', render: (c) => c.sent_at ? new Date(c.sent_at).toLocaleDateString('pt-PT') : '-' },
          {
            key: 'actions',
            header: 'Acoes',
            render: (c) =>
              c.status === 'draft' ? (
                <Button size="sm" onClick={() => handleSend(c.id)}>Enviar</Button>
              ) : null,
          },
        ]}
        data={campaigns}
        keyExtractor={(c) => c.id}
        emptyMessage="Nenhuma campanha encontrada."
      />

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Nova Campanha">
        <form onSubmit={handleCreate} className="space-y-4">
          <Input
            label="Nome"
            value={form.nome}
            onChange={(e) => setForm({ ...form, nome: e.target.value })}
            required
            autoFocus
          />
          <Input
            label="Assunto"
            value={form.subject}
            onChange={(e) => setForm({ ...form, subject: e.target.value })}
            required
          />
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-slate-700">Corpo do Email</label>
            <textarea
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 min-h-[100px]"
              value={form.body_template}
              onChange={(e) => setForm({ ...form, body_template: e.target.value })}
              required
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-slate-700">Filtros de Segmento (JSON, opcional)</label>
            <textarea
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 min-h-[60px] font-mono text-xs"
              value={form.segment_filters}
              onChange={(e) => setForm({ ...form, segment_filters: e.target.value })}
              placeholder='{"inactive_days": 30}'
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Criar</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
