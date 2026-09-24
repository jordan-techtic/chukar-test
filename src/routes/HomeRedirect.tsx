import { useEffect } from "react";
import { Navigate } from "react-router-dom";
import { Spinner } from "@/components/ui/spinner";
import { useAppContext } from "@/stores/AppContext";

export function HomeRedirect() {
  const { status, ensureSession } = useAppContext();

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
  return <Navigate to={status === "authenticated" ? "/calendar" : "/login"} replace />;
}
