import { useState } from "react";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { SidebarNav } from "@/components/layout/Sidebar";
import { useAuth } from "@/stores/AppContext";
import { humanizeEnum } from "@/lib/utils";

function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0] ?? ""}${parts[1][0] ?? ""}`.toUpperCase();
}

export function Header() {
  const { user, logout } = useAuth();
  const [navOpen, setNavOpen] = useState(false);
  const displayName = user?.username || user?.email || "Account";
  const role = user?.role ? humanizeEnum(user.role) : "";

  return (
    <header className="flex h-16 items-center justify-between gap-3 border-b border-border bg-card px-4">
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="lg:hidden"
        aria-label="Open navigation"
        aria-expanded={navOpen}
        onClick={() => setNavOpen(true)}
      >
        <Menu aria-hidden />
      </Button>
      <Sheet open={navOpen} onOpenChange={setNavOpen}>
        <SheetContent>
          <SheetHeader>
            <img src="/brand-logo.png" alt="Brand logo" className="h-8 w-auto max-w-[9.5rem] object-contain" />
          </SheetHeader>
          <SheetTitle className="sr-only">Navigation</SheetTitle>
          <SheetDescription className="sr-only">Calendar links</SheetDescription>
          <SidebarNav onNavigate={() => setNavOpen(false)} />
        </SheetContent>
      </Sheet>
      <div className="ml-auto">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              type="button"
              className="inline-flex h-11 items-center gap-2 rounded-full px-1.5 hover:bg-muted focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none md:h-10"
              aria-label="Account menu"
            >
              <span className="flex size-8 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
                {initials(displayName)}
              </span>
              <span className="hidden text-left sm:block">
                <span className="block max-w-40 truncate text-sm font-medium">{displayName}</span>
                {role ? (
                  <span className="block max-w-40 truncate text-xs text-muted-foreground">{role}</span>
                ) : null}
              </span>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>{displayName}</DropdownMenuLabel>
            {role ? <DropdownMenuLabel>{role}</DropdownMenuLabel> : null}
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onSelect={() => {
                logout();
              }}
            >
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
