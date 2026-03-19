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
  id: string | number;
  client_id: string | number;
  barber_id: string | number;
  service_id: string | number;
  start_at: string;
  payment_status: string;
  payment_method?: string | null;
}

const PAYMENT_STATUSES = [
  { value: '', label: 'Todos' },
  { value: 'not_required', label: 'Nao Requerido' },
  { value: 'pending', label: 'Pendente' },
  { value: 'paid', label: 'Pago' },
  { value: 'refunded', label: 'Reembolsado' },
];

const PAYMENT_METHODS = [
  { value: 'cash', label: 'Dinheiro' },
  { value: 'mbway', label: 'MB Way' },
  { value: 'multibanco', label: 'Multibanco' },
  { value: 'card_terminal', label: 'Terminal' },
  { value: 'bank_transfer', label: 'Transferencia' },
];

export default function PaymentsPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();

  const [appointments, setAppointments] = useState<AppointmentWithPayment[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [editing, setEditing] = useState<AppointmentWithPayment | null>(null);
  const [paymentStatus, setPaymentStatus] = useState('pending');
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [saving, setSaving] = useState(false);

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

  function openPaymentModal(appointment: AppointmentWithPayment) {
    setEditing(appointment);
    setPaymentStatus(appointment.payment_status ?? 'pending');
    setPaymentMethod(appointment.payment_method ?? 'cash');
  }

  async function handleSavePayment() {
    if (!editing) return;
    try {
      setSaving(true);
      await api.patch(`/payments/appointments/${editing.id}`, {
        payment_status: paymentStatus,
        payment_method: paymentStatus === 'not_required' ? null : paymentMethod,
      });
      toast('Pagamento atualizado com sucesso', 'success');
      setEditing(null);
      await load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao atualizar pagamento'), 'error');
    } finally {
      setSaving(false);
    }
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

  function methodLabel(method?: string | null) {
    const labels: Record<string, string> = {
      cash: 'Dinheiro',
      mbway: 'MB Way',
      multibanco: 'Multibanco',
      card_terminal: 'Terminal',
      bank_transfer: 'Transferencia',
    };
    return method ? labels[method] ?? method : '—';
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
          { key: 'id', header: 'ID', render: (a) => String(a.id).slice(0, 8) },
          { key: 'start', header: 'Data', render: (a) => new Date(a.start_at).toLocaleString('pt-PT') },
          { key: 'method', header: 'Metodo', render: (a) => methodLabel(a.payment_method) },
          { key: 'status', header: 'Estado Pagamento', render: (a) => statusBadge(a.payment_status ?? 'not_required') },
          {
            key: 'actions',
            header: 'Acoes',
            render: (a) => (
              <Button size="sm" onClick={() => openPaymentModal(a)}>Atualizar</Button>
            ),
          },
        ]}
        data={filtered}
        keyExtractor={(a) => String(a.id)}
        emptyMessage="Nenhum agendamento encontrado."
      />

      <Modal open={Boolean(editing)} onClose={() => setEditing(null)} title="Atualizar Pagamento">
        <div className="space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">Estado</label>
            <select
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800"
              value={paymentStatus}
              onChange={(e) => setPaymentStatus(e.target.value)}
            >
              {PAYMENT_STATUSES.filter((status) => status.value).map((status) => (
                <option key={status.value} value={status.value}>{status.label}</option>
              ))}
            </select>
          </div>

          {paymentStatus !== 'not_required' && (
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Metodo</label>
              <select
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800"
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
              >
                {PAYMENT_METHODS.map((method) => (
                  <option key={method.value} value={method.value}>{method.label}</option>
                ))}
              </select>
            </div>
          )}

          <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
            Regista pagamentos locais da barbearia como dinheiro, MB Way, multibanco, terminal ou transferencia.
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setEditing(null)} disabled={saving}>Fechar</Button>
            <Button onClick={handleSavePayment} disabled={saving}>
              {saving ? 'A guardar...' : 'Guardar'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
