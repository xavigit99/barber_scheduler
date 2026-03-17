import { useState, useEffect, useCallback } from 'react';
import api from '../../lib/api';
import Input from '../../components/Input';
import Button from '../../components/Button';
import Spinner from '../../components/Spinner';
import Table from '../../components/Table';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../contexts/AuthContext';
import type { Appointment } from '../../types';

interface Stats {
  total_barbers: number;
  total_clients: number;
  total_services: number;
  appointments_today: number;
}

interface RevenueReport {
  total_revenue: number;
  appointments: Appointment[];
}

function KpiCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-bold text-slate-800">{value}</p>
    </div>
  );
}

export default function ReportsPage() {
  const { toast } = useToast();
  const { tenantId } = useAuth();

  /* KPIs */
  const [stats, setStats] = useState<Stats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);

  /* Daily appointments */
  const [dailyDate, setDailyDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [dailyAppts, setDailyAppts] = useState<Appointment[]>([]);
  const [dailyLoading, setDailyLoading] = useState(false);

  /* Revenue */
  const [revStart, setRevStart] = useState(() => {
    const d = new Date();
    d.setDate(1);
    return d.toISOString().split('T')[0];
  });
  const [revEnd, setRevEnd] = useState(() => new Date().toISOString().split('T')[0]);
  const [revenue, setRevenue] = useState<RevenueReport | null>(null);
  const [revLoading, setRevLoading] = useState(false);

  /* Load stats once (and when tenant changes) */
  useEffect(() => {
    if (!tenantId) return;
    setStatsLoading(true);
    api
      .get('/admin/stats')
      .then((res) => setStats(res.data))
      .catch(() => toast('Erro ao carregar KPIs', 'error'))
      .finally(() => setStatsLoading(false));
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  /* Load daily appointments */
  const loadDaily = useCallback(async () => {
    if (!tenantId || !dailyDate) return;
    setDailyLoading(true);
    try {
      const res = await api.get(`/admin/reports/daily?date=${dailyDate}`);
      setDailyAppts(Array.isArray(res.data) ? res.data : []);
    } catch {
      toast('Erro ao carregar agendamentos do dia', 'error');
      setDailyAppts([]);
    } finally {
      setDailyLoading(false);
    }
  }, [tenantId, dailyDate]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { loadDaily(); }, [loadDaily]);

  /* Load revenue */
  const loadRevenue = useCallback(async () => {
    if (!tenantId || !revStart || !revEnd) return;
    setRevLoading(true);
    try {
      const res = await api.get(`/admin/reports/revenue?start=${revStart}&end=${revEnd}`);
      setRevenue(res.data);
    } catch {
      toast('Erro ao carregar relatório de receita', 'error');
      setRevenue(null);
    } finally {
      setRevLoading(false);
    }
  }, [tenantId, revStart, revEnd]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { loadRevenue(); }, [loadRevenue]);

  const fmt = (v: number) =>
    new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' }).format(v);

  if (!tenantId) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
        Seleciona uma barbearia para ver os relatórios.
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <h1 className="text-2xl font-semibold text-slate-800">Relatórios</h1>

      {/* KPIs */}
      <section>
        <h2 className="mb-4 text-lg font-medium text-slate-700">Resumo</h2>
        {statsLoading ? (
          <Spinner />
        ) : stats ? (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <KpiCard label="Barbeiros" value={stats.total_barbers} />
            <KpiCard label="Clientes" value={stats.total_clients} />
            <KpiCard label="Serviços" value={stats.total_services} />
            <KpiCard label="Agendamentos Hoje" value={stats.appointments_today} />
          </div>
        ) : (
          <p className="text-sm text-slate-500">Sem dados disponíveis.</p>
        )}
      </section>

      {/* Daily appointments */}
      <section>
        <h2 className="mb-4 text-lg font-medium text-slate-700">Agendamentos do Dia</h2>
        <div className="mb-4 flex items-end gap-3">
          <Input
            label="Data"
            type="date"
            value={dailyDate}
            onChange={(e) => setDailyDate(e.target.value)}
          />
          <Button size="sm" onClick={loadDaily}>Atualizar</Button>
        </div>
        {dailyLoading ? (
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
              { key: 'barber', header: 'Barbeiro ID', render: (a) => <span className="font-mono text-xs">{String(a.barber_id).slice(0, 8)}</span> },
              { key: 'client', header: 'Cliente ID', render: (a) => <span className="font-mono text-xs">{String(a.client_id).slice(0, 8)}</span> },
              { key: 'service', header: 'Serviço ID', render: (a) => <span className="font-mono text-xs">{String(a.service_id).slice(0, 8)}</span> },
            ]}
            data={dailyAppts}
            keyExtractor={(a) => a.id}
            emptyMessage="Sem agendamentos para esta data."
          />
        )}
      </section>

      {/* Revenue */}
      <section>
        <h2 className="mb-4 text-lg font-medium text-slate-700">Receita por Período</h2>
        <div className="mb-4 flex flex-wrap items-end gap-3">
          <Input
            label="Início"
            type="date"
            value={revStart}
            onChange={(e) => setRevStart(e.target.value)}
          />
          <Input
            label="Fim"
            type="date"
            value={revEnd}
            onChange={(e) => setRevEnd(e.target.value)}
          />
          <Button size="sm" onClick={loadRevenue}>Atualizar</Button>
        </div>
        {revLoading ? (
          <Spinner />
        ) : revenue !== null ? (
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-6 py-4 inline-flex items-center gap-3">
            <span className="text-sm text-emerald-700">Receita total:</span>
            <span className="text-2xl font-bold text-emerald-800">{fmt(revenue.total_revenue ?? 0)}</span>
          </div>
        ) : null}
      </section>
    </div>
  );
}
