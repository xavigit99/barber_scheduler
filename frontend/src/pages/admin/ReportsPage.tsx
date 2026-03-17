import { useState, useEffect } from 'react';
import api from '../../lib/api';
import Input from '../../components/Input';
import Button from '../../components/Button';
import Spinner from '../../components/Spinner';
import Table from '../../components/Table';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../contexts/AuthContext';
/* Backend daily report shapes */
interface DailyEntry {
  appointment_id: number;
  start_at: string;
  end_at: string;
  service: string | null;
  service_price: number;
  client: string | null;
}

interface DailyBarber {
  barber_id: number;
  barber_name: string;
  total_appointments: number;
  appointments: DailyEntry[];
}

interface DailyReport {
  date: string;
  total_appointments: number;
  barbers: DailyBarber[];
}

/* Backend returns this shape from GET /admin/stats */
interface Stats {
  barbers: number;
  clients: number;
  services: number;
  appointments_month: number;
  cancelled_month: number;
  revenue_month: number;
}

interface RevenueReport {
  total_revenue: number;
}

const fmtEur = new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' });

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
  const [dailyReport, setDailyReport] = useState<DailyReport | null>(null);
  const [dailyLoading, setDailyLoading] = useState(false);

  /* Revenue — only fires on explicit button click, not on every keystroke */
  const [revStart, setRevStart] = useState(() => {
    const d = new Date();
    d.setDate(1);
    return d.toISOString().split('T')[0];
  });
  const [revEnd, setRevEnd] = useState(() => new Date().toISOString().split('T')[0]);
  const [revenue, setRevenue] = useState<RevenueReport | null>(null);
  const [revLoading, setRevLoading] = useState(false);

  /* Load stats once per tenant */
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
  async function loadDaily() {
    if (!tenantId || !dailyDate) return;
    setDailyLoading(true);
    try {
      const res = await api.get(`/admin/reports/daily?target_date=${dailyDate}`);
      setDailyReport(res.data ?? null);
    } catch {
      toast('Erro ao carregar agendamentos do dia', 'error');
      setDailyReport(null);
    } finally {
      setDailyLoading(false);
    }
  }

  /* Auto-load daily when tenant becomes available */
  useEffect(() => {
    if (tenantId) loadDaily();
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  /* Revenue — manual trigger only */
  async function loadRevenue() {
    if (!tenantId || !revStart || !revEnd) return;
    setRevLoading(true);
    try {
      const res = await api.get(`/admin/reports/revenue?start_date=${revStart}&end_date=${revEnd}`);
      setRevenue(res.data);
    } catch {
      toast('Erro ao carregar relatório de receita', 'error');
      setRevenue(null);
    } finally {
      setRevLoading(false);
    }
  }

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
        <h2 className="mb-4 text-lg font-medium text-slate-700">Resumo do Mês</h2>
        {statsLoading ? (
          <Spinner />
        ) : stats ? (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <KpiCard label="Barbeiros" value={stats.barbers} />
            <KpiCard label="Clientes" value={stats.clients} />
            <KpiCard label="Serviços" value={stats.services} />
            <KpiCard label="Agendamentos (mês)" value={stats.appointments_month} />
            <KpiCard label="Cancelamentos (mês)" value={stats.cancelled_month} />
            <KpiCard label="Receita (mês)" value={fmtEur.format(stats.revenue_month)} />
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
        ) : dailyReport && dailyReport.total_appointments > 0 ? (
          <div className="space-y-6">
            {dailyReport.barbers.map((b) => (
              <div key={b.barber_id}>
                <p className="mb-2 text-sm font-medium text-slate-600">
                  {b.barber_name} — {b.total_appointments} agendamento(s)
                </p>
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
                    { key: 'client', header: 'Cliente', render: (a) => a.client ?? '—' },
                    { key: 'service', header: 'Serviço', render: (a) => a.service ?? '—' },
                    {
                      key: 'price',
                      header: 'Preço',
                      render: (a) => fmtEur.format(a.service_price),
                    },
                  ]}
                  data={b.appointments}
                  keyExtractor={(a) => String(a.appointment_id)}
                  emptyMessage=""
                />
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">Sem agendamentos para esta data.</p>
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
          <Button size="sm" onClick={loadRevenue}>Calcular</Button>
        </div>
        {revLoading ? (
          <Spinner />
        ) : revenue !== null ? (
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-6 py-4 inline-flex items-center gap-3">
            <span className="text-sm text-emerald-700">Receita total:</span>
            <span className="text-2xl font-bold text-emerald-800">{fmtEur.format(revenue.total_revenue ?? 0)}</span>
          </div>
        ) : null}
      </section>
    </div>
  );
}
