import type { ActivityOut } from '@/types/api';

export function parseIsoDate(dateStr: string): Date {
  const [year, month, day] = dateStr.split('-').map(Number);
  return new Date(year, month - 1, day);
}

export function formatIsoDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function buildWeeksForYear(year: number): Date[][] {
  const weeks: Date[][] = [];
  const cursor = new Date(year, 0, 1);
  const dayOfWeek = cursor.getDay();
  const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
  cursor.setDate(cursor.getDate() + mondayOffset);

  while (true) {
    const week: Date[] = [];
    for (let i = 0; i < 7; i++) {
      week.push(new Date(cursor));
      cursor.setDate(cursor.getDate() + 1);
    }

    const hasYearDay = week.some((d) => d.getFullYear() === year);
    if (hasYearDay) {
      weeks.push(week);
    }

    if (week[0].getFullYear() > year && week[6].getFullYear() > year) {
      break;
    }
  }

  return weeks;
}

export function weekIntersectsMonth(week: Date[], month: number): boolean {
  return week.some((d) => d.getMonth() + 1 === month);
}

export function activityOnDate(activity: ActivityOut, date: Date): boolean {
  const start = parseIsoDate(activity.start_date || activity.date);
  const end = parseIsoDate(activity.end_date || activity.start_date || activity.date);
  const time = date.getTime();
  return time >= start.getTime() && time <= end.getTime();
}

export const MONTH_NAMES = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
];

export const WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
