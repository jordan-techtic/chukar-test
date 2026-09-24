import { Component, type ErrorInfo, type ReactNode } from "react";
import { Button } from "@/components/ui/button";

type ErrorBoundaryProps = {
  children: ReactNode;
};

type ErrorBoundaryState = {
  hasError: boolean;
};

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error(error.message, info.componentStack);
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <div className="flex min-h-svh items-center justify-center bg-background p-6">
        <div className="max-w-md rounded-md border border-border bg-card p-6">
          <h1 className="text-lg font-semibold">Something went wrong.</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            An unexpected error stopped this page. You can try again or open the server error page.
          </p>
          <div className="mt-4 flex gap-2">
            <Button type="button" onClick={() => this.setState({ hasError: false })}>
              Try again
            </Button>
            <a
              href="/500"
              className="inline-flex h-11 items-center rounded-md px-4 text-sm font-semibold text-primary underline-offset-4 hover:underline focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none md:h-10"
            >
              Server error
            </a>
          </div>
        </div>
      </div>
    );
  }
}
