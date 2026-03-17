import { useState, useEffect } from 'react';
import api from '../../lib/api';
import Input from '../../components/Input';
import Table from '../../components/Table';
import Spinner from '../../components/Spinner';
import Button from '../../components/Button';
import { useToast } from '../../components/Toast';
import type { Appointment, Client, Service } from '../../types';

const BARBER_ID_KEY = 'barber_my_barber_id';

export default function SchedulePage() {
  const { toast } = useToast();
  const [barberId, setBarberId] = useState(() => localStorage.getItem(BARBER_ID_KEY) ?? '');
  const [savedBarberId, setSavedBarberId] = useState(() => localStorage.getItem(BARBER_ID_KEY) ?? '');
  const [targetDate, setTargetDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [clients, setClients] = useState<Record<string, string>>({});
  const [services, setServices] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  function saveBarberId() {
    localStorage.setItem(BARBER_ID_KEY, barberId);
    setSavedBarberId(barberId);
    toast('Barber ID guardado', 'success');
  }

  /* Load client and service maps once */
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
    if (!savedBarberId || !targetDate) return;
    setLoading(true);
    api
      .get(`/appointments/barbers/${savedBarberId}?target_date=${targetDate}`)
      .then((res) => setAppointments(Array.isArray(res.data) ? res.data : []))
      .catch(() => {
        toast('Erro ao carregar agenda', 'error');
        setAppointments([]);
      })
      .finally(() => setLoading(false));
  }, [savedBarberId, targetDate]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!savedBarberId) {
    return (
      <div className="mx-auto max-w-md py-12">
        <h1 className="mb-4 text-2xl font-semibold text-slate-800">Minha Agenda</h1>
        <p className="mb-4 text-sm text-slate-500">
          Introduza o seu Barber ID para ver a sua agenda.
        </p>
        <div className="flex gap-2">
          <Input
            value={barberId}
            onChange={(e) => setBarberId(e.target.value)}
            placeholder="Barber ID"
            className="flex-1"
          />
          <Button onClick={saveBarberId} disabled={!barberId}>Guardar</Button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Minha Agenda</h1>
      <div className="mb-4 flex items-end gap-4">
        <Input
          label="Data"
          type="date"
          value={targetDate}
          onChange={(e) => setTargetDate(e.target.value)}
        />
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            localStorage.removeItem(BARBER_ID_KEY);
            setSavedBarberId('');
            setBarberId('');
          }}
        >
          Alterar Barber ID
        </Button>
      </div>

      {loading ? (
        <Spinner />
      ) : (
        <Table
          columns={[
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
