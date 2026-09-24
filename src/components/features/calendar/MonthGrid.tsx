import { ActivityEntry } from "@/components/features/calendar/ActivityEntry";
import { formatIsoDate, MONTH_NAMES } from "@/lib/format";
import type { ActivityOut } from "@/types/api";

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] as const;

function monthCells(year: number, monthIndex: number) {
  const first = new Date(year, monthIndex, 1);
  const lead = (first.getDay() + 6) % 7;
  const days = new Date(year, monthIndex + 1, 0).getDate();
  const cells: { date: Date; inMonth: boolean }[] = [];
  for (let index = 0; index < lead; index += 1) {
    cells.push({ date: new Date(year, monthIndex, 1 - (lead - index)), inMonth: false });
  }
  for (let day = 1; day <= days; day += 1) {
    cells.push({ date: new Date(year, monthIndex, day), inMonth: true });
  }
  while (cells.length % 7 !== 0) {
    const previous = cells[cells.length - 1]?.date ?? first;
    const next = new Date(previous);
    next.setDate(previous.getDate() + 1);
    cells.push({ date: next, inMonth: false });
  }
  return cells;
}

function covers(activity: ActivityOut, iso: string): boolean {
  const start = activity.start_date || activity.date;
  const end = activity.end_date || start;
  return iso >= start && iso <= end;
}

export function MonthGrid({
  year,
  month,
  today,
  activities,
  onOpen,
}: {
  year: number;
  month: number;
  today: string;
  activities: ActivityOut[];
  onOpen: (activity: ActivityOut) => void;
}) {
  const cells = monthCells(year, month - 1);
  return (
    <section id={`month-${month}`} className="rounded-lg border border-border bg-card p-3">
      <h2 className="mb-3 text-lg font-semibold leading-6 text-foreground">{MONTH_NAMES[month - 1]}</h2>
      <div className="grid grid-cols-7 gap-1">
        {WEEKDAYS.map((day) => (
          <div key={day} className="px-1 text-center text-xs font-medium text-muted-foreground">
            {day}
          </div>
        ))}
        {cells.map((cell) => {
          const iso = formatIsoDate(cell.date);
          const dayActivities = cell.inMonth ? activities.filter((activity) => covers(activity, iso)) : [];
          return (
            <div
              key={iso + String(cell.inMonth)}
              className="min-h-16 min-w-0 rounded-sm p-1"
            >
              <p className={cell.inMonth ? "text-sm text-foreground" : "text-sm text-muted-foreground"}>
                {cell.inMonth && iso === today ? (
                  <span className="inline-flex size-6 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
                    {cell.date.getDate()}
                  </span>
                ) : (
                  cell.date.getDate()
                )}
              </p>
              {cell.inMonth ? (
                <div className="mt-1 space-y-1">
                  {dayActivities.map((activity) => (
                    <ActivityEntry key={activity.id + iso} activity={activity} date={iso} onOpen={onOpen} />
                  ))}
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </section>
  );
}
