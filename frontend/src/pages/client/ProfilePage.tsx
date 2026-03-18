import { useState, useEffect, type FormEvent } from 'react';
import api, { getApiError } from '../../lib/api';
import Input from '../../components/Input';
import Button from '../../components/Button';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../contexts/AuthContext';
import type { Client } from '../../types';

export default function ProfilePage() {
  const { toast } = useToast();
  const { clientId } = useAuth();

  /* Profile */
  const [client, setClient] = useState<Client | null>(null);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ nome: '', email: '', telefone: '' });
  const [saving, setSaving] = useState(false);

  /* Password */
  const [pwForm, setPwForm] = useState({ current_password: '', new_password: '', confirm: '' });
  const [savingPw, setSavingPw] = useState(false);

  useEffect(() => {
    api
      .get('/clients/me')
      .then((res) => {
        const c: Client = res.data;
        setClient(c);
        setForm({ nome: c.nome, email: c.email, telefone: c.telefone ?? '' });
      })
      .catch((err) => toast(getApiError(err, 'Erro ao carregar perfil'), 'error'))
      .finally(() => setLoading(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleSaveProfile(e: FormEvent) {
    e.preventDefault();
    if (!clientId) return;
    setSaving(true);
    try {
      const res = await api.put(`/clients/${clientId}`, {
        nome: form.nome,
        email: form.email,
        telefone: form.telefone || null,
      });
      setClient(res.data);
      toast('Perfil atualizado!', 'success');
    } catch (err) {
      toast(getApiError(err, 'Erro ao atualizar perfil'), 'error');
    } finally {
      setSaving(false);
    }
  }

  async function handleChangePassword(e: FormEvent) {
    e.preventDefault();
    if (pwForm.new_password !== pwForm.confirm) {
      toast('As passwords não coincidem', 'error');
      return;
    }
    setSavingPw(true);
    try {
      await api.post('/auth/change-password', {
        current_password: pwForm.current_password,
        new_password: pwForm.new_password,
      });
      toast('Password alterada!', 'success');
      setPwForm({ current_password: '', new_password: '', confirm: '' });
    } catch (err) {
      toast(getApiError(err, 'Erro ao alterar password'), 'error');
    } finally {
      setSavingPw(false);
    }
  }

  if (loading) return <Spinner />;
  if (!client) return <p className="text-sm text-slate-500">Perfil não encontrado.</p>;

  return (
    <div className="mx-auto max-w-lg space-y-10">
      <h1 className="text-2xl font-semibold text-slate-800">O meu perfil</h1>

      {/* Profile form */}
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-5 text-base font-medium text-slate-700">Dados pessoais</h2>
        <form onSubmit={handleSaveProfile} className="space-y-4">
          <Input
            label="Nome"
            value={form.nome}
            onChange={(e) => setForm({ ...form, nome: e.target.value })}
            required
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
          <div className="flex justify-end">
            <Button type="submit" disabled={saving}>{saving ? 'A guardar...' : 'Guardar'}</Button>
          </div>
        </form>
      </section>

      {/* Password form */}
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-5 text-base font-medium text-slate-700">Alterar password</h2>
        <form onSubmit={handleChangePassword} className="space-y-4">
          <Input
            label="Password atual"
            type="password"
            value={pwForm.current_password}
            onChange={(e) => setPwForm({ ...pwForm, current_password: e.target.value })}
            required
          />
          <Input
            label="Nova password"
            type="password"
            value={pwForm.new_password}
            onChange={(e) => setPwForm({ ...pwForm, new_password: e.target.value })}
            minLength={8}
            required
          />
          <Input
            label="Confirmar nova password"
            type="password"
            value={pwForm.confirm}
            onChange={(e) => setPwForm({ ...pwForm, confirm: e.target.value })}
            required
          />
          <div className="flex justify-end">
            <Button type="submit" disabled={savingPw}>{savingPw ? 'A guardar...' : 'Alterar password'}</Button>
          </div>
        </form>
      </section>
    </div>
  );
}
