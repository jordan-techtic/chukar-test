import { useEffect } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { Spinner } from "@/components/ui/spinner";
import { useAppContext } from "@/stores/AppContext";

export function ProtectedRoute() {
  const { status, ensureSession } = useAppContext();
  const location = useLocation();

  useEffect(() => {
    ensureSession();
  }, [ensureSession]);

  if (status === "checking") {
    return (
      <div className="flex min-h-svh items-center justify-center bg-background" aria-busy="true">
        <Spinner label="Loading session" />
      </div>
    );
  }

  if (status !== "authenticated") {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}
