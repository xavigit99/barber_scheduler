import { useState, useEffect } from 'react';
import api from '../../lib/api';
import Input from '../../components/Input';
import Table from '../../components/Table';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../contexts/AuthContext';
import type { Appointment, Client, Service } from '../../types';

export default function SchedulePage() {
  const { toast } = useToast();
  const { barberId } = useAuth();
  const [targetDate, setTargetDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [clients, setClients] = useState<Record<string, string>>({});
  const [services, setServices] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  /* Load client and service name maps once */
  useEffect(() => {
    Promise.all([api.get('/clients/'), api.get('/services/')])
      .then(([cRes, sRes]) => {
        const cMap: Record<string, string> = {};
        (Array.isArray(cRes.data) ? cRes.data : []).forEach((c: Client) => { cMap[String(c.id)] = c.nome; });
        const sMap: Record<string, string> = {};
        (Array.isArray(sRes.data) ? sRes.data : []).forEach((s: Service) => { sMap[String(s.id)] = s.nome; });
        setClients(cMap);
        setServices(sMap);
      })
      .catch(() => {/* non-critical */});
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!barberId || !targetDate) return;
    setLoading(true);
    api
      .get(`/appointments/barbers/${barberId}?target_date=${targetDate}`)
      .then((res) => setAppointments(Array.isArray(res.data) ? res.data : []))
      .catch(() => {
        toast('Erro ao carregar agenda', 'error');
        setAppointments([]);
      })
      .finally(() => setLoading(false));
  }, [barberId, targetDate]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!barberId) return <Spinner />;

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Minha Agenda</h1>
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
              key: 'start',
              header: 'Início',
              render: (a) =>
                new Date(a.start_at).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' }),
            },
            {
              key: 'end',
              header: 'Fim',
              render: (a) =>
                new Date(a.end_at).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' }),
            },
            { key: 'client', header: 'Cliente', render: (a) => clients[String(a.client_id)] ?? <span className="font-mono text-xs">{String(a.client_id).slice(0, 8)}</span> },
            { key: 'service', header: 'Serviço', render: (a) => services[String(a.service_id)] ?? <span className="font-mono text-xs">{String(a.service_id).slice(0, 8)}</span> },
          ]}
          data={appointments}
          keyExtractor={(a) => a.id}
          emptyMessage="Sem agendamentos para este dia."
        />
      )}
    </div>
  );
}
