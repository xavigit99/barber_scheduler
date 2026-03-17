import { useState, type FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../components/Toast';

export default function ClientLoginPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
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
      await login(username, password);
      navigate('/client', { replace: true });
    } catch {
      toast('Credenciais inválidas', 'error');
    } finally {
      setLoading(false);
    }
  }

  const inputClasses =
    'w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-4 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-amber-500 transition-colors';

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

        <h1 className="text-2xl font-bold text-white mb-1">Bem-vindo de volta</h1>
        <p className="text-sm text-slate-400 mb-8">Entra para gerir os teus agendamentos.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-sm text-slate-400">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
              required
              placeholder="O teu username"
              className={inputClasses}
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-sm text-slate-400">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="A tua password"
              className={inputClasses}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-amber-500 py-4 text-slate-900 font-bold text-sm hover:bg-amber-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {loading ? 'A entrar...' : 'Entrar'}
          </button>
        </form>

        <div className="mt-6 text-center space-y-3">
          <p className="text-sm text-slate-400">
            Não tens conta?{' '}
            <Link to={`/join/${tenantId}`} className="text-amber-400 font-medium hover:text-amber-300">
              Criar conta
            </Link>
          </p>
          <p className="text-sm text-slate-400">
            Preferes marcar sem conta?{' '}
            <Link to={`/book/${tenantId}`} className="text-amber-400 font-medium hover:text-amber-300">
              Marcar agora
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
