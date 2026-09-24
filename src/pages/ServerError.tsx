import { Button } from "@/components/ui/button";

export function ServerError({ onRetry }: { onRetry?: () => void }) {
  return (
    <main className="flex min-h-svh flex-col items-center justify-center gap-4 bg-background px-4 text-center">
      <h1 className="text-[28px] font-semibold leading-9 text-foreground">500 Server Error</h1>
      <p className="text-sm text-muted-foreground">Something went wrong.</p>
      <Button type="button" onClick={() => onRetry?.()}>
        Try again
      </Button>
    </main>
  );
}
