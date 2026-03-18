import { useState, useEffect, type FormEvent } from 'react';
import api, { getApiError } from '../../lib/api';
import Button from '../../components/Button';
import Modal from '../../components/Modal';
import Input from '../../components/Input';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';

interface LoyaltyAccount {
  pontos_total: number;
  pontos_disponiveis: number;
}

export default function MyLoyaltyPage() {
  const { toast } = useToast();
  const [account, setAccount] = useState<LoyaltyAccount | null>(null);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({ pontos: 0, descricao: '' });

  async function load() {
    try {
      const res = await api.get('/loyalty/me');
      setAccount(res.data);
    } catch (err) {
      toast(getApiError(err, 'Erro ao carregar fidelizacao'), 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleRedeem(e: FormEvent) {
    e.preventDefault();
    try {
      await api.post('/loyalty/redeem', {
        pontos: Number(form.pontos),
        descricao: form.descricao,
      });
      toast('Pontos resgatados', 'success');
      setModalOpen(false);
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao resgatar pontos'), 'error');
    }
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Fidelizacao</h1>

      <div className="rounded-xl bg-white p-8 shadow-sm border border-slate-200 max-w-md">
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="text-center">
            <p className="text-4xl font-bold text-slate-800">{account?.pontos_total ?? 0}</p>
            <p className="text-sm text-slate-500 mt-1">Pontos Total</p>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold text-emerald-600">{account?.pontos_disponiveis ?? 0}</p>
            <p className="text-sm text-slate-500 mt-1">Pontos Disponiveis</p>
          </div>
        </div>

        <Button
          onClick={() => { setForm({ pontos: 0, descricao: '' }); setModalOpen(true); }}
          disabled={!account?.pontos_disponiveis}
          className="w-full"
        >
          Resgatar Pontos
        </Button>

        <p className="text-xs text-slate-400 text-center mt-4">
          Ganha 1 ponto por cada minuto de servico.
        </p>
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Resgatar Pontos">
        <form onSubmit={handleRedeem} className="space-y-4">
          <Input
            label="Pontos a resgatar"
            type="number"
            min={1}
            max={account?.pontos_disponiveis ?? 0}
            value={form.pontos}
            onChange={(e) => setForm({ ...form, pontos: Number(e.target.value) })}
            required
            autoFocus
          />
          <Input
            label="Descricao"
            value={form.descricao}
            onChange={(e) => setForm({ ...form, descricao: e.target.value })}
            required
          />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Resgatar</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
