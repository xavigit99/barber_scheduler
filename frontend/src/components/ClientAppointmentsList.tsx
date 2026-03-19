import ClientAppointmentActions from './ClientAppointmentActions';
import type { Appointment } from '../types';

interface ClientAppointmentsListProps {
  appointments: Appointment[];
  emptyMessage: string;
  isPast: (appointment: Appointment) => boolean;
  barbers: Record<string, string>;
  services: Record<string, string>;
  reviewed: Set<string>;
  onReview: (appointmentId: string, barberName: string) => void;
  onReschedule: (appointment: Appointment) => void;
  onCancel: (appointmentId: string) => void;
}

export default function ClientAppointmentsList({
  appointments,
  emptyMessage,
  isPast,
  barbers,
  services,
  reviewed,
  onReview,
  onReschedule,
  onCancel,
}: ClientAppointmentsListProps) {
  if (appointments.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-500 shadow-sm">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {appointments.map((appointment) => {
        const barberName = barbers[String(appointment.barber_id)] ?? `#${appointment.barber_id}`;
        const serviceName = services[String(appointment.service_id)] ?? `#${appointment.service_id}`;
        const appointmentIsPast = isPast(appointment);

        return (
          <div
            key={appointment.id}
            className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div className="space-y-3">
                <div>
                  <p className="text-lg font-semibold text-slate-900">
                    {new Date(appointment.start_at).toLocaleDateString('pt-PT', {
                      weekday: 'long',
                      day: '2-digit',
                      month: 'long',
                    })}
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    {new Date(appointment.start_at).toLocaleTimeString('pt-PT', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                    {' - '}
                    {new Date(appointment.end_at).toLocaleTimeString('pt-PT', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Serviço</p>
                    <p className="mt-1 text-sm text-slate-700">{serviceName}</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Barbeiro</p>
                    <p className="mt-1 text-sm text-slate-700">{barberName}</p>
                  </div>
                </div>
              </div>

              <ClientAppointmentActions
                appointment={appointment}
                isPast={appointmentIsPast}
                isReviewed={reviewed.has(appointment.id)}
                barberName={barberName}
                onReview={onReview}
                onReschedule={onReschedule}
                onCancel={onCancel}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
