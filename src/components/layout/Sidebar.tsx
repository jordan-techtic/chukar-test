import { NavLink } from "react-router-dom";
import { cn } from "@/lib/cn";

export function Sidebar({ className }: { className?: string }) {
  return (
    <aside className={cn("flex flex-col gap-6 border-border bg-card p-4", className)}>
      <img src="/brand-logo.png" alt="Marketing Content Calendar" className="h-8 w-auto self-start" />
      <nav aria-label="Primary">
        <NavLink
          to="/calendar"
          end
          className={({ isActive }) =>
            cn(
              "inline-flex h-10 items-center rounded-full px-4 text-sm font-semibold focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
              isActive ? "bg-primary text-primary-foreground" : "text-foreground hover:bg-muted",
            )
          }
        >
          Calendar
        </NavLink>
      </nav>
    </aside>
  );
}
