import { Navigate } from "react-router-dom";
import { Spinner } from "@/components/ui/spinner";
import { useAuth } from "@/stores/AppContext";

export function HomeRedirect() {
  const { ready, authenticated } = useAuth();
  if (!ready) {
    return (
      <div className="flex min-h-svh items-center justify-center">
        <Spinner label="Loading session" />
      </div>
    );
  }
  return <Navigate to={authenticated ? "/calendar" : "/login"} replace />;
}
