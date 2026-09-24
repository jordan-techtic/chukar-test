import { Button } from "@/components/ui/button";

export function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div role="alert" className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-destructive/30 bg-card px-4 py-3">
      <p className="text-sm text-destructive">{message}</p>
      <Button type="button" variant="outline" onClick={onRetry}>
        Try again
      </Button>
    </div>
  );
}

export function ForbiddenState() {
  return (
    <div role="alert" className="rounded-lg border border-border bg-card px-4 py-6 text-sm text-foreground">
      You do not have access to the marketing calendar.
    </div>
  );
}
