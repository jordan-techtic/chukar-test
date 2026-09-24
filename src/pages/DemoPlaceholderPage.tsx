import { useQuery } from '@tanstack/react-query';
import { checkHealth } from '@/lib/api/health';
import { getApiErrorMessage } from '@/lib/api/errors';
import { Spinner } from '@/components/ui/spinner';
import { Button } from '@/components/ui/button';

async function fetchHealthWithDelay() {
  const start = Date.now();
  const response = await checkHealth();
  const elapsed = Date.now() - start;
  if (elapsed < 1000) {
    await new Promise((resolve) => setTimeout(resolve, 1000 - elapsed));
  }
  return response;
}

export function DemoPlaceholderPage() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['health-demo'],
    queryFn: fetchHealthWithDelay,
  });

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Spinner label="Loading placeholder data" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="mx-auto max-w-lg rounded-lg border border-border bg-card p-6" role="alert">
        <h1 className="text-xl font-semibold">Demo placeholder</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          {getApiErrorMessage(error, 'Unable to load placeholder data.')}
        </p>
        <Button className="mt-4" onClick={() => void refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg rounded-lg border border-border bg-card p-6">
      <h1 className="text-xl font-semibold">Demo placeholder</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        {data?.message || 'Health check passed.'}
      </p>
    </div>
  );
}
