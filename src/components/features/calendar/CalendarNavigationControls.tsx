import { ChevronLeft, ChevronRight } from 'lucide-react';
import { MONTH_NAMES } from '@/lib/calendar-utils';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface CalendarNavigationControlsProps {
  year: number;
  month: number;
  onYearChange: (year: number) => void;
  onMonthChange: (month: number) => void;
  onToday: () => void;
  onCreateActivity: () => void;
}

export function CalendarNavigationControls({
  year,
  month,
  onYearChange,
  onMonthChange,
  onToday,
  onCreateActivity,
}: CalendarNavigationControlsProps) {
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 11 }, (_, i) => currentYear - 5 + i);

  return (
    <div className="flex flex-wrap items-center gap-2">
      <div className="flex items-center gap-1">
        <Button
          type="button"
          variant="outline"
          size="icon"
          className="size-8"
          onClick={() => onYearChange(year - 1)}
          aria-label="Previous year"
        >
          <ChevronLeft className="size-4" />
        </Button>
        <Select value={String(year)} onValueChange={(v) => onYearChange(Number(v))}>
          <SelectTrigger className="h-8 w-[88px]" aria-label="Year">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {years.map((y) => (
              <SelectItem key={y} value={String(y)}>
                {y}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          type="button"
          variant="outline"
          size="icon"
          className="size-8"
          onClick={() => onYearChange(year + 1)}
          aria-label="Next year"
        >
          <ChevronRight className="size-4" />
        </Button>
      </div>

      <div className="flex items-center gap-1">
        <Button
          type="button"
          variant="outline"
          size="icon"
          className="size-8"
          onClick={() => {
            if (month === 1) {
              onYearChange(year - 1);
              onMonthChange(12);
            } else {
              onMonthChange(month - 1);
            }
          }}
          aria-label="Previous month"
        >
          <ChevronLeft className="size-4" />
        </Button>
        <Select value={String(month)} onValueChange={(v) => onMonthChange(Number(v))}>
          <SelectTrigger className="h-8 w-[120px]" aria-label="Month">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {MONTH_NAMES.map((name, index) => (
              <SelectItem key={name} value={String(index + 1)}>
                {name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          type="button"
          variant="outline"
          size="icon"
          className="size-8"
          onClick={() => {
            if (month === 12) {
              onYearChange(year + 1);
              onMonthChange(1);
            } else {
              onMonthChange(month + 1);
            }
          }}
          aria-label="Next month"
        >
          <ChevronRight className="size-4" />
        </Button>
      </div>

      <Button type="button" variant="outline" size="sm" className="h-8" onClick={onToday}>
        Today
      </Button>

      <Button type="button" size="sm" className="h-8" onClick={onCreateActivity}>
        Add Activity
      </Button>
    </div>
  );
}
