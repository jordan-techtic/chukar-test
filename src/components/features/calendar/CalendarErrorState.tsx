import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface CalendarErrorStateProps {
  message?: string;
  onRetry: () => void;
}

export function CalendarErrorState({
  message = 'Unable to load calendar. Please try again.',
  onRetry,
}: CalendarErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center" role="alert">
      <AlertCircle className="mb-4 size-10 text-destructive" aria-hidden="true" />
      <h2 className="text-lg font-semibold">Something went wrong</h2>
      <p className="mt-1 max-w-sm text-sm text-muted-foreground">{message}</p>
      <Button className="mt-4" onClick={onRetry}>
        Retry
      </Button>
    </div>
  );
}
