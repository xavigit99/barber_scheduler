import { useState, useEffect, type FormEvent } from 'react';
import api from '../../lib/api';
import Table from '../../components/Table';
import Button from '../../components/Button';
import Modal from '../../components/Modal';
import Input from '../../components/Input';
import Select from '../../components/Select';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import type { AvailabilityWindow, BarberBlock } from '../../types';

const BARBER_ID_KEY = 'barber_my_barber_id';

const WEEKDAYS = [
  { value: '0', label: 'Domingo' },
  { value: '1', label: 'Segunda' },
  { value: '2', label: 'Terca' },
  { value: '3', label: 'Quarta' },
  { value: '4', label: 'Quinta' },
  { value: '5', label: 'Sexta' },
  { value: '6', label: 'Sabado' },
];

function weekdayLabel(n: number): string {
  return WEEKDAYS[n]?.label ?? String(n);
}

export default function AvailabilityPage() {
  const { toast } = useToast();
  const [barberId] = useState(() => localStorage.getItem(BARBER_ID_KEY) ?? '');

  const [windows, setWindows] = useState<AvailabilityWindow[]>([]);
  const [blocks, setBlocks] = useState<BarberBlock[]>([]);
  const [loading, setLoading] = useState(true);

  /* window form */
  const [winModalOpen, setWinModalOpen] = useState(false);
  const [winForm, setWinForm] = useState({ dia_semana: '1', hora_inicio: '09:00:00', hora_fim: '18:00:00' });

  /* block form */
  const [blockModalOpen, setBlockModalOpen] = useState(false);
  const [blockForm, setBlockForm] = useState({ tipo: 'ferias', inicio: '', fim: '', motivo: '' });

  async function loadAll() {
    if (!barberId) return;
    try {
      const [wRes, bRes] = await Promise.all([
        api.get(`/barbers/${barberId}/availability/windows`),
        api.get(`/barbers/${barberId}/availability/blocks`),
      ]);
      setWindows(Array.isArray(wRes.data) ? wRes.data : []);
      setBlocks(Array.isArray(bRes.data) ? bRes.data : []);
    } catch {
      toast('Erro ao carregar disponibilidade', 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadAll(); }, [barberId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleAddWindow(e: FormEvent) {
    e.preventDefault();
    try {
      await api.post(`/barbers/${barberId}/availability/windows`, {
        dia_semana: Number(winForm.dia_semana),
        hora_inicio: winForm.hora_inicio,
        hora_fim: winForm.hora_fim,
      });
      toast('Janela adicionada', 'success');
      setWinModalOpen(false);
      loadAll();
    } catch {
      toast('Erro ao adicionar janela', 'error');
    }
  }

  async function handleDeleteWindow(windowId: string) {
    try {
      await api.delete(`/barbers/${barberId}/availability/windows/${windowId}`);
      toast('Janela removida', 'success');
      loadAll();
    } catch {
      toast('Erro ao remover janela', 'error');
    }
  }

  async function handleAddBlock(e: FormEvent) {
    e.preventDefault();
    try {
      await api.post(`/barbers/${barberId}/availability/blocks`, {
        tipo: blockForm.tipo,
        inicio: blockForm.inicio,
        fim: blockForm.fim,
        motivo: blockForm.motivo || null,
      });
      toast('Bloqueio adicionado', 'success');
      setBlockModalOpen(false);
      loadAll();
    } catch {
      toast('Erro ao adicionar bloqueio', 'error');
    }
  }

  async function handleDeleteBlock(blockId: string) {
    try {
      await api.delete(`/barbers/${barberId}/availability/blocks/${blockId}`);
      toast('Bloqueio removido', 'success');
      loadAll();
    } catch {
      toast('Erro ao remover bloqueio', 'error');
    }
  }

  if (!barberId) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
        Guarda o teu Barber ID na página <strong>Minha Agenda</strong> para gerir a disponibilidade.
      </div>
    );
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Disponibilidade</h1>

      {/* Weekly windows */}
      <div className="mb-8">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-medium text-slate-700">Janelas Semanais</h2>
          <Button size="sm" onClick={() => setWinModalOpen(true)}>+ Adicionar Janela</Button>
        </div>
        <Table
          columns={[
            { key: 'weekday', header: 'Dia', render: (w) => weekdayLabel(w.weekday) },
            { key: 'start', header: 'Inicio', render: (w) => w.start_time },
            { key: 'end', header: 'Fim', render: (w) => w.end_time },
            {
              key: 'actions',
              header: '',
              render: (w) => (
                <Button size="sm" variant="danger" onClick={() => handleDeleteWindow(w.id)}>Remover</Button>
              ),
            },
          ]}
          data={windows}
          keyExtractor={(w) => w.id}
          emptyMessage="Nenhuma janela configurada."
        />
      </div>

      {/* Blocks */}
      <div>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-medium text-slate-700">Bloqueios</h2>
          <Button size="sm" onClick={() => setBlockModalOpen(true)}>+ Adicionar Bloqueio</Button>
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
                <Button size="sm" variant="danger" onClick={() => handleDeleteBlock(b.id)}>Remover</Button>
              ),
            },
          ]}
          data={blocks}
          keyExtractor={(b) => b.id}
          emptyMessage="Nenhum bloqueio registado."
        />
      </div>

      {/* Window modal */}
      <Modal open={winModalOpen} onClose={() => setWinModalOpen(false)} title="Nova Janela Semanal">
        <form onSubmit={handleAddWindow} className="space-y-4">
          <Select
            label="Dia da Semana"
            options={WEEKDAYS}
            value={winForm.dia_semana}
            onChange={(e) => setWinForm({ ...winForm, dia_semana: e.target.value })}
          />
          <Input
            label="Hora Inicio"
            type="time"
            step="1"
            value={winForm.hora_inicio.slice(0, 5)}
            onChange={(e) => setWinForm({ ...winForm, hora_inicio: e.target.value + ':00' })}
            required
          />
          <Input
            label="Hora Fim"
            type="time"
            step="1"
            value={winForm.hora_fim.slice(0, 5)}
            onChange={(e) => setWinForm({ ...winForm, hora_fim: e.target.value + ':00' })}
            required
          />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setWinModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Adicionar</Button>
          </div>
        </form>
      </Modal>

      {/* Block modal */}
      <Modal open={blockModalOpen} onClose={() => setBlockModalOpen(false)} title="Novo Bloqueio">
        <form onSubmit={handleAddBlock} className="space-y-4">
          <Select
            label="Tipo"
            options={[
              { value: 'ferias', label: 'Ferias' },
              { value: 'doenca', label: 'Doenca' },
              { value: 'pessoal', label: 'Pessoal' },
              { value: 'outro', label: 'Outro' },
            ]}
            value={blockForm.tipo}
            onChange={(e) => setBlockForm({ ...blockForm, tipo: e.target.value })}
          />
          <Input
            label="Inicio"
            type="datetime-local"
            value={blockForm.inicio}
            onChange={(e) => setBlockForm({ ...blockForm, inicio: e.target.value })}
            required
          />
          <Input
            label="Fim"
            type="datetime-local"
            value={blockForm.fim}
            onChange={(e) => setBlockForm({ ...blockForm, fim: e.target.value })}
            required
          />
          <Input
            label="Motivo (opcional)"
            value={blockForm.motivo}
            onChange={(e) => setBlockForm({ ...blockForm, motivo: e.target.value })}
          />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setBlockModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Adicionar</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
