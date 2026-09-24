import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAppContext } from '@/stores/AppContext';
import { Spinner } from '@/components/ui/spinner';

export function ProtectedRoute() {
  const { status } = useAppContext();
  const location = useLocation();

  if (status === 'checking') {
    return (
      <div className="flex min-h-svh items-center justify-center bg-background">
        <Spinner label="Loading session" />
      </div>
    );
  }

  if (status === 'unauthenticated') {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}
