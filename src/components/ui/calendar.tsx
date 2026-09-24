import { DayPicker, type DayPickerProps } from "react-day-picker";
import { cn } from "@/lib/cn";
import "react-day-picker/style.css";

export function Calendar({ className, ...props }: DayPickerProps) {
  return (
    <DayPicker
      weekStartsOn={1}
      showOutsideDays
      className={cn("text-sm [--rdp-accent-color:var(--primary)] [--rdp-accent-background-color:#fde8e8]", className)}
      {...props}
    />
  );
}
