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

interface Invoice {
  id: string;
  appointment_id: string;
  invoice_number: string | null;
  status: string;
  created_at: string;
  invoice_url: string | null;
}

export default function InvoicesPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();

  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({ appointment_id: '' });

  async function load() {
    try {
      const res = await api.get('/invoices');
      setInvoices(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      toast(getApiError(err, 'Erro ao carregar faturas'), 'error');
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
      await api.post('/invoices', { appointment_id: form.appointment_id });
      toast('Fatura criada', 'success');
      setModalOpen(false);
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao criar fatura'), 'error');
    }
  }

  function statusBadge(status: string) {
    if (status === 'sent') {
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">Enviada</span>;
    }
    return <span className="px-2 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600">Rascunho</span>;
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
        <h1 className="text-2xl font-semibold text-slate-800">Faturas</h1>
        <Button onClick={() => { setForm({ appointment_id: '' }); setModalOpen(true); }}>
          + Nova Fatura
        </Button>
      </div>

      <Table
        columns={[
          { key: 'id', header: 'ID', render: (i) => i.id.slice(0, 8) },
          { key: 'appointment', header: 'Agendamento', render: (i) => i.appointment_id.slice(0, 8) },
          { key: 'number', header: 'Numero', render: (i) => i.invoice_number ?? '-' },
          { key: 'status', header: 'Estado', render: (i) => statusBadge(i.status) },
          { key: 'created', header: 'Criado em', render: (i) => new Date(i.created_at).toLocaleDateString('pt-PT') },
          {
            key: 'url',
            header: 'URL',
            render: (i) =>
              i.invoice_url ? (
                <a href={i.invoice_url} target="_blank" rel="noopener noreferrer" className="text-emerald-600 underline text-sm">
                  Ver
                </a>
              ) : (
                '-'
              ),
          },
        ]}
        data={invoices}
        keyExtractor={(i) => i.id}
        emptyMessage="Nenhuma fatura encontrada."
      />

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Nova Fatura">
        <form onSubmit={handleCreate} className="space-y-4">
          <Input
            label="ID do Agendamento"
            value={form.appointment_id}
            onChange={(e) => setForm({ appointment_id: e.target.value })}
            required
            autoFocus
            placeholder="UUID do agendamento"
          />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Criar</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
