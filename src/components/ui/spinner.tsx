import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

type SpinnerProps = {
  label: string;
  className?: string;
  visibleLabel?: boolean;
};

function Spinner({ label, className, visibleLabel = true }: SpinnerProps) {
  return (
    <span role="status" className={cn("inline-flex items-center gap-2 text-sm text-muted-foreground", className)}>
      <Loader2 className="size-4 animate-spin" aria-hidden />
      <span className={visibleLabel ? undefined : "sr-only"}>{label}</span>
    </span>
  );
}

export { Spinner };
