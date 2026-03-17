import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import type { Barber, Service, AvailableSlot, PublicFeedback } from '../../types';

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

type Step = 'barber' | 'service' | 'date' | 'slot' | 'info' | 'confirm';

const STEPS: { key: Step; label: string }[] = [
  { key: 'barber', label: '1. Barbeiro' },
  { key: 'service', label: '2. Serviço' },
  { key: 'date', label: '3. Data' },
  { key: 'slot', label: '4. Horário' },
  { key: 'info', label: '5. Dados' },
  { key: 'confirm', label: '6. Confirmar' },
];
const STEP_ORDER: Step[] = ['barber', 'service', 'date', 'slot', 'info', 'confirm'];

function StarRating({ rating }: { rating: number }) {
  return (
    <span className="text-amber-400 text-sm">
      {'★'.repeat(Math.round(rating))}{'☆'.repeat(5 - Math.round(rating))}
      <span className="ml-1 text-slate-400 text-xs">{rating.toFixed(1)}</span>
    </span>
  );
}

export default function PublicBookPage() {
  const { tenantId } = useParams<{ tenantId: string }>();

  const [step, setStep] = useState<Step>('barber');
  const [barbers, setBarbers] = useState<Barber[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [slots, setSlots] = useState<AvailableSlot[]>([]);
  const [ratings, setRatings] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');

  /* selections */
  const [selectedBarber, setSelectedBarber] = useState<Barber | null>(null);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [targetDate, setTargetDate] = useState('');
  const [selectedSlot, setSelectedSlot] = useState<AvailableSlot | null>(null);

  /* client info */
  const [clientName, setClientName] = useState('');
  const [clientEmail, setClientEmail] = useState('');
  const [clientPhone, setClientPhone] = useState('');

  /* Clear error banner whenever the user navigates to a different step */
  useEffect(() => { setError(''); }, [step]);

  useEffect(() => {
    if (!tenantId) return;
    Promise.all([
      fetch(`${BASE}/public/tenants/${tenantId}/barbers`).then((r) => r.json()),
      fetch(`${BASE}/public/tenants/${tenantId}/services`).then((r) => r.json()),
    ])
      .then(([bData, sData]) => {
        setBarbers(Array.isArray(bData) ? bData : []);
        setServices(Array.isArray(sData) ? sData : []);
        /* fetch ratings for each barber in parallel, batch into one setState */
        const bList: Barber[] = Array.isArray(bData) ? bData : [];
        Promise.all(
          bList.map((b) =>
            fetch(`${BASE}/feedback/barber/${b.id}`)
              .then((r) => r.json())
              .then((items: PublicFeedback[]) => {
                if (!Array.isArray(items) || items.length === 0) return null;
                const avg = items.reduce((acc, f) => acc + f.rating, 0) / items.length;
                return [String(b.id), avg] as [string, number];
              })
              .catch(() => null)
          )
        ).then((results) => {
          const map: Record<string, number> = {};
          results.forEach((r) => { if (r) map[r[0]] = r[1]; });
          if (Object.keys(map).length > 0) setRatings(map);
        });
      })
      .catch(() => setError('Erro ao carregar dados da barbearia.'))
      .finally(() => setLoading(false));
  }, [tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (step !== 'slot' || !selectedBarber || !selectedService || !targetDate || !tenantId) return;
    setLoadingSlots(true);
    fetch(
      `${BASE}/public/tenants/${tenantId}/barbers/${selectedBarber.id}/slots?service_id=${selectedService.id}&target_date=${targetDate}&timezone=Europe/Lisbon`,
    )
      .then((r) => r.json())
      .then((data) => {
        const list = data?.slots ?? data;
        setSlots(Array.isArray(list) ? list : []);
      })
      .catch(() => setSlots([]))
      .finally(() => setLoadingSlots(false));
  }, [step, selectedBarber, selectedService, targetDate, tenantId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleConfirm() {
    if (!selectedSlot || !selectedBarber || !selectedService || !tenantId) return;
    setSubmitting(true);
    setError('');
    try {
      const res = await fetch(`${BASE}/public/appointments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: Number(tenantId),
          barber_id: Number(selectedBarber.id),
          service_id: Number(selectedService.id),
          start_at: selectedSlot.inicio,
          client_name: clientName,
          client_email: clientEmail,
          client_phone: clientPhone || null,
        }),
      });
      if (!res.ok) throw new Error('Erro na resposta do servidor');
      setDone(true);
    } catch {
      setError('Erro ao criar agendamento. Tenta novamente.');
    } finally {
      setSubmitting(false);
    }
  }

  const currentIdx = STEP_ORDER.indexOf(step);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="h-8 w-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (done) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center px-4">
        <div className="w-full max-w-sm text-center space-y-4">
          <div className="text-5xl">✓</div>
          <h2 className="text-2xl font-bold text-amber-400">Agendamento Confirmado!</h2>
          <p className="text-slate-400">
            Receberás uma confirmação em <span className="text-white">{clientEmail}</span>.
          </p>
          <Link
            to={`/register?tenant=${tenantId}`}
            className="block w-full rounded-xl border border-amber-500/50 py-3 text-amber-400 font-medium hover:bg-amber-500/10 transition-colors"
          >
            Criar conta para gerir agendamentos
          </Link>
          <button
            onClick={() => {
              setDone(false);
              setStep('barber');
              setSelectedBarber(null);
              setSelectedService(null);
              setTargetDate('');
              setSelectedSlot(null);
              setClientName('');
              setClientEmail('');
              setClientPhone('');
            }}
            className="mt-4 w-full rounded-xl bg-amber-500 py-4 text-slate-900 font-semibold hover:bg-amber-400 transition-colors"
          >
            Novo Agendamento
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center px-4 py-8">
      <div className="w-full max-w-sm">
        {/* Brand */}
        <div className="mb-6 flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-amber-500 flex items-center justify-center text-slate-900 font-bold text-sm">
            B
          </div>
          <span className="text-white font-semibold text-lg">BarberPro</span>
        </div>

        {/* Progress bar */}
        <div className="mb-2 flex gap-1">
          {STEPS.map((s, i) => (
            <div
              key={s.key}
              className={`flex-1 h-1.5 rounded-full transition-colors ${
                i <= currentIdx ? 'bg-amber-500' : 'bg-slate-700'
              }`}
            />
          ))}
        </div>
        <p className="mb-6 text-sm text-slate-400">{STEPS[currentIdx].label}</p>

        {error && (
          <div className="mb-4 rounded-lg bg-red-900/30 border border-red-700 p-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {/* Step: barber */}
        {step === 'barber' && (
          <div className="space-y-3">
            <h2 className="text-xl font-bold text-white mb-4">Escolha o barbeiro</h2>
            {barbers.map((b) => (
              <button
                key={b.id}
                onClick={() => { setSelectedBarber(b); setStep('service'); }}
                className={`w-full rounded-xl border p-4 text-left transition-colors ${
                  selectedBarber?.id === b.id
                    ? 'border-amber-500 bg-amber-500/10'
                    : 'border-slate-700 bg-slate-800 hover:border-amber-500/50'
                }`}
              >
                <div className="font-semibold text-white">{b.nome}</div>
                {ratings[String(b.id)] !== undefined && (
                  <StarRating rating={ratings[String(b.id)]} />
                )}
              </button>
            ))}
            {barbers.length === 0 && (
              <p className="text-slate-500 text-sm">Nenhum barbeiro disponivel.</p>
            )}
          </div>
        )}

        {/* Step: service */}
        {step === 'service' && (
          <div className="space-y-3">
            <h2 className="text-xl font-bold text-white mb-4">Escolha o servico</h2>
            {services.map((s) => (
              <button
                key={s.id}
                onClick={() => { setSelectedService(s); setStep('date'); }}
                className={`w-full rounded-xl border p-4 text-left transition-colors ${
                  selectedService?.id === s.id
                    ? 'border-amber-500 bg-amber-500/10'
                    : 'border-slate-700 bg-slate-800 hover:border-amber-500/50'
                }`}
              >
                <div className="font-semibold text-white">{s.nome}</div>
                <div className="text-sm text-slate-400 mt-1">
                  {s.duracao_minutos} min ·{' '}
                  {new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' }).format(s.preco)}
                </div>
              </button>
            ))}
            <button
              onClick={() => setStep('barber')}
              className="w-full rounded-xl border border-slate-700 py-3 text-slate-400 hover:text-white transition-colors"
            >
              Voltar
            </button>
          </div>
        )}

        {/* Step: date */}
        {step === 'date' && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-white mb-4">Escolha a data</h2>
            <input
              type="date"
              value={targetDate}
              min={new Date().toISOString().split('T')[0]}
              onChange={(e) => setTargetDate(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-4 text-white text-base focus:outline-none focus:border-amber-500"
            />
            <button
              disabled={!targetDate}
              onClick={() => { setSelectedSlot(null); setStep('slot'); }}
              className="w-full rounded-xl bg-amber-500 py-4 text-slate-900 font-semibold disabled:opacity-40 hover:bg-amber-400 transition-colors"
            >
              Ver Horarios
            </button>
            <button
              onClick={() => setStep('service')}
              className="w-full rounded-xl border border-slate-700 py-3 text-slate-400 hover:text-white transition-colors"
            >
              Voltar
            </button>
          </div>
        )}

        {/* Step: slot */}
        {step === 'slot' && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-white mb-4">Escolha o horario</h2>
            {loadingSlots ? (
              <div className="flex justify-center py-8">
                <div className="h-8 w-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : slots.length === 0 ? (
              <p className="text-slate-500 text-sm py-4">Nenhum horario disponivel para esta data.</p>
            ) : (
              <div className="grid grid-cols-3 gap-2">
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
                      className={`rounded-xl border py-3 text-sm font-medium transition-colors ${
                        isSelected
                          ? 'border-amber-500 bg-amber-500/10 text-amber-400'
                          : 'border-slate-700 bg-slate-800 text-slate-300 hover:border-amber-500/50'
                      }`}
                    >
                      {time}
                    </button>
                  );
                })}
              </div>
            )}
            <button
              disabled={!selectedSlot}
              onClick={() => setStep('info')}
              className="w-full rounded-xl bg-amber-500 py-4 text-slate-900 font-semibold disabled:opacity-40 hover:bg-amber-400 transition-colors"
            >
              Seguinte
            </button>
            <button
              onClick={() => setStep('date')}
              className="w-full rounded-xl border border-slate-700 py-3 text-slate-400 hover:text-white transition-colors"
            >
              Voltar
            </button>
          </div>
        )}

        {/* Step: info */}
        {step === 'info' && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-white mb-4">Os seus dados</h2>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Nome *</label>
              <input
                type="text"
                value={clientName}
                onChange={(e) => setClientName(e.target.value)}
                placeholder="O seu nome completo"
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-4 text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Email *</label>
              <input
                type="email"
                value={clientEmail}
                onChange={(e) => setClientEmail(e.target.value)}
                placeholder="email@exemplo.com"
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-4 text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Telefone (opcional)</label>
              <input
                type="tel"
                value={clientPhone}
                onChange={(e) => setClientPhone(e.target.value)}
                placeholder="+351 9XX XXX XXX"
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-4 text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>
            <button
              disabled={!clientName.trim() || !clientEmail.trim()}
              onClick={() => setStep('confirm')}
              className="w-full rounded-xl bg-amber-500 py-4 text-slate-900 font-semibold disabled:opacity-40 hover:bg-amber-400 transition-colors"
            >
              Seguinte
            </button>
            <button
              onClick={() => setStep('slot')}
              className="w-full rounded-xl border border-slate-700 py-3 text-slate-400 hover:text-white transition-colors"
            >
              Voltar
            </button>
          </div>
        )}

        {/* Step: confirm */}
        {step === 'confirm' && selectedSlot && selectedBarber && selectedService && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-white mb-4">Confirmar Agendamento</h2>
            <div className="rounded-xl border border-slate-700 bg-slate-800 p-5 space-y-3">
              {[
                { label: 'Barbeiro', value: selectedBarber.nome },
                { label: 'Servico', value: selectedService.nome },
                {
                  label: 'Duracao',
                  value: `${selectedService.duracao_minutos} min`,
                },
                {
                  label: 'Preco',
                  value: new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' }).format(selectedService.preco),
                },
                { label: 'Data', value: new Date(targetDate + 'T00:00').toLocaleDateString('pt-PT') },
                {
                  label: 'Horario',
                  value: `${new Date(selectedSlot.inicio).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })} – ${new Date(selectedSlot.fim).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })}`,
                },
                { label: 'Nome', value: clientName },
                { label: 'Email', value: clientEmail },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between text-sm">
                  <span className="text-slate-400">{label}</span>
                  <span className="font-medium text-white">{value}</span>
                </div>
              ))}
            </div>
            <button
              onClick={handleConfirm}
              disabled={submitting}
              className="w-full rounded-xl bg-amber-500 py-4 text-slate-900 font-bold disabled:opacity-40 hover:bg-amber-400 transition-colors"
            >
              {submitting ? 'A agendar...' : 'Confirmar Agendamento'}
            </button>
            <button
              onClick={() => setStep('info')}
              className="w-full rounded-xl border border-slate-700 py-3 text-slate-400 hover:text-white transition-colors"
            >
              Voltar
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
