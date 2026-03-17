import { useState, type FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useToast } from '../../components/Toast';
import api from '../../lib/api';

export default function ClientRegisterPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [nome, setNome] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  function validate(): boolean {
    const next: Record<string, string> = {};

    if (nome.trim().length < 2) next.nome = 'Nome deve ter pelo menos 2 caracteres';
    if (username.trim().length < 2) next.username = 'Username deve ter pelo menos 2 caracteres';

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) next.email = 'Email inválido';
    if (password.length < 8) next.password = 'A password deve ter pelo menos 8 caracteres';
    if (password !== confirmPassword) next.confirmPassword = 'As passwords não coincidem';

    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      await api.post('/auth/register', {
        nome,
        username,
        email,
        password,
        tenant_id: Number(tenantId),
      });
      toast('Conta criada! Podes entrar agora.', 'success');
      navigate('/login', { replace: true });
    } catch (err: unknown) {
      let message = 'Erro ao criar conta. Tenta novamente.';
      if (
        typeof err === 'object' &&
        err !== null &&
        'response' in err &&
        typeof (err as Record<string, unknown>).response === 'object'
      ) {
        const resp = (err as { response: { data?: { detail?: string } } }).response;
        if (resp.data?.detail) message = resp.data.detail;
      }
      toast(message, 'error');
    } finally {
      setLoading(false);
    }
  }

  const inputClasses =
    'w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-4 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-amber-500 transition-colors';
  const inputErrorClasses =
    'w-full rounded-xl border border-red-500 bg-slate-800 px-4 py-4 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-amber-500 transition-colors';

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center px-4 py-10">
      <div className="w-full max-w-sm">
        {/* Brand */}
        <div className="mb-8 flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-amber-500 flex items-center justify-center text-slate-900 font-bold text-sm">
            B
          </div>
          <span className="text-white font-semibold text-lg">BarberPro</span>
        </div>

        <h1 className="text-2xl font-bold text-white mb-1">Criar conta</h1>
        <p className="text-sm text-slate-400 mb-8">
          Cria a tua conta para gerir os teus agendamentos.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Nome */}
          <div className="flex flex-col gap-1.5">
            <label className="text-sm text-slate-400">Nome completo</label>
            <input
              type="text"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              autoFocus
              placeholder="O teu nome"
              className={errors.nome ? inputErrorClasses : inputClasses}
            />
            {errors.nome && <span className="text-xs text-red-400">{errors.nome}</span>}
          </div>

          {/* Username */}
          <div className="flex flex-col gap-1.5">
            <label className="text-sm text-slate-400">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Ex: joao_silva"
              className={errors.username ? inputErrorClasses : inputClasses}
            />
            {errors.username && <span className="text-xs text-red-400">{errors.username}</span>}
          </div>

          {/* Email */}
          <div className="flex flex-col gap-1.5">
            <label className="text-sm text-slate-400">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="email@exemplo.com"
              className={errors.email ? inputErrorClasses : inputClasses}
            />
            {errors.email && <span className="text-xs text-red-400">{errors.email}</span>}
          </div>

          {/* Password */}
          <div className="flex flex-col gap-1.5">
            <label className="text-sm text-slate-400">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Mínimo 8 caracteres"
              className={errors.password ? inputErrorClasses : inputClasses}
            />
            {errors.password && <span className="text-xs text-red-400">{errors.password}</span>}
          </div>

          {/* Confirm password */}
          <div className="flex flex-col gap-1.5">
            <label className="text-sm text-slate-400">Confirmar password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Repete a password"
              className={errors.confirmPassword ? inputErrorClasses : inputClasses}
            />
            {errors.confirmPassword && (
              <span className="text-xs text-red-400">{errors.confirmPassword}</span>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-amber-500 py-4 text-slate-900 font-bold text-sm hover:bg-amber-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {loading ? 'A criar conta...' : 'Criar conta'}
          </button>
        </form>

        <div className="mt-6 text-center space-y-3">
          <p className="text-sm text-slate-400">
            Já tens conta?{' '}
            <Link to={`/signin/${tenantId}`} className="text-amber-400 font-medium hover:text-amber-300">
              Inicia sessão
            </Link>
          </p>
          <p className="text-sm text-slate-400">
            Queres marcar sem conta?{' '}
            <Link to={`/book/${tenantId}`} className="text-amber-400 font-medium hover:text-amber-300">
              Marcar agora
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
