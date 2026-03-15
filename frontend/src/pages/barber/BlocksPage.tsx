import { useState, useEffect, type FormEvent } from 'react';
import api from '../../lib/api';
import Table from '../../components/Table';
import Button from '../../components/Button';
import Modal from '../../components/Modal';
import Input from '../../components/Input';
import Select from '../../components/Select';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import type { BarberBlock } from '../../types';

const BARBER_ID_KEY = 'barber_my_barber_id';

export default function BlocksPage() {
  const { toast } = useToast();
  const barberId = localStorage.getItem(BARBER_ID_KEY) ?? '';
  const [blocks, setBlocks] = useState<BarberBlock[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({ tipo: 'pessoal', inicio: '', fim: '', motivo: '' });

  async function load() {
    if (!barberId) { setLoading(false); return; }
    try {
      const res = await api.get(`/barbers/${barberId}/availability/blocks`);
      setBlocks(Array.isArray(res.data) ? res.data : []);
    } catch {
      toast('Erro ao carregar bloqueios', 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      await api.post(`/barbers/${barberId}/availability/blocks`, {
        tipo: form.tipo,
        inicio: form.inicio,
        fim: form.fim,
        motivo: form.motivo || null,
      });
      toast('Bloqueio adicionado', 'success');
      setModalOpen(false);
      load();
    } catch {
      toast('Erro ao adicionar bloqueio', 'error');
    }
  }

  async function handleDelete(blockId: string) {
    try {
      await api.delete(`/barbers/${barberId}/availability/blocks/${blockId}`);
      toast('Bloqueio removido', 'success');
      load();
    } catch {
      toast('Erro ao remover bloqueio', 'error');
    }
  }

  if (!barberId) {
    return (
      <div className="py-12 text-center text-slate-500">
        Configure o seu Barber ID em <a href="/barber" className="text-emerald-600 underline">Minha Agenda</a> primeiro.
      </div>
    );
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-800">Meus Bloqueios</h1>
        <Button onClick={() => { setForm({ tipo: 'pessoal', inicio: '', fim: '', motivo: '' }); setModalOpen(true); }}>
          + Novo Bloqueio
        </Button>
      </div>

      <Table
        columns={[
          { key: 'tipo', header: 'Tipo', render: (b) => b.kind },
          { key: 'inicio', header: 'Inicio', render: (b) => new Date(b.start_at).toLocaleString('pt-PT') },
          { key: 'fim', header: 'Fim', render: (b) => new Date(b.end_at).toLocaleString('pt-PT') },
          { key: 'motivo', header: 'Motivo', render: (b) => b.reason ?? '-' },
          {
            key: 'actions',
            header: '',
            render: (b) => (
              <Button size="sm" variant="danger" onClick={() => handleDelete(b.id)}>Remover</Button>
            ),
          },
        ]}
        data={blocks}
        keyExtractor={(b) => b.id}
        emptyMessage="Nenhum bloqueio registado."
      />

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Novo Bloqueio">
        <form onSubmit={handleSubmit} className="space-y-4">
          <Select
            label="Tipo"
            options={[
              { value: 'ferias', label: 'Ferias' },
              { value: 'doenca', label: 'Doenca' },
              { value: 'pessoal', label: 'Pessoal' },
              { value: 'outro', label: 'Outro' },
            ]}
            value={form.tipo}
            onChange={(e) => setForm({ ...form, tipo: e.target.value })}
          />
          <Input label="Inicio" type="datetime-local" value={form.inicio} onChange={(e) => setForm({ ...form, inicio: e.target.value })} required />
          <Input label="Fim" type="datetime-local" value={form.fim} onChange={(e) => setForm({ ...form, fim: e.target.value })} required />
          <Input label="Motivo (opcional)" value={form.motivo} onChange={(e) => setForm({ ...form, motivo: e.target.value })} />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Adicionar</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
