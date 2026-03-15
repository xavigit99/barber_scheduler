import { useState, useEffect, type FormEvent } from 'react';
import api from '../../lib/api';
import Table from '../../components/Table';
import Button from '../../components/Button';
import Modal from '../../components/Modal';
import Input from '../../components/Input';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../contexts/AuthContext';
import type { Barbershop } from '../../types';

export default function BarbershopsPage() {
  const [shops, setShops] = useState<Barbershop[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Barbershop | null>(null);
  const [nome, setNome] = useState('');
  const { toast } = useToast();
  const { selectTenant } = useAuth();

  async function load() {
    try {
      const res = await api.get('/barbershops/');
      setShops(Array.isArray(res.data) ? res.data : []);
    } catch {
      toast('Erro ao carregar barbearias', 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  function openCreate() {
    setEditing(null);
    setNome('');
    setModalOpen(true);
  }

  function openEdit(shop: Barbershop) {
    setEditing(shop);
    setNome(shop.nome);
    setModalOpen(true);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      if (editing) {
        await api.put(`/barbershops/${editing.id}`, { nome });
        toast('Barbearia atualizada', 'success');
      } else {
        await api.post('/barbershops/', { nome });
        toast('Barbearia criada', 'success');
      }
      setModalOpen(false);
      load();
    } catch {
      toast('Erro ao guardar barbearia', 'error');
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Tem a certeza que deseja eliminar?')) return;
    try {
      await api.delete(`/barbershops/${id}`);
      toast('Barbearia eliminada', 'success');
      load();
    } catch {
      toast('Erro ao eliminar barbearia', 'error');
    }
  }

  function handleSelectTenant(shop: Barbershop) {
    selectTenant(shop.tenant_id);
    toast(`Tenant selecionado: ${shop.nome}`, 'success');
  }

  if (loading) return <Spinner />;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-800">Barbearias</h1>
        <Button onClick={openCreate}>+ Nova Barbearia</Button>
      </div>

      <Table
        columns={[
          { key: 'nome', header: 'Nome', render: (s) => s.nome },
          {
            key: 'tenant_id',
            header: 'Tenant ID',
            render: (s) => <span className="font-mono text-xs">{s.tenant_id}</span>,
          },
          {
            key: 'actions',
            header: 'Acoes',
            render: (s) => (
              <div className="flex gap-2">
                <Button size="sm" variant="secondary" onClick={() => handleSelectTenant(s)}>
                  Selecionar
                </Button>
                <Button size="sm" variant="ghost" onClick={() => openEdit(s)}>
                  Editar
                </Button>
                <Button size="sm" variant="danger" onClick={() => handleDelete(s.id)}>
                  Eliminar
                </Button>
              </div>
            ),
          },
        ]}
        data={shops}
        keyExtractor={(s) => s.id}
        emptyMessage="Nenhuma barbearia encontrada."
      />

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Editar Barbearia' : 'Nova Barbearia'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Nome"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            required
            autoFocus
          />
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
