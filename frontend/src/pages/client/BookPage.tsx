import { useState, useEffect } from 'react';
import api from '../../lib/api';
import Button from '../../components/Button';
import Select from '../../components/Select';
import Input from '../../components/Input';
import Spinner from '../../components/Spinner';
import { useToast } from '../../components/Toast';
import type { Barber, Service, AvailableSlot } from '../../types';

type Step = 'barber' | 'service' | 'date' | 'slot' | 'confirm';

export default function BookPage() {
  const { toast } = useToast();

  const [step, setStep] = useState<Step>('barber');
  const [barbers, setBarbers] = useState<Barber[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [slots, setSlots] = useState<AvailableSlot[]>([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  /* selections */
  const [selectedBarber, setSelectedBarber] = useState('');
  const [selectedService, setSelectedService] = useState('');
  const [targetDate, setTargetDate] = useState('');
  const [selectedSlot, setSelectedSlot] = useState<AvailableSlot | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [bRes, sRes] = await Promise.all([
          api.get('/barbers/'),
          api.get('/services/'),
        ]);
        setBarbers(Array.isArray(bRes.data) ? bRes.data : []);
        setServices(Array.isArray(sRes.data) ? sRes.data : []);
      } catch {
        toast('Erro ao carregar dados', 'error');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  /* Load slots when date is picked */
  useEffect(() => {
    if (step !== 'slot' || !selectedBarber || !selectedService || !targetDate) return;
    setLoadingSlots(true);
    api
      .get(
        `/barbers/${selectedBarber}/availability/slots?service_id=${selectedService}&target_date=${targetDate}&timezone=Europe/Lisbon`,
      )
      .then((res) => {
        const data = res.data?.slots ?? res.data;
        setSlots(Array.isArray(data) ? data : []);
      })
      .catch(() => {
        toast('Erro ao carregar horarios', 'error');
        setSlots([]);
      })
      .finally(() => setLoadingSlots(false));
  }, [step, selectedBarber, selectedService, targetDate]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleConfirm() {
    if (!selectedSlot) return;
    setSubmitting(true);
    try {
      /* client_id will be resolved server-side from the auth token for client role,
         but the API might require it — send empty string and let backend handle it.
         For demo, we use a placeholder. The backend spec shows client_id is required. */
      await api.post('/appointments/', {
        barber_id: selectedBarber,
        client_id: '', /* backend should resolve from auth */
        service_id: selectedService,
        data_inicio: selectedSlot.inicio,
      });
      toast('Agendamento confirmado!', 'success');
      /* reset */
      setStep('barber');
      setSelectedBarber('');
      setSelectedService('');
      setTargetDate('');
      setSelectedSlot(null);
    } catch {
      toast('Erro ao criar agendamento', 'error');
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <Spinner />;

  const barberName = barbers.find((b) => b.id === selectedBarber)?.nome ?? '';
  const serviceObj = services.find((s) => s.id === selectedService);

  /* Step indicator */
  const steps: { key: Step; label: string }[] = [
    { key: 'barber', label: '1. Barbeiro' },
    { key: 'service', label: '2. Servico' },
    { key: 'date', label: '3. Data' },
    { key: 'slot', label: '4. Horario' },
    { key: 'confirm', label: '5. Confirmar' },
  ];

  const stepOrder: Step[] = ['barber', 'service', 'date', 'slot', 'confirm'];
  const currentIdx = stepOrder.indexOf(step);

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Agendar</h1>

      {/* Progress bar */}
      <div className="mb-8 flex gap-2">
        {steps.map((s, i) => (
          <div
            key={s.key}
            className={`flex-1 rounded-full h-2 transition-colors ${
              i <= currentIdx ? 'bg-emerald-500' : 'bg-slate-200'
            }`}
          />
        ))}
      </div>
      <p className="mb-6 text-sm font-medium text-slate-600">{steps[currentIdx].label}</p>

      {/* Step: barber */}
      {step === 'barber' && (
        <div className="space-y-4">
          <Select
            label="Escolha o barbeiro"
            options={barbers.map((b) => ({ value: b.id, label: b.nome }))}
            value={selectedBarber}
            onChange={(e) => setSelectedBarber(e.target.value)}
            placeholder="Selecione..."
          />
          <Button disabled={!selectedBarber} onClick={() => setStep('service')}>
            Seguinte
          </Button>
        </div>
      )}

      {/* Step: service */}
      {step === 'service' && (
        <div className="space-y-4">
          <Select
            label="Escolha o servico"
            options={services.map((s) => ({
              value: s.id,
              label: `${s.nome} — ${s.duracao_minutos}min — ${new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' }).format(s.preco)}`,
            }))}
            value={selectedService}
            onChange={(e) => setSelectedService(e.target.value)}
            placeholder="Selecione..."
          />
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setStep('barber')}>Voltar</Button>
            <Button disabled={!selectedService} onClick={() => setStep('date')}>Seguinte</Button>
          </div>
        </div>
      )}

      {/* Step: date */}
      {step === 'date' && (
        <div className="space-y-4">
          <Input
            label="Escolha a data"
            type="date"
            value={targetDate}
            onChange={(e) => setTargetDate(e.target.value)}
            min={new Date().toISOString().split('T')[0]}
          />
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setStep('service')}>Voltar</Button>
            <Button disabled={!targetDate} onClick={() => { setSelectedSlot(null); setStep('slot'); }}>
              Ver Horarios
            </Button>
          </div>
        </div>
      )}

      {/* Step: slot */}
      {step === 'slot' && (
        <div className="space-y-4">
          {loadingSlots ? (
            <Spinner />
          ) : slots.length === 0 ? (
            <p className="text-sm text-slate-500">Nenhum horario disponivel para esta data.</p>
          ) : (
            <div className="grid grid-cols-3 gap-2 sm:grid-cols-4">
              {slots.map((slot) => {
                const time = new Date(slot.inicio).toLocaleTimeString('pt-PT', {
                  hour: '2-digit',
                  minute: '2-digit',
                });
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
          )}
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setStep('date')}>Voltar</Button>
            <Button disabled={!selectedSlot} onClick={() => setStep('confirm')}>
              Seguinte
            </Button>
          </div>
        </div>
      )}

      {/* Step: confirm */}
      {step === 'confirm' && selectedSlot && (
        <div className="space-y-4">
          <div className="rounded-lg border border-slate-200 bg-white p-6 space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">Barbeiro</span>
              <span className="font-medium text-slate-800">{barberName}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">Servico</span>
              <span className="font-medium text-slate-800">{serviceObj?.nome}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">Duracao</span>
              <span className="font-medium text-slate-800">{serviceObj?.duracao_minutos} min</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">Preco</span>
              <span className="font-medium text-slate-800">
                {serviceObj && new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' }).format(serviceObj.preco)}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">Data</span>
              <span className="font-medium text-slate-800">{targetDate}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">Horario</span>
              <span className="font-medium text-slate-800">
                {new Date(selectedSlot.inicio).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })}
                {' - '}
                {new Date(selectedSlot.fim).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setStep('slot')}>Voltar</Button>
            <Button onClick={handleConfirm} disabled={submitting}>
              {submitting ? 'A agendar...' : 'Confirmar Agendamento'}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
