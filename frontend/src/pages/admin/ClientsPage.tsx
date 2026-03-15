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
import type { Client } from '../../types';

export default function ClientsPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Client | null>(null);
  const [form, setForm] = useState({ nome: '', email: '', telefone: '' });

  async function load() {
    try {
      const res = await api.get('/clients/');
      setClients(Array.isArray(res.data) ? res.data : []);
    } catch {
      toast('Erro ao carregar clientes', 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  function openCreate() {
    setEditing(null);
    setForm({ nome: '', email: '', telefone: '' });
    setModalOpen(true);
  }

  function openEdit(c: Client) {
    setEditing(c);
    setForm({ nome: c.nome, email: c.email, telefone: c.telefone });
    setModalOpen(true);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const body = { ...form, tenant_id: tenantId };
    try {
      if (editing) {
        await api.put(`/clients/${editing.id}`, body);
        toast('Cliente atualizado', 'success');
      } else {
        await api.post('/clients/', body);
        toast('Cliente criado', 'success');
      }
      setModalOpen(false);
      load();
    } catch {
      toast('Erro ao guardar cliente', 'error');
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Eliminar cliente?')) return;
    try {
      await api.delete(`/clients/${id}`);
      toast('Cliente eliminado', 'success');
      load();
    } catch {
      toast('Erro ao eliminar cliente', 'error');
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
        <h1 className="text-2xl font-semibold text-slate-800">Clientes</h1>
        <Button onClick={openCreate}>+ Novo Cliente</Button>
      </div>

      <Table
        columns={[
          { key: 'nome', header: 'Nome', render: (c) => c.nome },
          { key: 'email', header: 'Email', render: (c) => c.email },
          { key: 'telefone', header: 'Telefone', render: (c) => c.telefone },
          {
            key: 'actions',
            header: 'Acoes',
            render: (c) => (
              <div className="flex gap-2">
                <Button size="sm" variant="ghost" onClick={() => openEdit(c)}>Editar</Button>
                <Button size="sm" variant="danger" onClick={() => handleDelete(c.id)}>Eliminar</Button>
              </div>
            ),
          },
        ]}
        data={clients}
        keyExtractor={(c) => c.id}
        emptyMessage="Nenhum cliente encontrado."
      />

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Editar Cliente' : 'Novo Cliente'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Nome" value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} required autoFocus />
          <Input label="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <Input label="Telefone" value={form.telefone} onChange={(e) => setForm({ ...form, telefone: e.target.value })} required />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">{editing ? 'Guardar' : 'Criar'}</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
