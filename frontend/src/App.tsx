import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ToastProvider } from './components/Toast';
import ProtectedRoute from './components/ProtectedRoute';
import Spinner from './components/Spinner';

/* Pages */
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/admin/DashboardPage';
import BarbershopsPage from './pages/admin/BarbershopsPage';
import BarbersPage from './pages/admin/BarbersPage';
import BarberAvailabilityPage from './pages/admin/BarberAvailabilityPage';
import ClientsPage from './pages/admin/ClientsPage';
import ServicesPage from './pages/admin/ServicesPage';
import AppointmentsPage from './pages/admin/AppointmentsPage';
import SchedulePage from './pages/barber/SchedulePage';
import BlocksPage from './pages/barber/BlocksPage';
import BookPage from './pages/client/BookPage';
import MyAppointmentsPage from './pages/client/MyAppointmentsPage';

/* Root redirect — sends user to role-appropriate home */
function RootRedirect() {
  const { user, loading } = useAuth();
  if (loading) return <Spinner />;
  if (!user) return <Navigate to="/login" replace />;
  const dest = user.role === 'admin' ? '/admin' : user.role === 'barber' ? '/barber' : '/client';
  return <Navigate to={dest} replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <Routes>
            {/* Public */}
            <Route path="/login" element={<LoginPage />} />

            {/* Root */}
            <Route path="/" element={<RootRedirect />} />

            {/* Admin routes */}
            <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
              <Route path="/admin" element={<DashboardPage />} />
              <Route path="/admin/barbershops" element={<BarbershopsPage />} />
              <Route path="/admin/barbers" element={<BarbersPage />} />
              <Route path="/admin/barbers/:id/availability" element={<BarberAvailabilityPage />} />
              <Route path="/admin/clients" element={<ClientsPage />} />
              <Route path="/admin/services" element={<ServicesPage />} />
              <Route path="/admin/appointments" element={<AppointmentsPage />} />
            </Route>

            {/* Barber routes */}
            <Route element={<ProtectedRoute allowedRoles={['barber']} />}>
              <Route path="/barber" element={<SchedulePage />} />
              <Route path="/barber/blocks" element={<BlocksPage />} />
            </Route>

            {/* Client routes */}
            <Route element={<ProtectedRoute allowedRoles={['client']} />}>
              <Route path="/client" element={<BookPage />} />
              <Route path="/client/appointments" element={<MyAppointmentsPage />} />
            </Route>

            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}
