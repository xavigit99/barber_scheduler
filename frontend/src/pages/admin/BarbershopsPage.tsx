import { useState, useEffect, type FormEvent } from 'react';
import api, { getApiError } from '../../lib/api';
import Table from '../../components/Table';
import Button from '../../components/Button';
import Modal from '../../components/Modal';
import Input from '../../components/Input';
import Select from '../../components/Select';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../contexts/AuthContext';
import type { Barbershop, Barber, Membership } from '../../types';

const apiBaseUrl = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/$/, '');

function buildBookingShareData(shop: Barbershop) {
  const appBaseUrl = window.location.origin.replace(/\/$/, '');
  const bookingUrl = `${appBaseUrl}/book/${shop.tenant_id}`;
  const qrCodeUrl = `${apiBaseUrl}/public/qr/${shop.tenant_id}`;
  const widgetScriptUrl = `${apiBaseUrl}/public/widget/${shop.tenant_id}`;
  const widgetSnippet = `<script src="${widgetScriptUrl}" async></script>`;

  return {
    bookingUrl,
    qrCodeUrl,
    widgetSnippet,
  };
}

export default function BarbershopsPage() {
  const [shops, setShops] = useState<Barbershop[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Barbershop | null>(null);
  const [nome, setNome] = useState('');
  const { toast } = useToast();
  const { selectTenant, tenantId } = useAuth();
  const [shareShop, setShareShop] = useState<Barbershop | null>(null);

  /* Memberships modal */
  const [membershipsShop, setMembershipsShop] = useState<Barbershop | null>(null);
  const [memberships, setMemberships] = useState<Membership[]>([]);
  const [allBarbers, setAllBarbers] = useState<Barber[]>([]);
  const [memberForm, setMemberForm] = useState({ barber_id: '', role: 'barber' });

  async function openMemberships(shop: Barbershop) {
    setMembershipsShop(shop);
    const [mRes, bRes] = await Promise.all([
      api.get(`/barbershops/${shop.id}/memberships`),
      api.get('/barbers/'),
    ]);
    setMemberships(Array.isArray(mRes.data) ? mRes.data : []);
    setAllBarbers(Array.isArray(bRes.data) ? bRes.data : []);
    setMemberForm({ barber_id: '', role: 'barber' });
  }

  async function handleAddMember(e: FormEvent) {
    e.preventDefault();
    if (!membershipsShop) return;
    try {
      await api.post(`/barbershops/${membershipsShop.id}/memberships`, {
        barber_id: Number(memberForm.barber_id),
        role: memberForm.role,
      });
      toast('Membro adicionado', 'success');
      const res = await api.get(`/barbershops/${membershipsShop.id}/memberships`);
      setMemberships(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      toast(getApiError(err, 'Erro ao adicionar membro'), 'error');
    }
  }

  async function handleRemoveMember(membershipId: number) {
    if (!membershipsShop) return;
    try {
      await api.delete(`/barbershops/${membershipsShop.id}/memberships/${membershipId}`);
      toast('Membro removido', 'success');
      const res = await api.get(`/barbershops/${membershipsShop.id}/memberships`);
      setMemberships(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      toast(getApiError(err, 'Erro ao remover membro'), 'error');
    }
  }

  async function load() {
    try {
      const res = await api.get('/barbershops/', { skipTenantHeader: true });
      setShops(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      toast(getApiError(err, 'Erro ao carregar barbearias'), 'error');
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
    } catch (err) {
      toast(getApiError(err, 'Erro ao guardar barbearia'), 'error');
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Tem a certeza que deseja eliminar?')) return;
    try {
      await api.delete(`/barbershops/${id}`);
      toast('Barbearia eliminada', 'success');
      load();
    } catch (err) {
      toast(getApiError(err, 'Erro ao eliminar barbearia'), 'error');
    }
  }

  function handleSelectTenant(shop: Barbershop) {
    selectTenant(shop.tenant_id, shop.nome);
    toast(`Barbearia seleccionada: ${shop.nome}`, 'success');
  }

  async function handleCopy(value: string, successMessage: string) {
    try {
      await navigator.clipboard.writeText(value);
      toast(successMessage, 'success');
    } catch {
      toast('Não foi possível copiar automaticamente.', 'error');
    }
  }

  if (loading) return <Spinner />;

  const shareData = shareShop ? buildBookingShareData(shareShop) : null;

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
                <Button
                  size="sm"
                  variant={s.tenant_id === tenantId ? 'primary' : 'secondary'}
                  onClick={() => handleSelectTenant(s)}
                >
                  {s.tenant_id === tenantId ? 'Seleccionada ✓' : 'Seleccionar'}
                </Button>
                <Button size="sm" variant="ghost" onClick={() => openMemberships(s)}>
                  Membros
                </Button>
                <Button size="sm" variant="ghost" onClick={() => setShareShop(s)}>
                  Partilha
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
        open={!!membershipsShop}
        onClose={() => setMembershipsShop(null)}
        title={`Membros — ${membershipsShop?.nome ?? ''}`}
      >
        <div className="space-y-4">
          <Table
            columns={[
              { key: 'barber_id', header: 'Barbeiro ID', render: (m) => <span className="font-mono text-xs">{m.barber_id}</span> },
              { key: 'role', header: 'Role', render: (m) => m.role },
              {
                key: 'actions',
                header: '',
                render: (m) => (
                  <Button size="sm" variant="danger" onClick={() => handleRemoveMember(m.id)}>Remover</Button>
                ),
              },
            ]}
            data={memberships}
            keyExtractor={(m) => String(m.id)}
            emptyMessage="Sem membros."
          />
          <form onSubmit={handleAddMember} className="flex gap-2 items-end">
            <div className="flex-1">
              <Select
                label="Barbeiro"
                options={allBarbers.map((b) => ({ value: String(b.id), label: b.nome }))}
                value={memberForm.barber_id}
                onChange={(e) => setMemberForm({ ...memberForm, barber_id: e.target.value })}
              />
            </div>
            <Button type="submit">Adicionar</Button>
          </form>
        </div>
      </Modal>

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

      <Modal
        open={!!shareShop}
        onClose={() => setShareShop(null)}
        title={`Partilha de Booking — ${shareShop?.nome ?? ''}`}
      >
        {shareData && (
          <div className="space-y-5">
            <div className="rounded-xl border border-emerald-100 bg-emerald-50 p-4">
              <p className="text-sm font-medium text-emerald-900">Link público de marcação</p>
              <p className="mt-1 break-all font-mono text-xs text-emerald-800">{shareData.bookingUrl}</p>
              <div className="mt-3 flex gap-2">
                <Button
                  size="sm"
                  onClick={() => handleCopy(shareData.bookingUrl, 'Link de booking copiado')}
                >
                  Copiar link
                </Button>
                <Button size="sm" variant="secondary" onClick={() => window.open(shareData.bookingUrl, '_blank', 'noopener,noreferrer')}>
                  Abrir página
                </Button>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="mb-3 flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-medium text-slate-900">QR code para balcão ou redes sociais</p>
                  <p className="text-xs text-slate-500">Aponta diretamente para a página pública de booking.</p>
                </div>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => window.open(shareData.qrCodeUrl, '_blank', 'noopener,noreferrer')}
                >
                  Abrir QR
                </Button>
              </div>
              <div className="flex justify-center rounded-lg bg-white p-4">
                <img
                  src={shareData.qrCodeUrl}
                  alt={`QR code de booking da barbearia ${shareShop?.nome ?? ''}`}
                  className="h-52 w-52 rounded-lg border border-slate-200 object-contain"
                />
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <div className="mb-3 flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-medium text-slate-900">Widget embed</p>
                  <p className="text-xs text-slate-500">Usa este snippet para embutir o booking num site externo.</p>
                </div>
                <Button
                  size="sm"
                  onClick={() => handleCopy(shareData.widgetSnippet, 'Snippet do widget copiado')}
                >
                  Copiar snippet
                </Button>
              </div>
              <textarea
                readOnly
                value={shareData.widgetSnippet}
                className="min-h-[88px] w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 font-mono text-xs text-slate-700"
              />
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
