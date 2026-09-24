import { CalendarOff } from 'lucide-react';

export function EmptyCalendarState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <CalendarOff className="mb-4 size-10 text-muted-foreground" aria-hidden="true" />
      <h2 className="text-lg font-semibold">No activities scheduled</h2>
      <p className="mt-1 max-w-sm text-sm text-muted-foreground">
        Use Add Activity in the toolbar to schedule your first marketing activity.
      </p>
    </div>
  );
}
