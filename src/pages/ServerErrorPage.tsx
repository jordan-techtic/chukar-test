import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

export function ServerErrorPage() {
  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-4 bg-background p-6 text-center">
      <h1 className="text-2xl font-semibold">500 — Server error</h1>
      <p className="text-muted-foreground">Something went wrong on our end. Please try again later.</p>
      <Button asChild>
        <Link to="/">Go home</Link>
      </Button>
    </div>
  );
}
