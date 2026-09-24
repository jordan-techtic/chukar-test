import { ChevronLeft, ChevronRight } from "lucide-react";
import type { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

interface CalendarNavigationProps {
  year: number;
  onPreviousYear: () => void;
  onNextYear: () => void;
  onToday: () => void;
  onPreviousMonth: () => void;
  onNextMonth: () => void;
}

function IconButton({
  label,
  onClick,
  children,
}: {
  label: string;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button type="button" variant="outline" size="icon" aria-label={label} onClick={onClick}>
          {children}
        </Button>
      </TooltipTrigger>
      <TooltipContent>{label}</TooltipContent>
    </Tooltip>
  );
}

export function CalendarNavigation({
  year,
  onPreviousYear,
  onNextYear,
  onToday,
  onPreviousMonth,
  onNextMonth,
}: CalendarNavigationProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <IconButton label={`Previous year, ${year - 1}`} onClick={onPreviousYear}>
        <ChevronLeft aria-hidden="true" />
      </IconButton>
      <p className="min-w-14 text-center text-sm font-semibold text-foreground">{year}</p>
      <IconButton label={`Next year, ${year + 1}`} onClick={onNextYear}>
        <ChevronRight aria-hidden="true" />
      </IconButton>
      <Button type="button" variant="outline" size="sm" onClick={onToday}>
        Today
      </Button>
      <IconButton label="Previous month" onClick={onPreviousMonth}>
        <ChevronLeft aria-hidden="true" />
      </IconButton>
      <IconButton label="Next month" onClick={onNextMonth}>
        <ChevronRight aria-hidden="true" />
      </IconButton>
    </div>
  );
}
