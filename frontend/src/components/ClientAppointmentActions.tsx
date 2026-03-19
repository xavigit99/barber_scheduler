import Button from './Button';
import type { Appointment } from '../types';

interface ClientAppointmentActionsProps {
  appointment: Appointment;
  isPast: boolean;
  isReviewed: boolean;
  barberName: string;
  onReview: (appointmentId: string, barberName: string) => void;
  onReschedule: (appointment: Appointment) => void;
  onCancel: (appointmentId: string) => void;
}

export default function ClientAppointmentActions({
  appointment,
  isPast,
  isReviewed,
  barberName,
  onReview,
  onReschedule,
  onCancel,
}: ClientAppointmentActionsProps) {
  if (isPast) {
    if (isReviewed) {
      return <span className="text-xs font-medium text-emerald-600">Avaliado ✓</span>;
    }

    return (
      <Button
        size="sm"
        variant="secondary"
        onClick={() => onReview(appointment.id, barberName)}
      >
        Avaliar
      </Button>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      <Button size="sm" variant="secondary" onClick={() => onReschedule(appointment)}>
        Remarcar
      </Button>
      <Button size="sm" variant="danger" onClick={() => onCancel(appointment.id)}>
        Cancelar
      </Button>
    </div>
  );
}
