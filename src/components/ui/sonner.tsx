/* eslint-disable react-refresh/only-export-components */
import { CircleCheck, Info, Loader2, OctagonX, TriangleAlert } from "lucide-react";
import type { CSSProperties, ComponentProps } from "react";
import { Toaster as SonnerToaster, toast as sonnerToast, useSonner } from "sonner";
import { cn } from "@/lib/cn";

export const toast = sonnerToast;
export { useSonner };

type ToasterProps = ComponentProps<typeof SonnerToaster>;

type SonnerStyle = CSSProperties & {
  "--normal-bg": string;
  "--normal-text": string;
  "--normal-border": string;
};

function toasterStyle(style: CSSProperties | undefined): SonnerStyle {
  const next: SonnerStyle = {
    "--normal-bg": "var(--popover)",
    "--normal-text": "var(--popover-foreground)",
    "--normal-border": "var(--border)",
  };
  if (style) {
    Object.assign(next, style);
  }
  next["--normal-bg"] = "var(--popover)";
  next["--normal-text"] = "var(--popover-foreground)";
  next["--normal-border"] = "var(--border)";
  return next;
}

export function Toaster({ className, style, duration = 4000, ...props }: ToasterProps) {
  return (
    <SonnerToaster
      theme="light"
      className={cn("toaster group", className)}
      {...props}
      richColors
      closeButton
      position="top-right"
      duration={duration}
      icons={{
        success: <CircleCheck className="size-4" aria-hidden="true" />,
        info: <Info className="size-4" aria-hidden="true" />,
        warning: <TriangleAlert className="size-4" aria-hidden="true" />,
        error: <OctagonX className="size-4" aria-hidden="true" />,
        loading: <Loader2 className="size-4 animate-spin" aria-hidden="true" />,
      }}
      toastOptions={{
        duration,
        classNames: {
          toast: "group toast border-border bg-popover text-popover-foreground",
          description: "text-muted-foreground",
          actionButton: "bg-primary text-primary-foreground",
          cancelButton: "bg-muted text-muted-foreground",
        },
      }}
      style={toasterStyle(style)}
    />
  );
}
