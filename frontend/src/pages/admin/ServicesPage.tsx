import { useState, useEffect, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import api, { getApiError } from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';
import Table from '../../components/Table';
import Button from '../../components/Button';
import Modal from '../../components/Modal';
import Input from '../../components/Input';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import type { Service } from '../../types';

export default function ServicesPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Service | null>(null);
  const [form, setForm] = useState({ nome: '', duracao_minutos: 30, preco: 0 });

  async function load() {
    try {
      const res = await api.get('/services/');
      setServices(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      toast(getApiError(err, 'Erro ao carregar servicos'), 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  function openCreate() {
    setEditing(null);
    setForm({ nome: '', duracao_minutos: 30, preco: 0 });
    setModalOpen(true);
  }

  function openEdit(s: Service) {
    setEditing(s);
    setForm({ nome: s.nome, duracao_minutos: s.duracao_minutos, preco: s.preco });
    setModalOpen(true);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const body = { ...form, tenant_id: tenantId };
    try {
      if (editing) {
        await api.put(`/services/${editing.id}`, body);
        toast('Servico atualizado', 'success');
      } else {
        await api.post('/services/', body);
        toast('Servico criado', 'success');
      }
      setModalOpen(false);
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao guardar servico'), 'error');
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Eliminar servico?')) return;
    try {
      await api.delete(`/services/${id}`);
      toast('Servico eliminado', 'success');
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao eliminar servico'), 'error');
    }
  }

  if (!tenantId) {
    return (
      <div className="py-12 text-center text-slate-500">
        Selecione um tenant em <Link to="/admin/barbershops" className="text-emerald-600 underline">Barbearias</Link> primeiro.
      </div>
    );
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-800">Servicos</h1>
        <Button onClick={openCreate}>+ Novo Servico</Button>
      </div>

      <Table
        columns={[
          { key: 'nome', header: 'Nome', render: (s) => s.nome },
          { key: 'duracao', header: 'Duracao (min)', render: (s) => `${s.duracao_minutos} min` },
          {
            key: 'preco',
            header: 'Preco',
            render: (s) =>
              new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' }).format(s.preco),
          },
          {
            key: 'actions',
            header: 'Acoes',
            render: (s) => (
              <div className="flex gap-2">
                <Button size="sm" variant="ghost" onClick={() => openEdit(s)}>Editar</Button>
                <Button size="sm" variant="danger" onClick={() => handleDelete(s.id)}>Eliminar</Button>
              </div>
            ),
          },
        ]}
        data={services}
        keyExtractor={(s) => s.id}
        emptyMessage="Nenhum servico encontrado."
      />

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Editar Servico' : 'Novo Servico'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Nome" value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} required autoFocus />
          <Input
            label="Duracao (minutos)"
            type="number"
            min={5}
            value={form.duracao_minutos}
            onChange={(e) => setForm({ ...form, duracao_minutos: Number(e.target.value) })}
            required
          />
          <Input
            label="Preco (EUR)"
            type="number"
            min={0}
            step={0.01}
            value={form.preco}
            onChange={(e) => setForm({ ...form, preco: Number(e.target.value) })}
            required
          />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">{editing ? 'Guardar' : 'Criar'}</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
