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

interface ServicePack {
  id: string;
  nome: string;
  service_id: string;
  n_sessoes: number;
  preco: number;
}

interface ClientPack {
  id: string;
  client_id: string;
  service_pack_id: string;
  sessoes_restantes: number;
  expira_em: string | null;
  client_nome?: string;
  pack_nome?: string;
}

interface ServiceOption {
  id: string;
  nome: string;
}

interface ClientOption {
  id: string;
  nome: string;
}

export default function PacksPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();

  const [servicePacks, setServicePacks] = useState<ServicePack[]>([]);
  const [clientPacks, setClientPacks] = useState<ClientPack[]>([]);
  const [services, setServices] = useState<ServiceOption[]>([]);
  const [clients, setClients] = useState<ClientOption[]>([]);
  const [loading, setLoading] = useState(true);

  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [purchaseModalOpen, setPurchaseModalOpen] = useState(false);

  const [createForm, setCreateForm] = useState({
    nome: '',
    service_id: '',
    n_sessoes: 5,
    preco: 0,
  });

  const [purchaseForm, setPurchaseForm] = useState({
    client_id: '',
    service_pack_id: '',
    expira_em: '',
  });

  async function load() {
    try {
      const [spRes, servRes, cliRes] = await Promise.all([
        api.get('/packs/services'),
        api.get('/services/'),
        api.get('/clients/'),
      ]);
      setServicePacks(Array.isArray(spRes.data) ? spRes.data : []);
      setServices(Array.isArray(servRes.data) ? servRes.data : []);
      setClients(Array.isArray(cliRes.data) ? cliRes.data : []);

      try {
        const cpRes = await api.get('/packs/all');
        setClientPacks(Array.isArray(cpRes.data) ? cpRes.data : []);
      } catch {
        setClientPacks([]);
      }
    } catch (err) {
      toast(getApiError(err, 'Erro ao carregar packs'), 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleCreatePack(e: FormEvent) {
    e.preventDefault();
    try {
      await api.post('/packs/services', {
        ...createForm,
        preco: Number(createForm.preco),
        n_sessoes: Number(createForm.n_sessoes),
      });
      toast('Pack criado', 'success');
      setCreateModalOpen(false);
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao criar pack'), 'error');
    }
  }

  async function handlePurchase(e: FormEvent) {
    e.preventDefault();
    try {
      await api.post('/packs/purchase', {
        client_id: purchaseForm.client_id,
        service_pack_id: purchaseForm.service_pack_id,
        expira_em: purchaseForm.expira_em || undefined,
      });
      toast('Pack adquirido', 'success');
      setPurchaseModalOpen(false);
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao adquirir pack'), 'error');
    }
  }

  function serviceName(id: string) {
    return services.find((s) => s.id === id)?.nome ?? id;
  }

  function clientName(id: string) {
    return clients.find((c) => c.id === id)?.nome ?? id;
  }

  function packName(id: string) {
    return servicePacks.find((p) => p.id === id)?.nome ?? id;
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
      {/* Service Packs */}
      <div className="mb-10">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-slate-800">Packs de Servico</h1>
          <Button onClick={() => { setCreateForm({ nome: '', service_id: '', n_sessoes: 5, preco: 0 }); setCreateModalOpen(true); }}>
            + Novo Pack
          </Button>
        </div>

        <Table
          columns={[
            { key: 'nome', header: 'Nome', render: (p) => p.nome },
            { key: 'service', header: 'Servico', render: (p) => serviceName(p.service_id) },
            { key: 'sessoes', header: 'Sessoes', render: (p) => p.n_sessoes },
            {
              key: 'preco',
              header: 'Preco',
              render: (p) =>
                new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' }).format(p.preco),
            },
          ]}
          data={servicePacks}
          keyExtractor={(p) => p.id}
          emptyMessage="Nenhum pack de servico encontrado."
        />
      </div>

      {/* Client Packs */}
      <div>
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-slate-800">Packs de Clientes</h1>
          <Button onClick={() => { setPurchaseForm({ client_id: '', service_pack_id: '', expira_em: '' }); setPurchaseModalOpen(true); }}>
            + Comprar Pack
          </Button>
        </div>

        <Table
          columns={[
            { key: 'client', header: 'Cliente', render: (p) => p.client_nome ?? clientName(p.client_id) },
            { key: 'pack', header: 'Pack', render: (p) => p.pack_nome ?? packName(p.service_pack_id) },
            { key: 'restantes', header: 'Sessoes Restantes', render: (p) => p.sessoes_restantes },
            { key: 'expira', header: 'Expira em', render: (p) => p.expira_em ?? '-' },
          ]}
          data={clientPacks}
          keyExtractor={(p) => p.id}
          emptyMessage="Nenhum pack de cliente encontrado."
        />
      </div>

      {/* Create Service Pack Modal */}
      <Modal open={createModalOpen} onClose={() => setCreateModalOpen(false)} title="Novo Pack de Servico">
        <form onSubmit={handleCreatePack} className="space-y-4">
          <Input
            label="Nome"
            value={createForm.nome}
            onChange={(e) => setCreateForm({ ...createForm, nome: e.target.value })}
            required
            autoFocus
          />
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-slate-700">Servico</label>
            <select
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800"
              value={createForm.service_id}
              onChange={(e) => setCreateForm({ ...createForm, service_id: e.target.value })}
              required
            >
              <option value="" disabled>Selecionar servico</option>
              {services.map((s) => (
                <option key={s.id} value={s.id}>{s.nome}</option>
              ))}
            </select>
          </div>
          <Input
            label="Numero de Sessoes"
            type="number"
            min={1}
            value={createForm.n_sessoes}
            onChange={(e) => setCreateForm({ ...createForm, n_sessoes: Number(e.target.value) })}
            required
          />
          <Input
            label="Preco (EUR)"
            type="number"
            min={0}
            step={0.01}
            value={createForm.preco}
            onChange={(e) => setCreateForm({ ...createForm, preco: Number(e.target.value) })}
            required
          />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setCreateModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Criar</Button>
          </div>
        </form>
      </Modal>

      {/* Purchase Pack Modal */}
      <Modal open={purchaseModalOpen} onClose={() => setPurchaseModalOpen(false)} title="Comprar Pack para Cliente">
        <form onSubmit={handlePurchase} className="space-y-4">
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-slate-700">Cliente</label>
            <select
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800"
              value={purchaseForm.client_id}
              onChange={(e) => setPurchaseForm({ ...purchaseForm, client_id: e.target.value })}
              required
            >
              <option value="" disabled>Selecionar cliente</option>
              {clients.map((c) => (
                <option key={c.id} value={c.id}>{c.nome}</option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-slate-700">Pack</label>
            <select
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800"
              value={purchaseForm.service_pack_id}
              onChange={(e) => setPurchaseForm({ ...purchaseForm, service_pack_id: e.target.value })}
              required
            >
              <option value="" disabled>Selecionar pack</option>
              {servicePacks.map((p) => (
                <option key={p.id} value={p.id}>{p.nome}</option>
              ))}
            </select>
          </div>
          <Input
            label="Data de Expiracao (opcional)"
            type="date"
            value={purchaseForm.expira_em}
            onChange={(e) => setPurchaseForm({ ...purchaseForm, expira_em: e.target.value })}
          />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setPurchaseModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Comprar</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
