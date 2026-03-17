import { useState, type FormEvent } from 'react';
import api from '../../lib/api';
import Button from '../../components/Button';
import Spinner from '../../components/Spinner';
import Table from '../../components/Table';
import Select from '../../components/Select';
import Input from '../../components/Input';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../contexts/AuthContext';

const ENTITIES = [
  { value: 'barber', label: 'Barbeiros' },
  { value: 'client', label: 'Clientes' },
  { value: 'service', label: 'Serviços' },
  { value: 'appointment', label: 'Agendamentos' },
  { value: 'barbershop', label: 'Barbearias' },
  { value: 'membership', label: 'Memberships' },
];

interface AuditEntry {
  id: string | number;
  deleted_at: string;
  nome?: string;
  email?: string;
  start_at?: string;
  end_at?: string;
  role?: string;
}

export default function CompliancePage() {
  const { toast } = useToast();
  const { tenantId } = useAuth();

  /* Audit log */
  const [auditEntity, setAuditEntity] = useState('client');
  const [auditLog, setAuditLog] = useState<AuditEntry[]>([]);
  const [auditLoading, setAuditLoading] = useState(false);
  const [auditLoaded, setAuditLoaded] = useState(false);

  /* Purge form */
  const [purgeEntity, setPurgeEntity] = useState('client');
  const [purgeOlderThan, setPurgeOlderThan] = useState('90');
  const [purging, setPurging] = useState(false);

  if (!tenantId) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
        Seleciona uma barbearia para ver os dados de compliance.
      </div>
    );
  }

  async function loadAudit() {
    setAuditLoading(true);
    setAuditLoaded(false);
    try {
      const res = await api.get(`/admin/audit?entity=${auditEntity}`);
      setAuditLog(Array.isArray(res.data) ? res.data : []);
      setAuditLoaded(true);
    } catch {
      toast('Erro ao carregar audit log', 'error');
      setAuditLog([]);
    } finally {
      setAuditLoading(false);
    }
  }

  async function handleExport() {
    try {
      const res = await api.get('/admin/export', { responseType: 'blob' });
      const url = URL.createObjectURL(new Blob([res.data], { type: 'application/json' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `gdpr-export-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast('Exportação concluída', 'success');
    } catch {
      toast('Erro ao exportar dados', 'error');
    }
  }

  async function handlePurge(e: FormEvent) {
    e.preventDefault();
    const days = Number(purgeOlderThan);
    if (!days || days < 1) {
      toast('Introduz um número válido de dias', 'error');
      return;
    }
    const confirmed = confirm(
      `Eliminar permanentemente registos de "${purgeEntity}" com mais de ${days} dias?\n\nEsta operação é irreversível.`
    );
    if (!confirmed) return;
    setPurging(true);
    try {
      await api.delete('/admin/purge', { data: { entity: purgeEntity, older_than_days: days } });
      toast(`Dados de "${purgeEntity}" purgados`, 'success');
    } catch {
      toast('Erro ao purgar dados', 'error');
    } finally {
      setPurging(false);
    }
  }

  return (
    <div className="space-y-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-800">Compliance & Auditoria</h1>
        <Button variant="secondary" size="sm" onClick={handleExport}>
          Exportar dados (GDPR)
        </Button>
      </div>

      {/* Audit log */}
      <section>
        <h2 className="mb-4 text-lg font-medium text-slate-700">Registos eliminados</h2>
        <div className="mb-4 flex items-end gap-3">
          <Select
            label="Entidade"
            options={ENTITIES}
            value={auditEntity}
            onChange={(e) => setAuditEntity(e.target.value)}
          />
          <Button size="sm" onClick={loadAudit}>Consultar</Button>
        </div>
        {auditLoading ? (
          <Spinner />
        ) : auditLoaded ? (
          <Table
            columns={[
              { key: 'id', header: 'ID', render: (e) => <span className="font-mono text-xs">{String(e.id).slice(0, 8)}</span> },
              { key: 'nome', header: 'Nome / Email', render: (e) => e.nome ?? e.email ?? '-' },
              { key: 'deleted_at', header: 'Eliminado em', render: (e) => new Date(e.deleted_at).toLocaleString('pt-PT') },
            ]}
            data={auditLog}
            keyExtractor={(e) => String(e.id)}
            emptyMessage="Nenhum registo eliminado encontrado."
          />
        ) : null}
      </section>

      {/* Purge */}
      <section className="rounded-xl border border-red-200 bg-red-50 p-6">
        <h2 className="mb-4 text-lg font-medium text-red-700">Purgar dados antigos</h2>
        <p className="mb-4 text-sm text-red-600">
          Elimina permanentemente (hard delete) registos já marcados como eliminados há mais de N dias. Irreversível.
        </p>
        <form onSubmit={handlePurge} className="flex flex-wrap items-end gap-3">
          <Select
            label="Entidade"
            options={ENTITIES}
            value={purgeEntity}
            onChange={(e) => setPurgeEntity(e.target.value)}
          />
          <Input
            label="Mais de (dias)"
            type="number"
            min="1"
            value={purgeOlderThan}
            onChange={(e) => setPurgeOlderThan(e.target.value)}
          />
          <Button variant="danger" type="submit" disabled={purging}>
            {purging ? 'A purgar...' : 'Purgar'}
          </Button>
        </form>
      </section>
    </div>
  );
}
