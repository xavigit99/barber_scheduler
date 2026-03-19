import { useState, useEffect } from 'react';
import api, { getApiError } from '../../lib/api';
import Button from '../../components/Button';
import ClientEmptyState from '../../components/ClientEmptyState';
import ClientPageHeader from '../../components/ClientPageHeader';
import DateAvailabilityCalendar from '../../components/DateAvailabilityCalendar';
import Select from '../../components/Select';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../contexts/AuthContext';
import { formatDayLabel, monthBounds, monthKeyFromDate } from '../../lib/dateCalendar';
import type { Barber, Service, AvailableSlot } from '../../types';

export default function BookPage() {
  const { toast } = useToast();
  const { clientId, tenantId } = useAuth();

  const [barbers, setBarbers] = useState<Barber[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [slots, setSlots] = useState<AvailableSlot[]>([]);
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [loadingAvailableDates, setLoadingAvailableDates] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  const [selectedBarber, setSelectedBarber] = useState('');
  const [selectedService, setSelectedService] = useState('');
  const [targetDate, setTargetDate] = useState('');
  const [calendarMonth, setCalendarMonth] = useState(() => monthKeyFromDate(new Date()));
  const [selectedSlot, setSelectedSlot] = useState<AvailableSlot | null>(null);

  useEffect(() => {
    if (!tenantId) {
      setLoading(false);
      return;
    }

    async function load() {
      setLoading(true);
      try {
        const [bRes, sRes] = await Promise.all([
          api.get('/barbers/'),
          api.get('/services/'),
        ]);
        setBarbers(Array.isArray(bRes.data) ? bRes.data : []);
        setServices(Array.isArray(sRes.data) ? sRes.data : []);
      } catch (err) {
        toast(getApiError(err, 'Erro ao carregar dados'), 'error');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!selectedBarber || !selectedService) {
      setAvailableDates([]);
      return;
    }

    const { startDate, endDate } = monthBounds(calendarMonth);
    setLoadingAvailableDates(true);
    api
      .get(
        `/barbers/${selectedBarber}/availability/dates?service_id=${selectedService}&start_date=${startDate}&end_date=${endDate}&timezone=Europe/Lisbon`,
      )
      .then((res) => {
        const data = Array.isArray(res.data?.dates) ? res.data.dates : [];
        setAvailableDates(data);
        if (targetDate && !data.includes(targetDate)) {
          setTargetDate('');
          setSelectedSlot(null);
          setSlots([]);
        }
      })
      .catch((err) => {
        toast(getApiError(err, 'Erro ao carregar dias disponiveis'), 'error');
        setAvailableDates([]);
      })
      .finally(() => setLoadingAvailableDates(false));
  }, [selectedBarber, selectedService, calendarMonth, targetDate]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!selectedBarber || !selectedService || !targetDate) {
      setSlots([]);
      return;
    }

    setLoadingSlots(true);
    api
      .get(
        `/barbers/${selectedBarber}/availability/slots?service_id=${selectedService}&target_date=${targetDate}&timezone=Europe/Lisbon`,
      )
      .then((res) => {
        const data = res.data?.slots ?? res.data;
        setSlots(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        toast(getApiError(err, 'Erro ao carregar horarios'), 'error');
        setSlots([]);
      })
      .finally(() => setLoadingSlots(false));
  }, [selectedBarber, selectedService, targetDate]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleConfirm() {
    if (!selectedSlot || !clientId) return;
    setSubmitting(true);
    try {
      await api.post('/appointments/', {
        barber_id: Number(selectedBarber),
        client_id: clientId,
        service_id: Number(selectedService),
        data_inicio: selectedSlot.inicio,
      });
      toast('Agendamento confirmado!', 'success');
      setSelectedBarber('');
      setSelectedService('');
      setTargetDate('');
      setAvailableDates([]);
      setCalendarMonth(monthKeyFromDate(new Date()));
      setSelectedSlot(null);
      setSlots([]);
    } catch (err) {
      toast(getApiError(err, 'Erro ao criar agendamento'), 'error');
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <Spinner />;

  if (!tenantId) {
    return (
      <ClientEmptyState
        message="Escolhe primeiro a barbearia onde queres marcar."
        linkTo="/barbershops"
        linkLabel="Ver barbearias"
      />
    );
  }

  if (!clientId) {
    return (
      <ClientEmptyState
        message="Ainda nao tens historico numa barbearia selecionada. Faz a tua primeira marcacao pela pagina publica da barbearia e a tua ficha passa a ficar associada a essa experiencia."
        linkTo="/barbershops"
        linkLabel="Ver barbearias"
      />
    );
  }

  const barberName = barbers.find((b) => String(b.id) === selectedBarber)?.nome ?? 'Por escolher';
  const serviceObj = services.find((s) => String(s.id) === selectedService);
  const canShowCalendar = Boolean(selectedBarber && selectedService);
  const canConfirm = Boolean(selectedBarber && selectedService && targetDate && selectedSlot);

  return (
    <div className="mx-auto max-w-5xl">
      <ClientPageHeader
        title="Agendar"
        description="Escolhe barbeiro, serviço, dia e horário no mesmo ecrã."
      />

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.6fr)_minmax(320px,0.9fr)]">
        <div className="space-y-4">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="grid gap-4 md:grid-cols-2">
              <Select
                label="Barbeiro"
                options={barbers.map((b) => ({ value: String(b.id), label: b.nome }))}
                value={selectedBarber}
                onChange={(e) => {
                  setSelectedBarber(e.target.value);
                  setTargetDate('');
                  setSelectedSlot(null);
                  setSlots([]);
                  setAvailableDates([]);
                  setCalendarMonth(monthKeyFromDate(new Date()));
                }}
                placeholder="Selecione..."
              />
              <Select
                label="Serviço"
                options={services.map((s) => ({
                  value: String(s.id),
                  label: `${s.nome} — ${s.duracao_minutos}min — ${new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' }).format(s.preco)}`,
                }))}
                value={selectedService}
                onChange={(e) => {
                  setSelectedService(e.target.value);
                  setTargetDate('');
                  setSelectedSlot(null);
                  setSlots([]);
                  setAvailableDates([]);
                  setCalendarMonth(monthKeyFromDate(new Date()));
                }}
                placeholder="Selecione..."
              />
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            {!canShowCalendar ? (
              <p className="text-sm text-slate-500">
                Escolhe primeiro o barbeiro e o serviço para veres os dias disponíveis.
              </p>
            ) : (
              <div className="space-y-4">
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
                  helperText="Os dias a verde já têm horários livres."
                  emptyText="Nao existem dias livres neste mes para esta combinacao."
                />
                {targetDate && (
                  <p className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
                    Dia escolhido: <span className="font-semibold">{formatDayLabel(new Date(`${targetDate}T00:00:00`))}</span>
                  </p>
                )}
              </div>
            )}
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm font-semibold text-slate-800">Horários</p>
            {!targetDate ? (
              <p className="mt-2 text-sm text-slate-500">
                Escolhe um dia para veres os horários disponíveis.
              </p>
            ) : loadingSlots ? (
              <div className="mt-3">
                <Spinner />
              </div>
            ) : slots.length === 0 ? (
              <p className="mt-2 text-sm text-slate-500">Nenhum horario disponivel para esta data.</p>
            ) : (
              <div className="mt-3 grid grid-cols-3 gap-2 sm:grid-cols-4">
                {slots.map((slot) => {
                  const time = new Date(slot.inicio).toLocaleTimeString('pt-PT', {
                    hour: '2-digit',
                    minute: '2-digit',
                  });
                  const isSelected = selectedSlot?.inicio === slot.inicio;
                  return (
                    <button
                      key={slot.inicio}
                      type="button"
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
            )}
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">Resumo</p>
            <div className="mt-4 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Barbeiro</span>
                <span className="font-medium text-slate-800">{barberName}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Serviço</span>
                <span className="font-medium text-slate-800">{serviceObj?.nome ?? 'Por escolher'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Duração</span>
                <span className="font-medium text-slate-800">
                  {serviceObj ? `${serviceObj.duracao_minutos} min` : 'Por escolher'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Preço</span>
                <span className="font-medium text-slate-800">
                  {serviceObj
                    ? new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' }).format(serviceObj.preco)
                    : 'Por escolher'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Data</span>
                <span className="font-medium text-slate-800">
                  {targetDate ? formatDayLabel(new Date(`${targetDate}T00:00:00`)) : 'Por escolher'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Horário</span>
                <span className="font-medium text-slate-800">
                  {selectedSlot
                    ? `${new Date(selectedSlot.inicio).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })} - ${new Date(selectedSlot.fim).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })}`
                    : 'Por escolher'}
                </span>
              </div>
            </div>

            <Button
              onClick={handleConfirm}
              disabled={!canConfirm || submitting || !clientId}
              className="mt-5 w-full"
            >
              {submitting ? 'A agendar...' : 'Confirmar Agendamento'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
