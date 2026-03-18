import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useToast } from '../components/Toast';
import api, { getApiError } from '../lib/api';

export default function AdminRegisterPage() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [confirmBootstrap, setConfirmBootstrap] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  function validate(): boolean {
    const next: Record<string, string> = {};

    if (username.trim().length < 2) {
      next.username = 'Nome de utilizador deve ter pelo menos 2 caracteres';
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      next.email = 'Email invalido';
    }

    if (password.length < 8) {
      next.password = 'A password deve ter pelo menos 8 caracteres';
    }

    if (password !== confirmPassword) {
      next.confirmPassword = 'As passwords nao coincidem';
    }

    if (!confirmBootstrap) {
      next.confirmBootstrap = 'Confirma que queres criar o primeiro administrador do sistema';
    }

    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      await api.post('/auth/bootstrap-admin', {
        username,
        email,
        password,
      });
      toast('Administrador criado com sucesso!', 'success');
      navigate('/login', { replace: true });
    } catch (err) {
      toast(getApiError(err, 'Erro ao criar administrador. Verifica se o bootstrap ja foi usado.'), 'error');
    } finally {
      setLoading(false);
    }
  }

  const inputClasses =
    'rounded-lg border border-slate-700 bg-slate-800 px-4 py-2.5 text-sm text-white placeholder-slate-500 transition-colors focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400';
  const inputErrorClasses =
    'rounded-lg border border-red-500 bg-slate-800 px-4 py-2.5 text-sm text-white placeholder-slate-500 transition-colors focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400';

  return (
    <div className="flex min-h-screen bg-[#0a0a0a]">
      <div className="hidden lg:flex lg:w-1/2 flex-col items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#0a0a0a] via-slate-900 to-[#0a0a0a]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(245,158,11,0.08)_0%,_transparent_70%)]" />

        <div className="relative z-10 text-center px-12 animate-[fadeIn_0.8s_ease-out]">
          <div className="text-6xl mb-6 opacity-80">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-20 h-20 mx-auto text-amber-400/70">
              <circle cx="6" cy="6" r="3" />
              <circle cx="6" cy="18" r="3" />
              <line x1="20" y1="4" x2="8.12" y2="15.88" />
              <line x1="14.47" y1="14.48" x2="20" y2="20" />
              <line x1="8.12" y1="8.12" x2="12" y2="12" />
            </svg>
          </div>

          <h1 className="text-5xl font-bold text-white tracking-tight mb-3">
            Barber<span className="text-amber-400">Pro</span>
          </h1>

          <div className="w-16 h-0.5 bg-amber-400/50 mx-auto mb-6" />

          <p className="text-xl text-slate-400 font-light italic">
            Bootstrap de acesso administrativo
          </p>

          <div className="mt-12 flex items-center justify-center gap-3 text-slate-600">
            <div className="w-12 h-px bg-slate-700" />
            <span className="text-xs uppercase tracking-[0.25em]">Hidden Route</span>
            <div className="w-12 h-px bg-slate-700" />
          </div>
        </div>
      </div>

      <div className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="w-full max-w-md animate-[slideUp_0.6s_ease-out]">
          <div className="lg:hidden text-center mb-10">
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Barber<span className="text-amber-400">Pro</span>
            </h1>
            <p className="text-sm text-slate-500 mt-1 italic">Bootstrap de acesso administrativo</p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl shadow-black/40 backdrop-blur-sm">
            <div className="mb-8">
              <h2 className="text-2xl font-semibold text-white">Criar administrador</h2>
              <p className="text-sm text-slate-500 mt-1">
                Pagina reservada para criar o primeiro administrador do sistema.
              </p>
            </div>

            <div className="mb-6 rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">
              Usa esta pagina apenas no arranque inicial. Depois de existir um admin, o bootstrap deixa de estar disponivel.
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="flex flex-col gap-1.5">
                <label htmlFor="admin-username" className="text-sm font-medium text-slate-300">
                  Nome de utilizador
                </label>
                <input
                  id="admin-username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoFocus
                  placeholder="Ex: admin"
                  className={errors.username ? inputErrorClasses : inputClasses}
                />
                {errors.username && <span className="text-xs text-red-400">{errors.username}</span>}
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="admin-email" className="text-sm font-medium text-slate-300">
                  Email
                </label>
                <input
                  id="admin-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="admin@exemplo.com"
                  className={errors.email ? inputErrorClasses : inputClasses}
                />
                {errors.email && <span className="text-xs text-red-400">{errors.email}</span>}
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="admin-password" className="text-sm font-medium text-slate-300">
                  Password
                </label>
                <input
                  id="admin-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="Minimo 8 caracteres"
                  className={errors.password ? inputErrorClasses : inputClasses}
                />
                {errors.password && <span className="text-xs text-red-400">{errors.password}</span>}
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="admin-confirm" className="text-sm font-medium text-slate-300">
                  Confirmar password
                </label>
                <input
                  id="admin-confirm"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  placeholder="Repete a password"
                  className={errors.confirmPassword ? inputErrorClasses : inputClasses}
                />
                {errors.confirmPassword && <span className="text-xs text-red-400">{errors.confirmPassword}</span>}
              </div>

              <label className="flex items-start gap-3 rounded-xl border border-slate-700 bg-slate-800/70 p-4 text-sm text-slate-300">
                <input
                  type="checkbox"
                  checked={confirmBootstrap}
                  onChange={(e) => setConfirmBootstrap(e.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border-slate-600 bg-slate-900 text-amber-400 focus:ring-amber-400"
                />
                <span>
                  Confirmo que quero criar o primeiro administrador desta instalacao.
                  {errors.confirmBootstrap && (
                    <span className="mt-2 block text-xs text-red-400">{errors.confirmBootstrap}</span>
                  )}
                </span>
              </label>

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-amber-500 px-4 py-2.5 text-sm font-bold text-slate-900 transition-colors hover:bg-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {loading ? 'A criar administrador...' : 'Criar administrador'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <Link
                to="/login"
                className="text-sm text-slate-400 transition-colors hover:text-amber-400"
              >
                Voltar ao login
              </Link>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
