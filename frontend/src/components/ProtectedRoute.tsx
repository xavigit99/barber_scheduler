import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Spinner from './Spinner';
import Navbar from './Navbar';
import type { Role } from '../types';

interface Props {
  allowedRoles?: Role[];
}

export default function ProtectedRoute({ allowedRoles }: Props) {
  const { user, loading } = useAuth();

  if (loading) return <Spinner />;

  if (!user) return <Navigate to="/login" replace />;

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    /* redirect to role-appropriate home */
    const home = user.role === 'admin' ? '/admin' : user.role === 'barber' ? '/barber' : '/client';
    return <Navigate to={home} replace />;
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Navbar />
      <main className="ml-60 flex-1 p-6">
        <Outlet />
      </main>
    </div>
  );
}
