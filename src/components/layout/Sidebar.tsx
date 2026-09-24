import { NavLink } from "react-router-dom";
import { CalendarDays } from "lucide-react";
import { cn } from "@/lib/utils";

export function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav aria-label="Primary" className="flex flex-col gap-1 p-3">
      <NavLink
        to="/calendar"
        onClick={onNavigate}
        className={({ isActive }) =>
          cn(
            "flex h-10 w-full items-center gap-3 rounded-full px-3 text-sm font-medium focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none",
            isActive
              ? "bg-primary text-primary-foreground"
              : "text-foreground hover:bg-muted",
          )
        }
      >
        <CalendarDays className="size-4" aria-hidden />
        Calendar
      </NavLink>
    </nav>
  );
}

export function Sidebar() {
  return (
    <aside className="hidden h-full flex-col border-r border-border bg-card lg:flex">
      <div className="flex h-16 items-center border-b border-border px-4">
        <img src="/brand-logo.png" alt="Brand logo" className="h-8 w-auto max-w-[9.5rem] object-contain" />
      </div>
      <SidebarNav />
    </aside>
  );
}
