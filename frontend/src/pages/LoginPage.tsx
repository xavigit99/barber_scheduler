import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Input from '../components/Input';
import Button from '../components/Button';
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
    <div className="flex min-h-screen items-center justify-center bg-slate-900">
      <div className="w-full max-w-sm rounded-xl bg-white p-8 shadow-xl">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500 text-white font-bold text-xl">
            B
          </div>
          <h1 className="text-xl font-semibold text-slate-800">BarberPro</h1>
          <p className="text-sm text-slate-500 mt-1">Acesso ao sistema</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Utilizador"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoFocus
          />
          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? 'A entrar...' : 'Entrar'}
          </Button>
        </form>
      </div>
    </div>
  );
}
