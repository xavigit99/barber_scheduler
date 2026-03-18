import { useState, useEffect, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import api, { getApiError } from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';
import Button from '../../components/Button';
import Modal from '../../components/Modal';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';

interface ClientOption {
  id: string;
  nome: string;
}

interface ClinicalRecord {
  alergias: string | null;
  notas_saude: string | null;
  consentimento_assinado: boolean;
  consentimento_data: string | null;
}

interface ClinicalNote {
  id: string;
  barber_id: string;
  nota: string;
  created_at: string;
  barber_nome?: string;
}

export default function ClinicalPage() {
  const { tenantId } = useAuth();
  const { toast } = useToast();

  const [clients, setClients] = useState<ClientOption[]>([]);
  const [selectedClientId, setSelectedClientId] = useState('');
  const [loading, setLoading] = useState(true);
  const [recordLoading, setRecordLoading] = useState(false);

  const [record, setRecord] = useState<ClinicalRecord | null>(null);
  const [notes, setNotes] = useState<ClinicalNote[]>([]);

  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editForm, setEditForm] = useState({ alergias: '', notas_saude: '' });

  const [noteModalOpen, setNoteModalOpen] = useState(false);
  const [noteForm, setNoteForm] = useState('');

  useEffect(() => {
    async function loadClients() {
      try {
        const res = await api.get('/clients/');
        setClients(Array.isArray(res.data) ? res.data : []);
      } catch (err) {
        toast(getApiError(err, 'Erro ao carregar clientes'), 'error');
      } finally {
        setLoading(false);
      }
    }
    loadClients();
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function loadRecord(clientId: string) {
    setRecordLoading(true);
    try {
      const [recRes, notesRes] = await Promise.all([
        api.get(`/clinical/${clientId}`),
        api.get(`/clinical/${clientId}/notes`),
      ]);
      setRecord(recRes.data);
      setNotes(Array.isArray(notesRes.data) ? notesRes.data : []);
    } catch {
      setRecord(null);
      setNotes([]);
    } finally {
      setRecordLoading(false);
    }
  }

  function handleSelectClient(clientId: string) {
    setSelectedClientId(clientId);
    if (clientId) {
      loadRecord(clientId);
    } else {
      setRecord(null);
      setNotes([]);
    }
  }

  function openEdit() {
    setEditForm({
      alergias: record?.alergias ?? '',
      notas_saude: record?.notas_saude ?? '',
    });
    setEditModalOpen(true);
  }

  async function handleEdit(e: FormEvent) {
    e.preventDefault();
    try {
      await api.put(`/clinical/${selectedClientId}`, {
        alergias: editForm.alergias || null,
        notas_saude: editForm.notas_saude || null,
      });
      toast('Ficha atualizada', 'success');
      setEditModalOpen(false);
      loadRecord(selectedClientId);
    } catch (err) {
      toast(getApiError(err, 'Erro ao atualizar ficha'), 'error');
    }
  }

  async function handleConsent() {
    try {
      await api.post(`/clinical/${selectedClientId}/consent`);
      toast('Consentimento assinado', 'success');
      loadRecord(selectedClientId);
    } catch (err) {
      toast(getApiError(err, 'Erro ao assinar consentimento'), 'error');
    }
  }

  async function handleAddNote(e: FormEvent) {
    e.preventDefault();
    try {
      await api.post(`/clinical/${selectedClientId}/notes`, { nota: noteForm });
      toast('Nota adicionada', 'success');
      setNoteModalOpen(false);
      setNoteForm('');
      loadRecord(selectedClientId);
    } catch (err) {
      toast(getApiError(err, 'Erro ao adicionar nota'), 'error');
    }
  }

  const selectedClientName = clients.find((c) => c.id === selectedClientId)?.nome ?? '';

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
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Fichas Clinicas</h1>

      {/* Client selector */}
      <div className="mb-6">
        <label className="text-sm font-medium text-slate-700 block mb-1">Selecionar Cliente</label>
        <select
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 w-full max-w-md"
          value={selectedClientId}
          onChange={(e) => handleSelectClient(e.target.value)}
        >
          <option value="">-- Selecionar --</option>
          {clients.map((c) => (
            <option key={c.id} value={c.id}>{c.nome}</option>
          ))}
        </select>
      </div>

      {recordLoading && <Spinner />}

      {selectedClientId && !recordLoading && (
        <div className="space-y-6">
          {/* Clinical record card */}
          <div className="rounded-xl bg-white p-6 shadow-sm border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-800">Ficha de {selectedClientName}</h2>
              <div className="flex gap-2">
                <Button size="sm" onClick={openEdit}>Editar Ficha</Button>
                {!record?.consentimento_assinado && (
                  <Button size="sm" variant="secondary" onClick={handleConsent}>Assinar Consentimento</Button>
                )}
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-slate-600">Alergias:</span>
                <p className="text-slate-800 mt-1">{record?.alergias || 'Nenhuma registada'}</p>
              </div>
              <div>
                <span className="font-medium text-slate-600">Notas de Saude:</span>
                <p className="text-slate-800 mt-1">{record?.notas_saude || 'Nenhuma'}</p>
              </div>
              <div>
                <span className="font-medium text-slate-600">Consentimento:</span>
                <span className="ml-2">
                  {record?.consentimento_assinado ? (
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">Assinado</span>
                  ) : (
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-700">Pendente</span>
                  )}
                </span>
              </div>
              {record?.consentimento_data && (
                <div>
                  <span className="font-medium text-slate-600">Data Consentimento:</span>
                  <p className="text-slate-800 mt-1">{new Date(record.consentimento_data).toLocaleDateString('pt-PT')}</p>
                </div>
              )}
            </div>
          </div>

          {/* Notes section */}
          <div className="rounded-xl bg-white p-6 shadow-sm border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-800">Notas</h2>
              <Button size="sm" onClick={() => { setNoteForm(''); setNoteModalOpen(true); }}>
                + Adicionar Nota
              </Button>
            </div>
            {notes.length === 0 ? (
              <p className="text-sm text-slate-400">Nenhuma nota registada.</p>
            ) : (
              <div className="space-y-3">
                {notes.map((n) => (
                  <div key={n.id} className="border-l-2 border-emerald-400 pl-3 py-1">
                    <p className="text-sm text-slate-800">{n.nota}</p>
                    <p className="text-xs text-slate-400 mt-1">
                      {n.barber_nome ?? `Barbeiro ${String(n.barber_id).slice(0, 6)}`} — {new Date(n.created_at).toLocaleString('pt-PT')}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Edit Modal */}
      <Modal open={editModalOpen} onClose={() => setEditModalOpen(false)} title="Editar Ficha Clinica">
        <form onSubmit={handleEdit} className="space-y-4">
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-slate-700">Alergias</label>
            <textarea
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 min-h-[80px]"
              value={editForm.alergias}
              onChange={(e) => setEditForm({ ...editForm, alergias: e.target.value })}
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-slate-700">Notas de Saude</label>
            <textarea
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 min-h-[80px]"
              value={editForm.notas_saude}
              onChange={(e) => setEditForm({ ...editForm, notas_saude: e.target.value })}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setEditModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Guardar</Button>
          </div>
        </form>
      </Modal>

      {/* Add Note Modal */}
      <Modal open={noteModalOpen} onClose={() => setNoteModalOpen(false)} title="Adicionar Nota">
        <form onSubmit={handleAddNote} className="space-y-4">
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-slate-700">Nota</label>
            <textarea
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 min-h-[100px]"
              value={noteForm}
              onChange={(e) => setNoteForm(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setNoteModalOpen(false)} type="button">Cancelar</Button>
            <Button type="submit">Adicionar</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
