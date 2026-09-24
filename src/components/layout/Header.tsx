import { LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { queryClient } from "@/lib/queryClient";
import { useAppContext } from "@/stores/AppContext";

export function Header() {
  const { user, logout } = useAppContext();
  const navigate = useNavigate();

  function onLogout() {
    logout();
    queryClient.clear();
    navigate("/login", { replace: true });
  }

  return (
    <header className="flex h-16 items-center justify-between gap-3 border-b border-border bg-card px-4">
      <p className="truncate text-sm font-semibold text-foreground xl:hidden">Marketing Content Calendar</p>
      <p className="hidden text-sm font-semibold text-foreground xl:block">Marketing Content Calendar</p>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" type="button" aria-label="Account menu">
            {user?.username ?? "Account"}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onSelect={onLogout}>
            <LogOut className="size-4" aria-hidden="true" />
            Sign out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
