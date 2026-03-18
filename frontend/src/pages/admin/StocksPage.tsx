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

interface Product {
  id: string;
  nome: string;
  descricao: string | null;
  stock_atual: number;
  stock_minimo: number;
  preco_unitario: number;
}

export default function StocksPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();

  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [stockModalOpen, setStockModalOpen] = useState(false);

  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const [createForm, setCreateForm] = useState({
    nome: '',
    descricao: '',
    stock_minimo: 5,
    preco_unitario: 0,
  });

  const [editForm, setEditForm] = useState({
    nome: '',
    descricao: '',
    stock_minimo: 0,
    preco_unitario: 0,
  });

  const [stockForm, setStockForm] = useState({ delta: 0, reason: '' });

  async function load() {
    try {
      const res = await api.get('/products');
      setProducts(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      toast(getApiError(err, 'Erro ao carregar produtos'), 'error');
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
      await api.post('/products', {
        nome: createForm.nome,
        descricao: createForm.descricao || null,
        stock_minimo: Number(createForm.stock_minimo),
        preco_unitario: Number(createForm.preco_unitario),
      });
      toast('Produto criado', 'success');
      setCreateModalOpen(false);
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao criar produto'), 'error');
    }
  }

  function openEdit(p: Product) {
    setSelectedProduct(p);
    setEditForm({
      nome: p.nome,
      descricao: p.descricao ?? '',
      stock_minimo: p.stock_minimo,
      preco_unitario: p.preco_unitario,
    });
    setEditModalOpen(true);
  }

  async function handleEdit(e: FormEvent) {
    e.preventDefault();
    if (!selectedProduct) return;
    try {
      await api.put(`/products/${selectedProduct.id}`, {
        nome: editForm.nome,
        descricao: editForm.descricao || null,
        stock_minimo: Number(editForm.stock_minimo),
        preco_unitario: Number(editForm.preco_unitario),
      });
      toast('Produto atualizado', 'success');
      setEditModalOpen(false);
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao atualizar produto'), 'error');
    }
  }

  function openStockAdjust(p: Product) {
    setSelectedProduct(p);
    setStockForm({ delta: 0, reason: '' });
    setStockModalOpen(true);
  }

  async function handleStockAdjust(e: FormEvent) {
    e.preventDefault();
    if (!selectedProduct) return;
    try {
      await api.post(`/products/${selectedProduct.id}/stock`, {
        delta: Number(stockForm.delta),
        reason: stockForm.reason,
      });
      toast('Stock ajustado', 'success');
      setStockModalOpen(false);
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao ajustar stock'), 'error');
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Eliminar produto?')) return;
    try {
      await api.delete(`/products/${id}`);
      toast('Produto eliminado', 'success');
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao eliminar produto'), 'error');
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
        <h1 className="text-2xl font-semibold text-slate-800">Stocks</h1>
        <Button onClick={() => { setCreateForm({ nome: '', descricao: '', stock_minimo: 5, preco_unitario: 0 }); setCreateModalOpen(true); }}>
          + Novo Produto
        </Button>
      </div>

      <Table
        columns={[
          { key: 'nome', header: 'Nome', render: (p) => p.nome },
          {
            key: 'stock',
            header: 'Stock Atual',
            render: (p) => (
              <span className={p.stock_atual <= p.stock_minimo ? 'text-amber-600 font-semibold' : ''}>
                {p.stock_atual}
              </span>
            ),
          },
          { key: 'minimo', header: 'Stock Minimo', render: (p) => p.stock_minimo },
          {
            key: 'preco',
            header: 'Preco Unit.',
            render: (p) =>
              new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' }).format(p.preco_unitario),
          },
          {
            key: 'actions',
            header: 'Acoes',
            render: (p) => (
              <div className="flex gap-2">
                <Button size="sm" variant="ghost" onClick={() => openStockAdjust(p)}>Ajustar Stock</Button>
                <Button size="sm" variant="ghost" onClick={() => openEdit(p)}>Editar</Button>
                <Button size="sm" variant="danger" onClick={() => handleDelete(p.id)}>Eliminar</Button>
              </div>
            ),
          },
        ]}
        data={products}
        keyExtractor={(p) => p.id}
        emptyMessage="Nenhum produto encontrado."
      />

      {/* Create Modal */}
      <Modal open={createModalOpen} onClose={() => setCreateModalOpen(false)} title="Novo Produto">
        <form onSubmit={handleCreate} className="space-y-4">
          <Input label="Nome" value={createForm.nome} onChange={(e) => setCreateForm({ ...createForm, nome: e.target.value })} required autoFocus />
          <Input label="Descricao" value={createForm.descricao} onChange={(e) => setCreateForm({ ...createForm, descricao: e.target.value })} />
          <Input label="Stock Minimo" type="number" min={0} value={createForm.stock_minimo} onChange={(e) => setCreateForm({ ...createForm, stock_minimo: Number(e.target.value) })} required />
          <Input label="Preco Unitario (EUR)" type="number" min={0} step={0.01} value={createForm.preco_unitario} onChange={(e) => setCreateForm({ ...createForm, preco_unitario: Number(e.target.value) })} required />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setCreateModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Criar</Button>
          </div>
        </form>
      </Modal>

      {/* Edit Modal */}
      <Modal open={editModalOpen} onClose={() => setEditModalOpen(false)} title="Editar Produto">
        <form onSubmit={handleEdit} className="space-y-4">
          <Input label="Nome" value={editForm.nome} onChange={(e) => setEditForm({ ...editForm, nome: e.target.value })} required autoFocus />
          <Input label="Descricao" value={editForm.descricao} onChange={(e) => setEditForm({ ...editForm, descricao: e.target.value })} />
          <Input label="Stock Minimo" type="number" min={0} value={editForm.stock_minimo} onChange={(e) => setEditForm({ ...editForm, stock_minimo: Number(e.target.value) })} required />
          <Input label="Preco Unitario (EUR)" type="number" min={0} step={0.01} value={editForm.preco_unitario} onChange={(e) => setEditForm({ ...editForm, preco_unitario: Number(e.target.value) })} required />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setEditModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Guardar</Button>
          </div>
        </form>
      </Modal>

      {/* Stock Adjust Modal */}
      <Modal open={stockModalOpen} onClose={() => setStockModalOpen(false)} title={`Ajustar Stock — ${selectedProduct?.nome ?? ''}`}>
        <form onSubmit={handleStockAdjust} className="space-y-4">
          <p className="text-sm text-slate-600">Stock atual: {selectedProduct?.stock_atual ?? 0}</p>
          <Input
            label="Delta (positivo ou negativo)"
            type="number"
            value={stockForm.delta}
            onChange={(e) => setStockForm({ ...stockForm, delta: Number(e.target.value) })}
            required
            autoFocus
          />
          <Input
            label="Motivo"
            value={stockForm.reason}
            onChange={(e) => setStockForm({ ...stockForm, reason: e.target.value })}
            required
          />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setStockModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Ajustar</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
