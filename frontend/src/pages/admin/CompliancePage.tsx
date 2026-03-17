import { useState, useEffect } from 'react';
import api from '../../lib/api';
import Button from '../../components/Button';
import Spinner from '../../components/Spinner';
import Table from '../../components/Table';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../contexts/AuthContext';

interface AuditEntry {
  id: string;
  action: string;
  entity: string;
  entity_id: string;
  performed_at: string;
  performed_by: string | null;
}

export default function CompliancePage() {
  const { toast } = useToast();
  const { tenantId } = useAuth();

  const [auditLog, setAuditLog] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [purging, setPurging] = useState(false);

  useEffect(() => {
    if (!tenantId) return;
    api
      .get('/admin/audit')
      .then((res) => setAuditLog(Array.isArray(res.data) ? res.data : []))
      .catch(() => toast('Erro ao carregar audit log', 'error'))
      .finally(() => setLoading(false));
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleExport() {
    try {
      const res = await api.get('/admin/export', { responseType: 'blob' });
      const url = URL.createObjectURL(new Blob([res.data], { type: 'application/json' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `gdpr-export-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast('Exportação concluída', 'success');
    } catch {
      toast('Erro ao exportar dados', 'error');
    }
  }

  async function handlePurge() {
    const confirmed = confirm(
      'Esta ação irá eliminar permanentemente dados antigos. Esta operação é irreversível.\n\nTens a certeza?'
    );
    if (!confirmed) return;
    setPurging(true);
    try {
      await api.delete('/admin/purge');
      toast('Dados antigos eliminados', 'success');
    } catch {
      toast('Erro ao purgar dados', 'error');
    } finally {
      setPurging(false);
    }
  }

  if (!tenantId) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
        Seleciona uma barbearia para ver os dados de compliance.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-800">Compliance & Auditoria</h1>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={handleExport}>
            Exportar dados (GDPR)
          </Button>
          <Button variant="danger" size="sm" onClick={handlePurge} disabled={purging}>
            {purging ? 'A purgar...' : 'Purgar dados antigos'}
          </Button>
        </div>
      </div>

      <section>
        <h2 className="mb-4 text-lg font-medium text-slate-700">Audit Log</h2>
        {loading ? (
          <Spinner />
        ) : (
          <Table
            columns={[
              {
                key: 'date',
                header: 'Data',
                render: (e) => new Date(e.performed_at).toLocaleString('pt-PT'),
              },
              { key: 'action', header: 'Ação', render: (e) => e.action },
              { key: 'entity', header: 'Entidade', render: (e) => e.entity },
              {
                key: 'entity_id',
                header: 'ID',
                render: (e) => <span className="font-mono text-xs">{String(e.entity_id).slice(0, 8)}</span>,
              },
              {
                key: 'by',
                header: 'Por',
                render: (e) => e.performed_by ? <span className="font-mono text-xs">{String(e.performed_by).slice(0, 8)}</span> : '-',
              },
            ]}
            data={auditLog}
            keyExtractor={(e) => e.id}
            emptyMessage="Nenhuma entrada no audit log."
          />
        )}
      </section>
    </div>
  );
}
