import { useState, useEffect, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import api from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';
import Table from '../../components/Table';
import Button from '../../components/Button';
import Modal from '../../components/Modal';
import Input from '../../components/Input';
import Select from '../../components/Select';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import type { Barber, Client, Service, Appointment } from '../../types';

export default function AppointmentsPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();

  const [barbers, setBarbers] = useState<Barber[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingAppts, setLoadingAppts] = useState(false);

  const [selectedBarber, setSelectedBarber] = useState('');
  const [targetDate, setTargetDate] = useState(() => new Date().toISOString().split('T')[0]);

  /* create modal */
  const [modalOpen, setModalOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    barber_id: '',
    client_id: '',
    service_id: '',
    data_inicio: '',
  });
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurrence, setRecurrence] = useState<'weekly' | 'biweekly'>('weekly');
  const [recurrenceCount, setRecurrenceCount] = useState(4);

  /* load reference data */
  useEffect(() => {
    async function load() {
      try {
        const [bRes, cRes, sRes] = await Promise.all([
          api.get('/barbers/'),
          api.get('/clients/'),
          api.get('/services/'),
        ]);
        const b = Array.isArray(bRes.data) ? bRes.data : [];
        setBarbers(b);
        setClients(Array.isArray(cRes.data) ? cRes.data : []);
        setServices(Array.isArray(sRes.data) ? sRes.data : []);
        if (b.length > 0) setSelectedBarber(b[0].id);
      } catch {
        toast('Erro ao carregar dados', 'error');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  /* load appointments for selected barber + date */
  useEffect(() => {
    if (!selectedBarber || !targetDate) return;
    setLoadingAppts(true);
    api
      .get(`/appointments/barbers/${selectedBarber}?target_date=${targetDate}`)
      .then((res) => setAppointments(Array.isArray(res.data) ? res.data : []))
      .catch(() => setAppointments([]))
      .finally(() => setLoadingAppts(false));
  }, [selectedBarber, targetDate]);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    try {
      if (isRecurring) {
        const res = await api.post('/appointments/recurring', {
          barber_id: Number(createForm.barber_id),
          client_id: Number(createForm.client_id),
          service_id: Number(createForm.service_id),
          data_inicio: createForm.data_inicio,
          recurrence,
          count: recurrenceCount,
        });
        const created = res.data?.created?.length ?? 0;
        const skipped = res.data?.skipped_count ?? 0;
        toast(`${created} agendamentos criados, ${skipped} ignorados (conflito)`, 'success');
      } else {
        await api.post('/appointments/', {
          barber_id: Number(createForm.barber_id),
          client_id: Number(createForm.client_id),
          service_id: Number(createForm.service_id),
          data_inicio: createForm.data_inicio,
        });
        toast('Agendamento criado', 'success');
      }
      setModalOpen(false);
      const res = await api.get(`/appointments/barbers/${selectedBarber}?target_date=${targetDate}`);
      setAppointments(Array.isArray(res.data) ? res.data : []);
    } catch (err: unknown) {
      const detail =
        typeof err === 'object' && err !== null && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      toast(detail ?? 'Erro ao criar agendamento', 'error');
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Cancelar agendamento?')) return;
    try {
      await api.delete(`/appointments/${id}`);
      toast('Agendamento cancelado', 'success');
      setAppointments((prev) => prev.filter((a) => String(a.id) !== String(id)));
    } catch {
      toast('Erro ao cancelar agendamento', 'error');
    }
  }

  function barberName(id: string | number): string {
    return barbers.find((b) => String(b.id) === String(id))?.nome ?? String(id);
  }
  function clientName(id: string | number): string {
    return clients.find((c) => String(c.id) === String(id))?.nome ?? String(id);
  }
  function serviceName(id: string | number): string {
    return services.find((s) => String(s.id) === String(id))?.nome ?? String(id);
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
        <h1 className="text-2xl font-semibold text-slate-800">Agendamentos</h1>
        <Button onClick={() => {
          setCreateForm({ barber_id: selectedBarber || '', client_id: '', service_id: '', data_inicio: '' });
          setModalOpen(true);
        }}>
          + Novo Agendamento
        </Button>
      </div>

      {/* Filters */}
      <div className="mb-4 flex flex-wrap items-end gap-4">
        <Select
          label="Barbeiro"
          options={barbers.map((b) => ({ value: b.id, label: b.nome }))}
          value={selectedBarber}
          onChange={(e) => setSelectedBarber(e.target.value)}
        />
        <Input
          label="Data"
          type="date"
          value={targetDate}
          onChange={(e) => setTargetDate(e.target.value)}
        />
      </div>

      {loadingAppts ? (
        <Spinner />
      ) : (
        <Table
          columns={[
            { key: 'barber', header: 'Barbeiro', render: (a) => barberName(a.barber_id) },
            { key: 'client', header: 'Cliente', render: (a) => clientName(a.client_id) },
            { key: 'service', header: 'Servico', render: (a) => serviceName(a.service_id) },
            {
              key: 'start',
              header: 'Inicio',
              render: (a) => new Date(a.start_at).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' }),
            },
            {
              key: 'end',
              header: 'Fim',
              render: (a) => new Date(a.end_at).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' }),
            },
            {
              key: 'actions',
              header: '',
              render: (a) => (
                <Button size="sm" variant="danger" onClick={() => handleDelete(a.id)}>
                  Cancelar
                </Button>
              ),
            },
          ]}
          data={appointments}
          keyExtractor={(a) => a.id}
          emptyMessage="Nenhum agendamento para este dia."
        />
      )}

      {/* Create modal */}
      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Novo Agendamento">
        <form onSubmit={handleCreate} className="space-y-4">
          <Select
            label="Barbeiro"
            options={barbers.map((b) => ({ value: b.id, label: b.nome }))}
            value={createForm.barber_id}
            onChange={(e) => setCreateForm({ ...createForm, barber_id: e.target.value })}
            placeholder="Selecione..."
          />
          <Select
            label="Cliente"
            options={clients.map((c) => ({ value: c.id, label: c.nome }))}
            value={createForm.client_id}
            onChange={(e) => setCreateForm({ ...createForm, client_id: e.target.value })}
            placeholder="Selecione..."
          />
          <Select
            label="Servico"
            options={services.map((s) => ({ value: s.id, label: `${s.nome} (${s.duracao_minutos}min)` }))}
            value={createForm.service_id}
            onChange={(e) => setCreateForm({ ...createForm, service_id: e.target.value })}
            placeholder="Selecione..."
          />
          <Input
            label="Data e Hora"
            type="datetime-local"
            value={createForm.data_inicio}
            onChange={(e) => setCreateForm({ ...createForm, data_inicio: e.target.value })}
            required
          />

          {/* Recurring toggle */}
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={isRecurring}
              onChange={(e) => setIsRecurring(e.target.checked)}
              className="rounded border-slate-300"
            />
            Recorrente
          </label>

          {isRecurring && (
            <div className="space-y-3 rounded border border-slate-200 bg-slate-50 p-3">
              <Select
                label="Frequencia"
                options={[
                  { value: 'weekly', label: 'Semanal' },
                  { value: 'biweekly', label: 'Quinzenal' },
                ]}
                value={recurrence}
                onChange={(e) => setRecurrence(e.target.value as 'weekly' | 'biweekly')}
              />
              <Input
                label="Quantidade (1-12)"
                type="number"
                value={String(recurrenceCount)}
                onChange={(e) => setRecurrenceCount(Math.min(12, Math.max(1, Number(e.target.value))))}
                min={1}
                max={12}
              />
            </div>
          )}

          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Criar</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
