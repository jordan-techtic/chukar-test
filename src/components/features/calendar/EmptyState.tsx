import { CalendarOff } from "lucide-react";

export function EmptyState({ year }: { year: number }) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 text-sm text-muted-foreground">
      <CalendarOff className="size-4 shrink-0" aria-hidden="true" />
      <p>No marketing activities are scheduled for {year}.</p>
    </div>
  );
}
