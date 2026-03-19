export function toDateKey(value: Date | string): string {
  if (typeof value === 'string') {
    return value.includes('T') ? value.slice(0, 10) : value;
  }

  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, '0');
  const day = String(value.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function monthKeyFromDate(value: Date | string): string {
  return toDateKey(value).slice(0, 7);
}

export function parseMonthKey(month: string): Date {
  const [year, monthNumber] = month.split('-').map(Number);
  return new Date(year, (monthNumber || 1) - 1, 1);
}

export function shiftMonth(month: string, offset: number): string {
  const current = parseMonthKey(month);
  const shifted = new Date(current.getFullYear(), current.getMonth() + offset, 1);
  return `${shifted.getFullYear()}-${String(shifted.getMonth() + 1).padStart(2, '0')}`;
}

export function buildMonthDays(month: string): Date[] {
  const firstDay = parseMonthKey(month);
  const firstWeekday = (firstDay.getDay() + 6) % 7;
  const gridStart = new Date(firstDay);
  gridStart.setDate(firstDay.getDate() - firstWeekday);

  return Array.from({ length: 42 }, (_, index) => {
    const day = new Date(gridStart);
    day.setDate(gridStart.getDate() + index);
    return day;
  });
}

export function monthBounds(month: string): { startDate: string; endDate: string } {
  const start = parseMonthKey(month);
  const end = new Date(start.getFullYear(), start.getMonth() + 1, 0);
  return {
    startDate: toDateKey(start),
    endDate: toDateKey(end),
  };
}

export function formatMonthLabel(month: string): string {
  return parseMonthKey(month).toLocaleDateString('pt-PT', {
    month: 'long',
    year: 'numeric',
  });
}

export function formatDayLabel(date: Date): string {
  return date.toLocaleDateString('pt-PT', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
  });
}
