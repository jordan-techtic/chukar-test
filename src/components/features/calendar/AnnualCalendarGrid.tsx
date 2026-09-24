import type { ActivityOut } from '@/types/api';
import { buildWeeksForYear, WEEKDAY_LABELS } from '@/lib/calendar-utils';
import { WeekRow } from './WeekRow';

interface AnnualCalendarGridProps {
  year: number;
  month: number | null;
  today: string;
  activities: ActivityOut[];
  onActivityClick: (activity: ActivityOut) => void;
}

export function AnnualCalendarGrid({
  year,
  month,
  today,
  activities,
  onActivityClick,
}: AnnualCalendarGridProps) {
  const weeks = buildWeeksForYear(year);

  return (
    <div className="min-w-[640px] overflow-x-auto rounded-lg border border-border bg-card">
      <div className="grid grid-cols-7 border-b border-border bg-muted/30">
        {WEEKDAY_LABELS.map((label) => (
          <div
            key={label}
            className="px-2 py-2 text-center text-xs font-medium uppercase tracking-widest text-muted-foreground"
          >
            {label}
          </div>
        ))}
      </div>
      {weeks.map((week) => {
        const key = week.map((d) => d.toISOString()).join('-');
        return (
          <WeekRow
            key={key}
            week={week}
            year={year}
            month={month}
            today={today}
            activities={activities}
            onActivityClick={onActivityClick}
          />
        );
      })}
    </div>
  );
}
