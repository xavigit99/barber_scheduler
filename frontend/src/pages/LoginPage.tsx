import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../components/Toast';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const user = await login(username, password);
      const dest = user.role === 'admin' ? '/admin' : user.role === 'barber' ? '/barber' : '/client';
      navigate(dest, { replace: true });
    } catch {
      toast('Credenciais invalidas', 'error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen bg-[#0a0a0a]">
      {/* Left branding panel — desktop only */}
      <div className="hidden lg:flex lg:w-1/2 flex-col items-center justify-center relative overflow-hidden">
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#0a0a0a] via-slate-900 to-[#0a0a0a]" />
        {/* Subtle radial glow */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(245,158,11,0.08)_0%,_transparent_70%)]" />

        <div className="relative z-10 text-center px-12 animate-[fadeIn_0.8s_ease-out]">
          {/* Scissors icon */}
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
            O teu corte, no teu tempo
          </p>

          {/* Decorative line details */}
          <div className="mt-12 flex items-center justify-center gap-3 text-slate-600">
            <div className="w-12 h-px bg-slate-700" />
            <span className="text-xs uppercase tracking-[0.25em]">Est. 2024</span>
            <div className="w-12 h-px bg-slate-700" />
          </div>
        </div>
      </div>

      {/* Right form panel */}
      <div className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="w-full max-w-md animate-[slideUp_0.6s_ease-out]">
          {/* Mobile branding */}
          <div className="lg:hidden text-center mb-10">
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Barber<span className="text-amber-400">Pro</span>
            </h1>
            <p className="text-sm text-slate-500 mt-1 italic">O teu corte, no teu tempo</p>
          </div>

          {/* Form card */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl shadow-black/40 backdrop-blur-sm">
            <div className="mb-8">
              <h2 className="text-2xl font-semibold text-white">Bem-vindo de volta</h2>
              <p className="text-sm text-slate-500 mt-1">Introduz os teus dados para continuar</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="flex flex-col gap-1.5">
                <label htmlFor="username" className="text-sm font-medium text-slate-300">
                  Utilizador
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoFocus
                  placeholder="O teu nome de utilizador"
                  className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-2.5 text-sm text-white placeholder-slate-500 transition-colors focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="password" className="text-sm font-medium text-slate-300">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="A tua password"
                  className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-2.5 text-sm text-white placeholder-slate-500 transition-colors focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-amber-500 px-4 py-2.5 text-sm font-bold text-slate-900 transition-colors hover:bg-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {loading ? 'A entrar...' : 'Entrar'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <Link
                to="/register"
                className="text-sm text-slate-400 transition-colors hover:text-amber-400"
              >
                Nao tens conta?{' '}
                <span className="font-medium text-amber-400 hover:text-amber-300">
                  Cria uma aqui &rarr;
                </span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Global keyframe styles */}
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
