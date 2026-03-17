import { useState, useEffect, useCallback } from 'react';
import api from '../../lib/api';
import Input from '../../components/Input';
import Table from '../../components/Table';
import Button from '../../components/Button';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import type { Appointment, Barber, Feedback, Service } from '../../types';

function StarPicker({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type="button"
          onClick={() => onChange(n)}
          className={`text-2xl transition-colors cursor-pointer ${n <= value ? 'text-amber-400' : 'text-slate-300 hover:text-amber-300'}`}
        >
          ★
        </button>
      ))}
    </div>
  );
}

interface ReviewModalProps {
  appointmentId: string;
  barberName: string;
  onClose: () => void;
  onDone: (appointmentId: string) => void;
}

function ReviewModal({ appointmentId, barberName, onClose, onDone }: ReviewModalProps) {
  const { toast } = useToast();
  const [rating, setRating] = useState(5);
  const [comentario, setComentario] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleEsc = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape' && !submitting) onClose();
  }, [onClose, submitting]);

  useEffect(() => {
    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [handleEsc]);

  async function handleSubmit() {
    setSubmitting(true);
    try {
      await api.post('/feedback', { appointment_id: Number(appointmentId), rating, comentario: comentario || null });
      toast('Avaliação enviada!', 'success');
      onDone(appointmentId);
    } catch {
      toast('Erro ao enviar avaliação', 'error');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl space-y-4">
        <h2 className="text-lg font-semibold text-slate-800">Avaliar — {barberName}</h2>
        <div>
          <label className="block text-sm text-slate-500 mb-2">Classificação</label>
          <StarPicker value={rating} onChange={setRating} />
        </div>
        <div>
          <label className="block text-sm text-slate-500 mb-1">Comentário (opcional)</label>
          <textarea
            value={comentario}
            onChange={(e) => setComentario(e.target.value)}
            maxLength={2000}
            rows={3}
            placeholder="O que achaste do serviço?"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:border-emerald-500 resize-none"
          />
          <p className="text-xs text-slate-400 text-right">{comentario.length}/2000</p>
        </div>
        <div className="flex gap-2 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={submitting}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit} disabled={submitting}>
            {submitting ? 'A enviar...' : 'Enviar Avaliação'}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default function MyAppointmentsPage() {
  const { toast } = useToast();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [barbers, setBarbers] = useState<Record<string, string>>({});
  const [services, setServices] = useState<Record<string, string>>({});
  const [reviewed, setReviewed] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [targetDate, setTargetDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [reviewTarget, setReviewTarget] = useState<{ id: string; barberName: string } | null>(null);

  /* Load barber/service name maps + already-reviewed appointments once */
  useEffect(() => {
    Promise.all([api.get('/barbers/'), api.get('/services/'), api.get('/feedback/me')])
      .then(([bRes, sRes, fRes]) => {
        const bMap: Record<string, string> = {};
        (Array.isArray(bRes.data) ? bRes.data : []).forEach((b: Barber) => {
          bMap[String(b.id)] = b.nome;
        });
        const sMap: Record<string, string> = {};
        (Array.isArray(sRes.data) ? sRes.data : []).forEach((s: Service) => {
          sMap[String(s.id)] = s.nome;
        });
        setBarbers(bMap);
        setServices(sMap);
        const ids = new Set<string>(
          (Array.isArray(fRes.data) ? fRes.data : []).map((f: Feedback) => String(f.appointment_id))
        );
        setReviewed(ids);
      })
      .catch(() => {/* non-critical */});
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function load(date: string) {
    setLoading(true);
    try {
      const res = await api.get(`/appointments/clients/me/appointments?target_date=${date}`);
      setAppointments(Array.isArray(res.data) ? res.data : []);
    } catch {
      toast('Erro ao carregar agendamentos', 'error');
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(targetDate);
  }, [targetDate]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleCancel(id: string) {
    if (!confirm('Cancelar este agendamento?')) return;
    try {
      await api.delete(`/appointments/${id}`);
      toast('Agendamento cancelado', 'success');
      setAppointments((prev) => prev.filter((a) => a.id !== id));
    } catch {
      toast('Erro ao cancelar agendamento', 'error');
    }
  }

  function isPast(appointment: Appointment) {
    return new Date(appointment.end_at) < new Date();
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Meus Agendamentos</h1>

      <div className="mb-4">
        <Input
          label="Data"
          type="date"
          value={targetDate}
          onChange={(e) => setTargetDate(e.target.value)}
        />
      </div>

      {loading ? (
        <Spinner />
      ) : (
        <Table
          columns={[
            {
              key: 'date',
              header: 'Data',
              render: (a) => new Date(a.start_at).toLocaleDateString('pt-PT'),
            },
            {
              key: 'start',
              header: 'Inicio',
              render: (a) =>
                new Date(a.start_at).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' }),
            },
            {
              key: 'end',
              header: 'Fim',
              render: (a) =>
                new Date(a.end_at).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' }),
            },
            {
              key: 'barber',
              header: 'Barbeiro',
              render: (a) => barbers[String(a.barber_id)] ?? `#${a.barber_id}`,
            },
            {
              key: 'service',
              header: 'Servico',
              render: (a) => services[String(a.service_id)] ?? `#${a.service_id}`,
            },
            {
              key: 'actions',
              header: '',
              render: (a) => (
                <div className="flex gap-2">
                  {isPast(a) ? (
                    reviewed.has(a.id) ? (
                      <span className="text-xs text-emerald-600 font-medium">Avaliado ✓</span>
                    ) : (
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() =>
                          setReviewTarget({ id: a.id, barberName: barbers[String(a.barber_id)] ?? `#${a.barber_id}` })
                        }
                      >
                        Avaliar
                      </Button>
                    )
                  ) : (
                    <Button size="sm" variant="danger" onClick={() => handleCancel(a.id)}>
                      Cancelar
                    </Button>
                  )}
                </div>
              ),
            },
          ]}
          data={appointments}
          keyExtractor={(a) => a.id}
          emptyMessage="Nenhum agendamento para esta data."
        />
      )}

      {reviewTarget && (
        <ReviewModal
          appointmentId={reviewTarget.id}
          barberName={reviewTarget.barberName}
          onClose={() => setReviewTarget(null)}
          onDone={(id) => {
            setReviewed((prev) => new Set([...prev, id]));
            setReviewTarget(null);
          }}
        />
      )}
    </div>
  );
}
