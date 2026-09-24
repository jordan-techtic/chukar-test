import { Navigate, Outlet, useLocation } from "react-router-dom";
import { Spinner } from "@/components/ui/spinner";
import { useAuth } from "@/stores/AppContext";

export function ProtectedRoute() {
  const { ready, authenticated } = useAuth();
  const location = useLocation();

  if (!ready) {
    return (
      <div className="flex min-h-svh items-center justify-center">
        <Spinner label="Loading session" />
      </div>
    );
  }

  if (!authenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}
