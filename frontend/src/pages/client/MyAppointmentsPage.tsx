import { useState, useEffect } from 'react';
import api from '../../lib/api';
import Input from '../../components/Input';
import Table from '../../components/Table';
import Button from '../../components/Button';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import type { Appointment } from '../../types';

export default function MyAppointmentsPage() {
  const { toast } = useToast();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [targetDate, setTargetDate] = useState(() => new Date().toISOString().split('T')[0]);

  async function load(date: string) {
    setLoading(true);
    try {
      const res = await api.get(`/appointments/clients/me/appointments?target_date=${date}`);
      setAppointments(Array.isArray(res.data) ? res.data : []);
    } catch {
      toast('Erro ao carregar agendamentos', 'error');
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(targetDate);
  }, [targetDate]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleCancel(id: string) {
    if (!confirm('Cancelar este agendamento?')) return;
    try {
      await api.delete(`/appointments/${id}`);
      toast('Agendamento cancelado', 'success');
      setAppointments((prev) => prev.filter((a) => a.id !== id));
    } catch {
      toast('Erro ao cancelar agendamento', 'error');
    }
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Meus Agendamentos</h1>

      <div className="mb-4">
        <Input
          label="Data"
          type="date"
          value={targetDate}
          onChange={(e) => setTargetDate(e.target.value)}
        />
      </div>

      {loading ? (
        <Spinner />
      ) : (
        <Table
          columns={[
            {
              key: 'date',
              header: 'Data',
              render: (a) => new Date(a.start_at).toLocaleDateString('pt-PT'),
            },
            {
              key: 'start',
              header: 'Inicio',
              render: (a) =>
                new Date(a.start_at).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' }),
            },
            {
              key: 'end',
              header: 'Fim',
              render: (a) =>
                new Date(a.end_at).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' }),
            },
            {
              key: 'barber',
              header: 'Barbeiro',
              render: (a) => <span className="font-mono text-xs">{a.barber_id.slice(0, 8)}...</span>,
            },
            {
              key: 'actions',
              header: '',
              render: (a) => (
                <Button size="sm" variant="danger" onClick={() => handleCancel(a.id)}>
                  Cancelar
                </Button>
              ),
            },
          ]}
          data={appointments}
          keyExtractor={(a) => a.id}
          emptyMessage="Nenhum agendamento para esta data."
        />
      )}
    </div>
  );
}
