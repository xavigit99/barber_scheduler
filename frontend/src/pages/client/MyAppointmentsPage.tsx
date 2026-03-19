import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api, { getApiError } from '../../lib/api';
import ClientAppointmentsList from '../../components/ClientAppointmentsList';
import DateAvailabilityCalendar from '../../components/DateAvailabilityCalendar';
import Button from '../../components/Button';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../contexts/AuthContext';
import { formatDayLabel, monthBounds, monthKeyFromDate, toDateKey } from '../../lib/dateCalendar';
import type { Appointment, Barber, Feedback, Service, AvailableSlot } from '../../types';

/* ── Star picker ─────────────────────────────────────────────────── */
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

/* ── Review modal ────────────────────────────────────────────────── */
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
    } catch (err) {
      toast(getApiError(err, 'Erro ao enviar avaliação'), 'error');
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
          <Button variant="secondary" onClick={onClose} disabled={submitting}>Cancelar</Button>
          <Button onClick={handleSubmit} disabled={submitting}>
            {submitting ? 'A enviar...' : 'Enviar Avaliação'}
          </Button>
        </div>
      </div>
    </div>
  );
}

/* ── Reschedule modal ─────────────────────────────────────────────── */
interface RescheduleModalProps {
  appointment: Appointment;
  onClose: () => void;
  onDone: () => void;
}

function RescheduleModal({ appointment, onClose, onDone }: RescheduleModalProps) {
  const { toast } = useToast();
  const [targetDate, setTargetDate] = useState('');
  const [calendarMonth, setCalendarMonth] = useState(() => monthKeyFromDate(new Date()));
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [slots, setSlots] = useState<AvailableSlot[]>([]);
  const [loadingAvailableDates, setLoadingAvailableDates] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<AvailableSlot | null>(null);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const { startDate, endDate } = monthBounds(calendarMonth);

    setLoadingAvailableDates(true);
    api
      .get(
        `/barbers/${appointment.barber_id}/availability/dates?service_id=${appointment.service_id}&start_date=${startDate}&end_date=${endDate}&timezone=Europe/Lisbon`,
      )
      .then((res) => {
        const data = Array.isArray(res.data?.dates) ? res.data.dates : [];
        setAvailableDates(data);
        if (targetDate && !data.includes(targetDate)) {
          setTargetDate('');
          setSelectedSlot(null);
        }
      })
      .catch((err) => {
        toast(getApiError(err, 'Erro ao carregar dias disponiveis'), 'error');
        setAvailableDates([]);
      })
      .finally(() => setLoadingAvailableDates(false));
  }, [appointment.barber_id, appointment.service_id, calendarMonth, targetDate]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!targetDate) { setSlots([]); return; }
    setLoadingSlots(true);
    setSelectedSlot(null);
    api
      .get(`/barbers/${appointment.barber_id}/availability/slots?service_id=${appointment.service_id}&target_date=${targetDate}&timezone=Europe/Lisbon`)
      .then((res) => {
        const data = res.data?.slots ?? res.data;
        setSlots(Array.isArray(data) ? data : []);
      })
      .catch((err) => { toast(getApiError(err, 'Erro ao carregar horários'), 'error'); setSlots([]); })
      .finally(() => setLoadingSlots(false));
  }, [targetDate]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleSubmit() {
    if (!selectedSlot) return;
    setSubmitting(true);
    try {
      await api.patch(`/appointments/${appointment.id}`, { nova_data_inicio: selectedSlot.inicio });
      toast('Agendamento remarcado!', 'success');
      onDone();
    } catch (err) {
      toast(getApiError(err, 'Erro ao remarcar agendamento'), 'error');
    } finally {
      setSubmitting(false);
    }
  }

  const handleEsc = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape' && !submitting) onClose();
  }, [onClose, submitting]);

  useEffect(() => {
    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [handleEsc]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl space-y-4">
        <h2 className="text-lg font-semibold text-slate-800">Remarcar Agendamento</h2>
        <DateAvailabilityCalendar
          month={calendarMonth}
          onMonthChange={setCalendarMonth}
          selectedDate={targetDate}
          onSelectDate={(date) => {
            setTargetDate(date);
            setSelectedSlot(null);
          }}
          highlightedDates={availableDates}
          loading={loadingAvailableDates}
          minDate={new Date().toISOString().split('T')[0]}
          tone="available"
          helperText="Os dias a verde ja tem horarios livres para remarcar."
          emptyText="Nao ha dias livres neste mes para este servico."
        />
        {targetDate && (
          <p className="text-sm text-slate-600">
            Nova data: <span className="font-medium">{formatDayLabel(new Date(`${targetDate}T00:00:00`))}</span>
          </p>
        )}
        {targetDate && (
          loadingSlots ? (
            <Spinner />
          ) : slots.length === 0 ? (
            <p className="text-sm text-slate-500">Nenhum horário disponível.</p>
          ) : (
            <div className="grid grid-cols-3 gap-2">
              {slots.map((slot) => {
                const time = new Date(slot.inicio).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' });
                const isSelected = selectedSlot?.inicio === slot.inicio;
                return (
                  <button
                    key={slot.inicio}
                    onClick={() => setSelectedSlot(slot)}
                    className={`rounded-lg border px-3 py-2 text-sm transition-colors cursor-pointer ${
                      isSelected
                        ? 'border-emerald-500 bg-emerald-50 text-emerald-700 font-medium'
                        : 'border-slate-200 bg-white text-slate-700 hover:border-emerald-300'
                    }`}
                  >
                    {time}
                  </button>
                );
              })}
            </div>
          )
        )}
        <div className="flex gap-2 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={submitting}>Cancelar</Button>
          <Button onClick={handleSubmit} disabled={!selectedSlot || submitting}>
            {submitting ? 'A remarcar...' : 'Confirmar'}
          </Button>
        </div>
      </div>
    </div>
  );
}

/* ── Main page ───────────────────────────────────────────────────── */
type Tab = 'date' | 'past';

export default function MyAppointmentsPage() {
  const { toast } = useToast();
  const { tenantId } = useAuth();
  const [tab, setTab] = useState<Tab>('date');
  const [allAppointments, setAllAppointments] = useState<Appointment[]>([]);
  const [barbers, setBarbers] = useState<Record<string, string>>({});
  const [services, setServices] = useState<Record<string, string>>({});
  const [reviewed, setReviewed] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [targetDate, setTargetDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [reviewTarget, setReviewTarget] = useState<{ id: string; barberName: string } | null>(null);
  const [rescheduleTarget, setRescheduleTarget] = useState<Appointment | null>(null);

  /* Load barber/service maps + already-reviewed set once */
  useEffect(() => {
    if (!tenantId) {
      setBarbers({});
      setServices({});
      setReviewed(new Set());
      setAllAppointments([]);
      return;
    }
    Promise.all([api.get('/barbers/'), api.get('/services/'), api.get('/feedback/me')])
      .then(([bRes, sRes, fRes]) => {
        const bMap: Record<string, string> = {};
        (Array.isArray(bRes.data) ? bRes.data : []).forEach((b: Barber) => { bMap[String(b.id)] = b.nome; });
        const sMap: Record<string, string> = {};
        (Array.isArray(sRes.data) ? sRes.data : []).forEach((s: Service) => { sMap[String(s.id)] = s.nome; });
        setBarbers(bMap);
        setServices(sMap);
        setReviewed(new Set(
          (Array.isArray(fRes.data) ? fRes.data : []).map((f: Feedback) => String(f.appointment_id))
        ));
      })
      .catch(() => {/* non-critical */});
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function loadAppointments() {
    setLoading(true);
    try {
      const res = await api.get('/appointments/clients/me/appointments');
      const data: Appointment[] = Array.isArray(res.data) ? res.data : [];
      data.sort((a, b) => new Date(a.start_at).getTime() - new Date(b.start_at).getTime());
      setAllAppointments(data);
    } catch (err) {
      toast(getApiError(err, 'Erro ao carregar agendamentos'), 'error');
      setAllAppointments([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!tenantId) {
      setAllAppointments([]);
      setLoading(false);
      return;
    }
    loadAppointments();
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleCancel(id: string) {
    if (!confirm('Cancelar este agendamento?')) return;
    try {
      await api.delete(`/appointments/${id}`);
      toast('Agendamento cancelado', 'success');
      setAllAppointments((prev) => prev.filter((a) => String(a.id) !== String(id)));
    } catch (err) {
      toast(getApiError(err, 'Erro ao cancelar agendamento'), 'error');
    }
  }

  function isPast(a: Appointment) {
    return new Date(a.end_at) < new Date();
  }

  const upcomingAppointments = allAppointments
    .filter((appointment) => !isPast(appointment))
    .sort((a, b) => new Date(a.start_at).getTime() - new Date(b.start_at).getTime());
  const upcomingDateOptions = Array.from(new Set(upcomingAppointments.map((appointment) => toDateKey(appointment.start_at))));
  const todayKey = toDateKey(new Date());
  const selectedDate = upcomingDateOptions.includes(targetDate)
    ? targetDate
    : (upcomingDateOptions.find((date) => date >= todayKey) ?? upcomingDateOptions[0] ?? targetDate);
  const nextAppointment = upcomingAppointments[0] ?? null;
  const appointments = tab === 'past'
    ? allAppointments
        .filter((appointment) => isPast(appointment))
        .sort((a, b) => new Date(b.start_at).getTime() - new Date(a.start_at).getTime())
    : allAppointments.filter((appointment) => toDateKey(appointment.start_at) === selectedDate);

  useEffect(() => {
    if (tab !== 'date') return;
    if (selectedDate !== targetDate) {
      setTargetDate(selectedDate);
    }
  }, [selectedDate, targetDate, tab]);

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Meus Agendamentos</h1>

      {/* Tabs */}
      <div className="mb-4 flex gap-1 border-b border-slate-200">
        {([['date', 'Por Data'], ['past', 'Passados (Avaliar)']] as [Tab, string][]).map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors cursor-pointer ${
              tab === key
                ? 'border-emerald-500 text-emerald-700'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Date filter (only in date tab) */}
      {tab === 'date' && (
        <div className="mb-4 grid gap-4 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)]">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-700">Próximo agendamento</p>
            {nextAppointment ? (
              <>
                <p className="mt-3 text-2xl font-semibold text-slate-900">
                  {new Date(nextAppointment.start_at).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })}
                </p>
                <p className="mt-1 text-sm font-medium text-slate-700">
                  {formatDayLabel(new Date(nextAppointment.start_at))}
                </p>
                <p className="mt-4 text-sm text-slate-600">
                  {services[String(nextAppointment.service_id)] ?? `#${nextAppointment.service_id}`}
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  com {barbers[String(nextAppointment.barber_id)] ?? `#${nextAppointment.barber_id}`}
                </p>
              </>
            ) : (
              <>
                <p className="mt-3 text-xl font-semibold text-slate-900">Sem agendamentos futuros</p>
                <p className="mt-2 text-sm text-slate-500">
                  Quando tiveres uma nova marcação, ela aparece aqui logo em destaque.
                </p>
              </>
            )}
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-amber-700">Dias Marcados</p>
            <p className="mt-2 text-sm text-slate-500">
              Escolhe um dia para veres logo as marcacoes dessa data.
            </p>
            <div className="mt-4">
              {selectedDate && upcomingDateOptions.length > 0 && (
                <p className="mt-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
                  A mostrar o dia: <span className="font-semibold">{formatDayLabel(new Date(`${selectedDate}T00:00:00`))}</span>
                </p>
              )}
              {upcomingDateOptions.length === 0 ? (
                <p className="mt-3 text-sm text-slate-500">Nao tens agendamentos futuros nesta barbearia.</p>
              ) : (
                <div className="mt-3 flex flex-wrap gap-2">
                  {upcomingDateOptions.map((date) => {
                    const isSelected = date === selectedDate;
                    return (
                      <button
                        key={date}
                        type="button"
                        onClick={() => setTargetDate(date)}
                        className={`rounded-full border px-3 py-2 text-sm font-medium transition-colors ${
                          isSelected
                            ? 'border-amber-500 bg-amber-500 text-white'
                            : 'border-amber-200 bg-amber-50 text-amber-700 hover:border-amber-300'
                        }`}
                      >
                        {formatDayLabel(new Date(`${date}T00:00:00`))}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {tab === 'past' && (
        <p className="mb-4 text-sm text-slate-500">
          Agendamentos concluídos — clica em <strong>Avaliar</strong> para deixar a tua avaliação.
        </p>
      )}

      {!tenantId ? (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-8 text-center">
          <p className="text-slate-500">
            Escolhe primeiro a barbearia onde queres consultar os teus agendamentos.
            {' '}
            <Link to="/barbershops" className="font-medium underline">
              Ver barbearias
            </Link>
          </p>
        </div>
      ) : loading ? (
        <Spinner />
      ) : (
        <ClientAppointmentsList
          appointments={appointments}
          isPast={isPast}
          barbers={barbers}
          services={services}
          reviewed={reviewed}
          onReview={(appointmentId, barberName) => setReviewTarget({ id: appointmentId, barberName })}
          onReschedule={(appointment) => setRescheduleTarget(appointment)}
          onCancel={handleCancel}
          emptyMessage={tab === 'past' ? 'Nenhum agendamento passado.' : 'Nenhum agendamento para esta data.'}
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

      {rescheduleTarget && (
        <RescheduleModal
          appointment={rescheduleTarget}
          onClose={() => setRescheduleTarget(null)}
          onDone={() => {
            setRescheduleTarget(null);
            loadAppointments();
          }}
        />
      )}
    </div>
  );
}
