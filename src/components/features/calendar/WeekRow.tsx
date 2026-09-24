import type { ActivityOut } from '@/types/api';
import { formatIsoDate } from '@/lib/calendar-utils';
import { cn } from '@/lib/utils';
import { ActivityEntry } from './ActivityEntry';

interface WeekRowProps {
  week: Date[];
  year: number;
  month: number | null;
  today: string;
  activities: ActivityOut[];
  onActivityClick: (activity: ActivityOut) => void;
}

export function WeekRow({ week, year, month, today, activities, onActivityClick }: WeekRowProps) {
  return (
    <div className="grid grid-cols-7 border-b border-border last:border-b-0">
      {week.map((day) => {
        const iso = formatIsoDate(day);
        const inYear = day.getFullYear() === year;
        const inSelectedMonth = month == null || day.getMonth() + 1 === month;
        const isToday = iso === today;
        const dayActivities = inYear
          ? activities.filter((activity) => {
              const start = activity.start_date || activity.date;
              return start === iso;
            })
          : [];

        return (
          <div
            key={iso}
            className={cn(
              'min-h-[88px] border-r border-border p-2 last:border-r-0 md:min-h-[100px]',
              !inYear && 'bg-muted/40 text-muted-foreground',
              inYear && !inSelectedMonth && 'opacity-60',
            )}
          >
            <div
              className={cn(
                'mb-2 inline-flex size-7 items-center justify-center rounded-full text-xs font-medium',
                isToday && inYear && 'ring-2 ring-ring ring-offset-1',
              )}
            >
              {day.getDate()}
            </div>
            <div className="space-y-0.5">
              {dayActivities.map((activity) => (
                <ActivityEntry key={activity.id} activity={activity} onClick={onActivityClick} />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
