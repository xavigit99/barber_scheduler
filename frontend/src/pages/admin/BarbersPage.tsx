import { useState, useEffect, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import api from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';
import Table from '../../components/Table';
import Button from '../../components/Button';
import Modal from '../../components/Modal';
import Input from '../../components/Input';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import type { Barber } from '../../types';

export default function BarbersPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();
  const [barbers, setBarbers] = useState<Barber[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Barber | null>(null);
  const [form, setForm] = useState({ nome: '', email: '', telefone: '', username: '', password: '' });

  async function load() {
    try {
      const res = await api.get('/barbers/');
      setBarbers(Array.isArray(res.data) ? res.data : []);
    } catch {
      toast('Erro ao carregar barbeiros', 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  function openCreate() {
    setEditing(null);
    setForm({ nome: '', email: '', telefone: '', username: '', password: '' });
    setModalOpen(true);
  }

  function openEdit(b: Barber) {
    setEditing(b);
    setForm({ nome: b.nome, email: b.email, telefone: b.telefone, username: '', password: '' });
    setModalOpen(true);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      if (editing) {
        await api.put(`/barbers/${editing.id}`, { nome: form.nome, email: form.email, telefone: form.telefone });
        toast('Barbeiro atualizado', 'success');
      } else {
        await api.post('/auth/register-barber', {
          username: form.username,
          email: form.email,
          password: form.password,
          nome: form.nome,
          telefone: form.telefone || null,
          tenant_id: Number(tenantId),
        });
        toast('Barbeiro criado', 'success');
      }
      setModalOpen(false);
      load();
    } catch {
      toast('Erro ao guardar barbeiro', 'error');
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Eliminar barbeiro?')) return;
    try {
      await api.delete(`/barbers/${id}`);
      toast('Barbeiro eliminado', 'success');
      load();
    } catch {
      toast('Erro ao eliminar barbeiro', 'error');
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
        <h1 className="text-2xl font-semibold text-slate-800">Barbeiros</h1>
        <Button onClick={openCreate}>+ Novo Barbeiro</Button>
      </div>

      <Table
        columns={[
          { key: 'nome', header: 'Nome', render: (b) => b.nome },
          { key: 'email', header: 'Email', render: (b) => b.email },
          { key: 'telefone', header: 'Telefone', render: (b) => b.telefone },
          {
            key: 'actions',
            header: 'Acoes',
            render: (b) => (
              <div className="flex gap-2">
                <Link to={`/admin/barbers/${b.id}/availability`}>
                  <Button size="sm" variant="secondary">Disponibilidade</Button>
                </Link>
                <Button size="sm" variant="ghost" onClick={() => openEdit(b)}>
                  Editar
                </Button>
                <Button size="sm" variant="danger" onClick={() => handleDelete(b.id)}>
                  Eliminar
                </Button>
              </div>
            ),
          },
        ]}
        data={barbers}
        keyExtractor={(b) => b.id}
        emptyMessage="Nenhum barbeiro encontrado."
      />

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Editar Barbeiro' : 'Novo Barbeiro'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Nome"
            value={form.nome}
            onChange={(e) => setForm({ ...form, nome: e.target.value })}
            required
            autoFocus
          />
          <Input
            label="Email"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
          <Input
            label="Telefone"
            value={form.telefone}
            onChange={(e) => setForm({ ...form, telefone: e.target.value })}
          />
          {!editing && (
            <>
              <Input
                label="Username"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                required
              />
              <Input
                label="Password"
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
                minLength={8}
              />
            </>
          )}
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)} type="button">
              Cancelar
            </Button>
            <Button type="submit">{editing ? 'Guardar' : 'Criar'}</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
