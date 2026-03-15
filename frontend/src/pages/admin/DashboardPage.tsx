import { useState, useEffect } from 'react';
import api from '../../lib/api';
import Spinner from '../../components/Spinner';

interface Stats {
  barbers: number;
  clients: number;
  services: number;
  appointmentsToday: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [barbersRes, clientsRes, servicesRes] = await Promise.all([
          api.get('/barbers/'),
          api.get('/clients/'),
          api.get('/services/'),
        ]);

        /* Appointments today is best-effort — some setups may not have a barber yet */
        let appointmentsToday = 0;
        const barbers = barbersRes.data;
        if (Array.isArray(barbers) && barbers.length > 0) {
          const today = new Date().toISOString().split('T')[0];
          try {
            const res = await api.get(
              `/appointments/barbers/${barbers[0].id}?target_date=${today}`,
            );
            appointmentsToday = Array.isArray(res.data) ? res.data.length : 0;
          } catch {
            /* ignore — barber may not have appointments endpoint */
          }
        }

        setStats({
          barbers: Array.isArray(barbers) ? barbers.length : 0,
          clients: Array.isArray(clientsRes.data) ? clientsRes.data.length : 0,
          services: Array.isArray(servicesRes.data) ? servicesRes.data.length : 0,
          appointmentsToday,
        });
      } catch {
        setStats({ barbers: 0, clients: 0, services: 0, appointmentsToday: 0 });
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <Spinner />;

  const cards = [
    { label: 'Barbeiros', value: stats?.barbers ?? 0, color: 'bg-emerald-500' },
    { label: 'Clientes', value: stats?.clients ?? 0, color: 'bg-blue-500' },
    { label: 'Servicos', value: stats?.services ?? 0, color: 'bg-amber-500' },
    { label: 'Agendamentos Hoje', value: stats?.appointmentsToday ?? 0, color: 'bg-purple-500' },
  ];

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Dashboard</h1>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => (
          <div key={card.label} className="rounded-xl bg-white p-6 shadow-sm border border-slate-200">
            <div className={`mb-3 inline-flex h-10 w-10 items-center justify-center rounded-lg ${card.color} text-white font-bold text-sm`}>
              {card.value}
            </div>
            <h3 className="text-sm font-medium text-slate-500">{card.label}</h3>
            <p className="mt-1 text-2xl font-bold text-slate-800">{card.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
