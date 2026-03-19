import { buildMonthDays, formatMonthLabel, monthKeyFromDate, shiftMonth, toDateKey } from '../lib/dateCalendar';

interface DateAvailabilityCalendarProps {
  month: string;
  onMonthChange: (month: string) => void;
  selectedDate: string;
  onSelectDate: (date: string) => void;
  highlightedDates: string[];
  loading?: boolean;
  minDate?: string;
  tone?: 'available' | 'appointments';
  theme?: 'light' | 'dark';
  helperText?: string;
  emptyText?: string;
}

const WEEKDAY_LABELS = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'];

export default function DateAvailabilityCalendar({
  month,
  onMonthChange,
  selectedDate,
  onSelectDate,
  highlightedDates,
  loading = false,
  minDate,
  tone = 'available',
  theme = 'light',
  helperText,
  emptyText,
}: DateAvailabilityCalendarProps) {
  const selectedMonth = monthKeyFromDate(month);
  const highlighted = new Set(highlightedDates);
  const days = buildMonthDays(selectedMonth);

  const darkTheme = theme === 'dark';

  return (
    <div className={`rounded-2xl border p-4 shadow-sm ${
      darkTheme ? 'border-slate-700 bg-slate-800' : 'border-slate-200 bg-white'
    }`}>
      <div className="mb-4 flex items-center justify-between gap-2">
        <button
          type="button"
          onClick={() => onMonthChange(shiftMonth(selectedMonth, -1))}
          className={`rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
            darkTheme
              ? 'border-slate-700 text-slate-300 hover:border-slate-500 hover:text-white'
              : 'border-slate-200 text-slate-600 hover:border-slate-300 hover:text-slate-800'
          }`}
        >
          Anterior
        </button>
        <div className="text-center">
          <p className={`text-sm font-semibold capitalize ${darkTheme ? 'text-white' : 'text-slate-800'}`}>
            {formatMonthLabel(selectedMonth)}
          </p>
          {helperText && <p className={`text-xs ${darkTheme ? 'text-slate-400' : 'text-slate-500'}`}>{helperText}</p>}
        </div>
        <button
          type="button"
          onClick={() => onMonthChange(shiftMonth(selectedMonth, 1))}
          className={`rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
            darkTheme
              ? 'border-slate-700 text-slate-300 hover:border-slate-500 hover:text-white'
              : 'border-slate-200 text-slate-600 hover:border-slate-300 hover:text-slate-800'
          }`}
        >
          Seguinte
        </button>
      </div>

      <div className={`mb-2 grid grid-cols-7 gap-1 text-center text-xs font-medium uppercase tracking-wide ${
        darkTheme ? 'text-slate-500' : 'text-slate-400'
      }`}>
        {WEEKDAY_LABELS.map((label) => (
          <div key={label}>{label}</div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {days.map((date) => {
          const key = toDateKey(date);
          const inMonth = monthKeyFromDate(date) === selectedMonth;
          const isHighlighted = highlighted.has(key);
          const isSelected = selectedDate === key;
          const isDisabled = !inMonth || (minDate ? key < minDate : false);

          let stateClasses = darkTheme
            ? 'border-slate-700 bg-slate-900 text-slate-500'
            : 'border-slate-200 bg-white text-slate-400';
          if (isHighlighted && tone === 'available') {
            stateClasses = darkTheme
              ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300'
              : 'border-emerald-200 bg-emerald-50 text-emerald-700';
          }
          if (isHighlighted && tone === 'appointments') {
            stateClasses = darkTheme
              ? 'border-amber-500/40 bg-amber-500/10 text-amber-300'
              : 'border-amber-200 bg-amber-50 text-amber-700';
          }
          if (isSelected) {
            stateClasses = tone === 'appointments'
              ? 'border-amber-500 bg-amber-500 text-white'
              : 'border-emerald-500 bg-emerald-500 text-white';
          }
          if (isDisabled) {
            stateClasses = darkTheme
              ? 'border-slate-800 bg-slate-900 text-slate-700'
              : 'border-slate-100 bg-slate-50 text-slate-300';
          }

          return (
            <button
              key={key}
              type="button"
              disabled={isDisabled || (!isHighlighted && !isSelected)}
              onClick={() => onSelectDate(key)}
              className={`relative min-h-11 rounded-xl border text-sm font-medium transition-colors ${stateClasses} ${
                isDisabled || (!isHighlighted && !isSelected)
                  ? 'cursor-not-allowed'
                  : 'cursor-pointer hover:brightness-95'
              }`}
              title={key}
            >
              {date.getDate()}
              {isHighlighted && !isSelected && (
                <span
                  className={`absolute bottom-1 left-1/2 h-1.5 w-1.5 -translate-x-1/2 rounded-full ${
                    tone === 'appointments' ? 'bg-amber-500' : 'bg-emerald-500'
                  }`}
                />
              )}
            </button>
          );
        })}
      </div>

      {loading && <p className={`mt-3 text-sm ${darkTheme ? 'text-slate-400' : 'text-slate-500'}`}>A carregar datas...</p>}
      {!loading && highlighted.size === 0 && emptyText && (
        <p className={`mt-3 text-sm ${darkTheme ? 'text-slate-400' : 'text-slate-500'}`}>{emptyText}</p>
      )}
    </div>
  );
}
