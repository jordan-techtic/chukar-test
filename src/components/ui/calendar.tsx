import type { ComponentProps } from "react";
import { DayPicker } from "react-day-picker";
import { cn } from "@/lib/utils";
import "react-day-picker/style.css";

type CalendarProps = ComponentProps<typeof DayPicker>;

function Calendar({ className, ...props }: CalendarProps) {
  return (
    <DayPicker
      weekStartsOn={1}
      showOutsideDays
      className={cn("text-sm [--rdp-accent-color:var(--primary)] [--rdp-accent-background-color:var(--muted)]", className)}
      {...props}
    />
  );
}

export { Calendar };
