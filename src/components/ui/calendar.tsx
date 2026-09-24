import { ChevronLeft, ChevronRight } from "lucide-react";
import { DayPicker, type ChevronProps, type DayPickerProps } from "react-day-picker";
import { cn } from "@/lib/cn";
import "react-day-picker/style.css";

function CalendarChevron({ orientation, className, size = 16 }: ChevronProps) {
  const Icon = orientation === "left" || orientation === "up" ? ChevronLeft : ChevronRight;
  return <Icon className={className} size={size} aria-hidden="true" />;
}

export function Calendar({ className, ...props }: DayPickerProps) {
  return (
    <DayPicker
      weekStartsOn={1}
      showOutsideDays
      navLayout="around"
      className={cn(
        "text-sm [--rdp-accent-color:var(--primary)] [--rdp-accent-background-color:#fde8e8] [--rdp-day-height:2rem] [--rdp-day-width:2rem] [--rdp-nav-height:2rem]",
        className,
      )}
      components={{ Chevron: CalendarChevron }}
      labels={{
        labelPrevious: () => "Previous month",
        labelNext: () => "Next month",
      }}
      {...props}
    />
  );
}
