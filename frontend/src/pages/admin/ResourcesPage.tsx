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

interface Resource {
  id: string;
  nome: string;
  tipo: string;
}

export default function ResourcesPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();

  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({ nome: '', tipo: 'sala' });

  async function load() {
    try {
      const res = await api.get('/resources');
      setResources(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      toast(getApiError(err, 'Erro ao carregar recursos'), 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    try {
      await api.post('/resources', form);
      toast('Recurso criado', 'success');
      setModalOpen(false);
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao criar recurso'), 'error');
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Eliminar recurso?')) return;
    try {
      await api.delete(`/resources/${id}`);
      toast('Recurso eliminado', 'success');
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao eliminar recurso'), 'error');
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
        <h1 className="text-2xl font-semibold text-slate-800">Recursos</h1>
        <Button onClick={() => { setForm({ nome: '', tipo: 'sala' }); setModalOpen(true); }}>
          + Novo Recurso
        </Button>
      </div>

      <Table
        columns={[
          { key: 'nome', header: 'Nome', render: (r) => r.nome },
          { key: 'tipo', header: 'Tipo', render: (r) => r.tipo },
          {
            key: 'actions',
            header: 'Acoes',
            render: (r) => (
              <Button size="sm" variant="danger" onClick={() => handleDelete(r.id)}>Eliminar</Button>
            ),
          },
        ]}
        data={resources}
        keyExtractor={(r) => r.id}
        emptyMessage="Nenhum recurso encontrado."
      />

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Novo Recurso">
        <form onSubmit={handleCreate} className="space-y-4">
          <Input
            label="Nome"
            value={form.nome}
            onChange={(e) => setForm({ ...form, nome: e.target.value })}
            required
            autoFocus
          />
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-slate-700">Tipo</label>
            <select
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800"
              value={form.tipo}
              onChange={(e) => setForm({ ...form, tipo: e.target.value })}
            >
              <option value="sala">Sala</option>
              <option value="cadeira">Cadeira</option>
              <option value="equipamento">Equipamento</option>
            </select>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Criar</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
