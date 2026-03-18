import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api, { getApiError } from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';
import Table from '../../components/Table';
import Button from '../../components/Button';
import Modal from '../../components/Modal';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';

interface AppointmentWithPayment {
  id: string;
  client_id: string;
  barber_id: string;
  service_id: string;
  start_at: string;
  payment_status: string;
}

const PAYMENT_STATUSES = [
  { value: '', label: 'Todos' },
  { value: 'not_required', label: 'Nao Requerido' },
  { value: 'pending', label: 'Pendente' },
  { value: 'paid', label: 'Pago' },
  { value: 'refunded', label: 'Reembolsado' },
];

export default function PaymentsPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();

  const [appointments, setAppointments] = useState<AppointmentWithPayment[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [checkoutUrl, setCheckoutUrl] = useState('');
  const [linkModalOpen, setLinkModalOpen] = useState(false);

  async function load() {
    try {
      const res = await api.get('/appointments/');
      setAppointments(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      toast(getApiError(err, 'Erro ao carregar agendamentos'), 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleGenerateLink(appointmentId: string) {
    try {
      const res = await api.post('/payments/checkout', { appointment_id: appointmentId });
      setCheckoutUrl(res.data.checkout_url ?? res.data.url ?? '');
      setLinkModalOpen(true);
    } catch (err) {
      toast(getApiError(err, 'Erro ao gerar link de pagamento'), 'error');
    }
  }

  function copyToClipboard() {
    navigator.clipboard.writeText(checkoutUrl).then(() => {
      toast('Link copiado', 'success');
    });
  }

  function statusBadge(status: string) {
    const styles: Record<string, string> = {
      not_required: 'bg-slate-100 text-slate-600',
      pending: 'bg-amber-100 text-amber-700',
      paid: 'bg-emerald-100 text-emerald-700',
      refunded: 'bg-red-100 text-red-700',
    };
    const labels: Record<string, string> = {
      not_required: 'Nao Requerido',
      pending: 'Pendente',
      paid: 'Pago',
      refunded: 'Reembolsado',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] ?? 'bg-slate-100 text-slate-600'}`}>
        {labels[status] ?? status}
      </span>
    );
  }

  const filtered = statusFilter
    ? appointments.filter((a) => a.payment_status === statusFilter)
    : appointments;

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
        <h1 className="text-2xl font-semibold text-slate-800">Pagamentos</h1>
        <div className="flex items-center gap-2">
          <label className="text-sm text-slate-600">Filtrar:</label>
          <select
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            {PAYMENT_STATUSES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </div>
      </div>

      <Table
        columns={[
          { key: 'id', header: 'ID', render: (a) => a.id.slice(0, 8) },
          { key: 'start', header: 'Data', render: (a) => new Date(a.start_at).toLocaleString('pt-PT') },
          { key: 'status', header: 'Estado Pagamento', render: (a) => statusBadge(a.payment_status ?? 'not_required') },
          {
            key: 'actions',
            header: 'Acoes',
            render: (a) =>
              (a.payment_status === 'pending') ? (
                <Button size="sm" onClick={() => handleGenerateLink(a.id)}>Gerar Link</Button>
              ) : null,
          },
        ]}
        data={filtered}
        keyExtractor={(a) => a.id}
        emptyMessage="Nenhum agendamento encontrado."
      />

      <Modal open={linkModalOpen} onClose={() => setLinkModalOpen(false)} title="Link de Pagamento">
        <div className="space-y-4">
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
            <p className="break-all text-sm font-mono text-slate-700">{checkoutUrl}</p>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setLinkModalOpen(false)}>Fechar</Button>
            <Button onClick={copyToClipboard}>Copiar Link</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
