import { Navigate } from 'react-router-dom';
import { useAppContext } from '@/stores/AppContext';
import { Spinner } from '@/components/ui/spinner';

export function RootRedirectPage() {
  const { status } = useAppContext();

  if (status === 'checking') {
    return (
      <div className="flex min-h-svh items-center justify-center bg-background">
        <Spinner label="Loading session" />
      </div>
    );
  }

  return <Navigate to={status === 'authenticated' ? '/calendar' : '/login'} replace />;
}
