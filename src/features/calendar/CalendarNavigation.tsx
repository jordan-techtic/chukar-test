import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { MONTHS, MAX_YEAR, MIN_YEAR } from "@/features/calendar/dates";

export function CalendarNavigation({
  year,
  onYearChange,
  onToday,
  onMonthSelect,
}: {
  year: number;
  onYearChange: (year: number) => void;
  onToday: () => void;
  onMonthSelect: (month: number) => void;
}) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              type="button"
              variant="outline"
              size="icon"
              aria-label="Previous year"
              disabled={year <= MIN_YEAR}
              onClick={() => onYearChange(year - 1)}
            >
              <ChevronLeft aria-hidden />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Previous year</TooltipContent>
        </Tooltip>
        <span className="min-w-16 text-center text-sm font-semibold" aria-live="polite">
          {year}
        </span>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              type="button"
              variant="outline"
              size="icon"
              aria-label="Next year"
              disabled={year >= MAX_YEAR}
              onClick={() => onYearChange(year + 1)}
            >
              <ChevronRight aria-hidden />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Next year</TooltipContent>
        </Tooltip>
        <Button type="button" variant="outline" size="sm" onClick={onToday}>
          Today
        </Button>
      </div>
      <div className="flex flex-wrap gap-2">
        {MONTHS.map((month, index) => (
          <Button
            key={month}
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => onMonthSelect(index + 1)}
          >
            {month}
          </Button>
        ))}
      </div>
    </div>
  );
}
