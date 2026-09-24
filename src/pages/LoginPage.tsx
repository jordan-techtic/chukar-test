import { Navigate } from 'react-router-dom';
import { useAppContext } from '@/stores/AppContext';
import { Spinner } from '@/components/ui/spinner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LoginForm } from '@/components/features/auth/LoginForm';

export function LoginPage() {
  const { status } = useAppContext();

  if (status === 'checking') {
    return (
      <div className="flex min-h-svh items-center justify-center bg-background">
        <Spinner label="Loading session" />
      </div>
    );
  }

  if (status === 'authenticated') {
    return <Navigate to="/calendar" replace />;
  }

  return (
    <div className="flex min-h-svh items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="items-center text-center">
          <img
            src="/brand-logo.png"
            alt="Brand logo"
            className="mb-4 h-12 w-auto object-contain"
          />
          <CardTitle>Marketing Content Calendar</CardTitle>
        </CardHeader>
        <CardContent>
          <LoginForm />
        </CardContent>
      </Card>
    </div>
  );
}
