import { useState, useEffect, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import api, { getApiError } from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';
import Table from '../../components/Table';
import Button from '../../components/Button';
import Input from '../../components/Input';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';

interface SegmentedClient {
  id: string;
  nome: string;
  email: string;
  telefone: string;
}

interface ServiceOption {
  id: string;
  nome: string;
}

export default function ClientSegmentPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();

  const [services, setServices] = useState<ServiceOption[]>([]);
  const [results, setResults] = useState<SegmentedClient[]>([]);
  const [loading, setLoading] = useState(false);
  const [servicesLoading, setServicesLoading] = useState(true);

  const [filters, setFilters] = useState({
    inactive_days: '',
    min_spend: '',
    service_id: '',
    has_birthday_this_month: false,
  });

  useEffect(() => {
    async function loadServices() {
      try {
        const res = await api.get('/services/');
        setServices(Array.isArray(res.data) ? res.data : []);
      } catch {
        /* ignore */
      } finally {
        setServicesLoading(false);
      }
    }
    loadServices();
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleFilter(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.inactive_days) params.set('inactive_days', filters.inactive_days);
      if (filters.min_spend) params.set('min_spend', filters.min_spend);
      if (filters.service_id) params.set('service_id', filters.service_id);
      if (filters.has_birthday_this_month) params.set('has_birthday_this_month', 'true');

      const res = await api.get(`/clients/segment?${params.toString()}`);
      setResults(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      toast(getApiError(err, 'Erro ao segmentar clientes'), 'error');
    } finally {
      setLoading(false);
    }
  }

  if (!tenantId) {
    return (
      <div className="py-12 text-center text-slate-500">
        Selecione um tenant em <Link to="/admin/barbershops" className="text-emerald-600 underline">Barbearias</Link> primeiro.
      </div>
    );
  }

  if (servicesLoading) return <Spinner />;

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Segmentacao de Clientes</h1>

      {/* Filter form */}
      <form onSubmit={handleFilter} className="mb-6 rounded-xl bg-white p-6 shadow-sm border border-slate-200">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <Input
            label="Dias Inativo"
            type="number"
            min={0}
            value={filters.inactive_days}
            onChange={(e) => setFilters({ ...filters, inactive_days: e.target.value })}
            placeholder="ex: 30"
          />
          <Input
            label="Gasto Minimo (EUR)"
            type="number"
            min={0}
            step={0.01}
            value={filters.min_spend}
            onChange={(e) => setFilters({ ...filters, min_spend: e.target.value })}
            placeholder="ex: 50"
          />
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-slate-700">Servico</label>
            <select
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800"
              value={filters.service_id}
              onChange={(e) => setFilters({ ...filters, service_id: e.target.value })}
            >
              <option value="">Todos</option>
              {services.map((s) => (
                <option key={s.id} value={s.id}>{s.nome}</option>
              ))}
            </select>
          </div>
          <div className="flex items-end pb-1">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.has_birthday_this_month}
                onChange={(e) => setFilters({ ...filters, has_birthday_this_month: e.target.checked })}
                className="h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
              />
              <span className="text-sm text-slate-700">Aniversario este mes</span>
            </label>
          </div>
        </div>
        <Button type="submit" disabled={loading}>Filtrar</Button>
      </form>

      {loading && <Spinner />}

      {!loading && results.length > 0 && (
        <Table
          columns={[
            { key: 'nome', header: 'Nome', render: (c) => c.nome },
            { key: 'email', header: 'Email', render: (c) => c.email },
            { key: 'telefone', header: 'Telefone', render: (c) => c.telefone ?? '-' },
          ]}
          data={results}
          keyExtractor={(c) => c.id}
          emptyMessage="Nenhum cliente encontrado."
        />
      )}

      {!loading && results.length === 0 && (
        <p className="text-sm text-slate-400 text-center py-8">Aplique filtros para segmentar clientes.</p>
      )}
    </div>
  );
}
