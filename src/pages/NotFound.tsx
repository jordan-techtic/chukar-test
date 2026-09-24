import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAppContext } from "@/stores/AppContext";

export function NotFound() {
  const { status } = useAppContext();
  const signedIn = status === "authenticated";
  return (
    <main className="flex min-h-svh flex-col items-center justify-center gap-4 bg-background px-4 text-center">
      <h1 className="text-[28px] font-semibold leading-9 text-foreground">404 Not Found</h1>
      <p className="text-sm text-muted-foreground">This page does not exist.</p>
      <Button asChild>
        <Link to={signedIn ? "/calendar" : "/login"}>{signedIn ? "Back to calendar" : "Back to sign in"}</Link>
      </Button>
    </main>
  );
}
