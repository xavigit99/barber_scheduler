import { useState } from 'react';
import api, { getApiError } from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';
import { Link } from 'react-router-dom';
import Button from '../../components/Button';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';

export default function SAFTPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();

  const currentYear = new Date().getFullYear();
  const [year, setYear] = useState(currentYear);
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleExport() {
    setLoading(true);
    try {
      const res = await api.get(`/admin/saft?year=${year}`);
      setResult(JSON.stringify(res.data, null, 2));
    } catch (err) {
      toast(getApiError(err, 'Erro ao exportar SAF-T'), 'error');
    } finally {
      setLoading(false);
    }
  }

  function handleDownload() {
    if (!result) return;
    const blob = new Blob([result], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `saft_${year}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (!tenantId) {
    return (
      <div className="py-12 text-center text-slate-500">
        Selecione um tenant em <Link to="/admin/barbershops" className="text-emerald-600 underline">Barbearias</Link> primeiro.
      </div>
    );
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">SAF-T Export</h1>

      <div className="mb-6 flex items-center gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-slate-700">Ano</label>
          <select
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800"
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
          >
            {Array.from({ length: 5 }, (_, i) => currentYear - i).map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>
        <div className="flex items-end gap-2 pt-5">
          <Button onClick={handleExport} disabled={loading}>Exportar</Button>
          {result && <Button variant="secondary" onClick={handleDownload}>Download JSON</Button>}
        </div>
      </div>

      {loading && <Spinner />}

      {result && !loading && (
        <div className="rounded-xl bg-white p-6 shadow-sm border border-slate-200">
          <pre className="text-xs text-slate-700 overflow-auto max-h-[500px] whitespace-pre-wrap font-mono">
            {result}
          </pre>
        </div>
      )}
    </div>
  );
}
