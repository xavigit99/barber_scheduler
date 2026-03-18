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

interface ClientWithLoyalty {
  id: string;
  nome: string;
  email: string;
  pontos_total: number;
  pontos_disponiveis: number;
}

export default function LoyaltyPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();

  const [clients, setClients] = useState<ClientWithLoyalty[]>([]);
  const [loading, setLoading] = useState(true);
  const [redeemModalOpen, setRedeemModalOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState<ClientWithLoyalty | null>(null);
  const [redeemForm, setRedeemForm] = useState({ pontos: 0, descricao: '' });

  async function load() {
    try {
      const cliRes = await api.get('/clients/');
      const clientList = Array.isArray(cliRes.data) ? cliRes.data : [];

      const enriched: ClientWithLoyalty[] = await Promise.all(
        clientList.map(async (c: { id: string; nome: string; email: string }) => {
          try {
            const loyRes = await api.get(`/loyalty/${c.id}`);
            return {
              ...c,
              pontos_total: loyRes.data.pontos_total ?? 0,
              pontos_disponiveis: loyRes.data.pontos_disponiveis ?? 0,
            };
          } catch {
            return { ...c, pontos_total: 0, pontos_disponiveis: 0 };
          }
        }),
      );
      setClients(enriched);
    } catch (err) {
      toast(getApiError(err, 'Erro ao carregar fidelizacao'), 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  function openRedeem(client: ClientWithLoyalty) {
    setSelectedClient(client);
    setRedeemForm({ pontos: 0, descricao: '' });
    setRedeemModalOpen(true);
  }

  async function handleRedeem(e: FormEvent) {
    e.preventDefault();
    if (!selectedClient) return;
    try {
      await api.post('/loyalty/redeem', {
        client_id: selectedClient.id,
        pontos: Number(redeemForm.pontos),
        descricao: redeemForm.descricao,
      });
      toast('Pontos resgatados', 'success');
      setRedeemModalOpen(false);
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao resgatar pontos'), 'error');
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
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Fidelizacao</h1>

      <Table
        columns={[
          { key: 'nome', header: 'Cliente', render: (c) => c.nome },
          { key: 'total', header: 'Pontos Total', render: (c) => c.pontos_total },
          { key: 'disponiveis', header: 'Pontos Disponiveis', render: (c) => c.pontos_disponiveis },
          {
            key: 'actions',
            header: 'Acoes',
            render: (c) => (
              <Button size="sm" onClick={() => openRedeem(c)}>Resgatar</Button>
            ),
          },
        ]}
        data={clients}
        keyExtractor={(c) => c.id}
        emptyMessage="Nenhum cliente encontrado."
      />

      <Modal open={redeemModalOpen} onClose={() => setRedeemModalOpen(false)} title={`Resgatar Pontos — ${selectedClient?.nome ?? ''}`}>
        <form onSubmit={handleRedeem} className="space-y-4">
          <Input
            label="Pontos a resgatar"
            type="number"
            min={1}
            max={selectedClient?.pontos_disponiveis ?? 0}
            value={redeemForm.pontos}
            onChange={(e) => setRedeemForm({ ...redeemForm, pontos: Number(e.target.value) })}
            required
            autoFocus
          />
          <Input
            label="Descricao"
            value={redeemForm.descricao}
            onChange={(e) => setRedeemForm({ ...redeemForm, descricao: e.target.value })}
            required
          />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setRedeemModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Resgatar</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
