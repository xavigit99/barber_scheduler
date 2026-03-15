import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface NavItem {
  to: string;
  label: string;
}

const adminLinks: NavItem[] = [
  { to: '/admin', label: 'Dashboard' },
  { to: '/admin/barbershops', label: 'Barbearias' },
  { to: '/admin/barbers', label: 'Barbeiros' },
  { to: '/admin/clients', label: 'Clientes' },
  { to: '/admin/services', label: 'Servicos' },
  { to: '/admin/appointments', label: 'Agendamentos' },
];

const barberLinks: NavItem[] = [
  { to: '/barber', label: 'Minha Agenda' },
  { to: '/barber/blocks', label: 'Bloqueios' },
];

const clientLinks: NavItem[] = [
  { to: '/client', label: 'Agendar' },
  { to: '/client/appointments', label: 'Meus Agendamentos' },
];

export default function Navbar() {
  const { user, logout, tenantId } = useAuth();
  const location = useLocation();

  if (!user) return null;

  const links =
    user.role === 'admin' ? adminLinks : user.role === 'barber' ? barberLinks : clientLinks;

  const isActive = (path: string) => location.pathname === path;

  return (
    <aside className="fixed left-0 top-0 flex h-screen w-60 flex-col bg-slate-900 text-slate-300">
      {/* brand */}
      <div className="flex items-center gap-2 px-5 py-5 border-b border-slate-800">
        <div className="h-8 w-8 rounded-full bg-emerald-500 flex items-center justify-center text-white font-bold text-sm">
          B
        </div>
        <span className="text-white font-semibold text-lg">BarberPro</span>
      </div>

      {/* tenant badge */}
      {tenantId && (
        <div className="px-5 py-2 text-xs text-slate-500 truncate border-b border-slate-800">
          Tenant: {tenantId.slice(0, 8)}...
        </div>
      )}

      {/* nav links */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`block rounded-lg px-3 py-2 text-sm transition-colors ${
              isActive(link.to)
                ? 'bg-emerald-600/20 text-emerald-400 font-medium'
                : 'hover:bg-slate-800 hover:text-white'
            }`}
          >
            {link.label}
          </Link>
        ))}
      </nav>

      {/* footer */}
      <div className="border-t border-slate-800 px-5 py-4">
        <div className="mb-2 text-xs text-slate-500 truncate">{user.username}</div>
        <button
          onClick={logout}
          className="w-full rounded-lg bg-slate-800 px-3 py-2 text-sm text-slate-400 hover:bg-slate-700 hover:text-white transition-colors cursor-pointer"
        >
          Sair
        </button>
      </div>
    </aside>
  );
}
