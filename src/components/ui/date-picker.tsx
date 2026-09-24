import { forwardRef, useState, type ComponentProps } from "react";
import { Calendar as CalendarIcon } from "lucide-react";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/cn";
import { formatDisplayDate, formatIsoDate, parseIsoDate } from "@/lib/format";

export { Calendar };

interface DatePickerProps extends Omit<ComponentProps<"button">, "value" | "onChange"> {
  value: string;
  onChange: (value: string) => void;
  invalid?: boolean;
  placeholder?: string;
}

export const DatePicker = forwardRef<HTMLButtonElement, DatePickerProps>(function DatePicker(
  { id, value, onChange, disabled, invalid, placeholder = "Pick a date", className, ...props },
  ref,
) {
  const [open, setOpen] = useState(false);
  const selected = value ? parseIsoDate(value) : undefined;
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          ref={ref}
          id={id}
          type="button"
          disabled={disabled}
          aria-invalid={invalid || props["aria-invalid"] || undefined}
          className={cn(
            "flex h-10 w-full items-center justify-between rounded-md border border-input bg-card px-3 text-left text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50",
            (invalid || props["aria-invalid"]) && "border-destructive",
            !value && "text-muted-foreground",
            className,
          )}
          {...props}
        >
          <span>{value ? formatDisplayDate(value) : placeholder}</span>
          <CalendarIcon className="size-4 text-muted-foreground" aria-hidden="true" />
        </button>
      </PopoverTrigger>
      <PopoverContent>
        <Calendar
          mode="single"
          selected={selected}
          onSelect={(date) => {
            onChange(date ? formatIsoDate(date) : "");
            setOpen(false);
          }}
        />
      </PopoverContent>
    </Popover>
  );
});
