import type { SVGAttributes } from "react";
import { cn } from "@/lib/cn";

interface SpinnerProps extends SVGAttributes<SVGSVGElement> {
  label?: string;
}

export function Spinner({ label = "Loading", className, ...props }: SpinnerProps) {
  return (
    <span className="inline-flex" role="status">
      <svg
        viewBox="0 0 24 24"
        aria-hidden="true"
        className={cn("size-6 animate-spin text-current", className)}
        fill="none"
        {...props}
      >
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeOpacity="0.25" strokeWidth="3" />
        <path
          d="M21 12a9 9 0 0 0-9-9"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
      <span className="sr-only">{label}</span>
    </span>
  );
}
