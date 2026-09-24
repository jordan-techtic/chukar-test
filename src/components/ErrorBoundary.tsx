import { Component, type ErrorInfo, type ReactNode } from "react";
import { ServerError } from "@/pages/ServerError";

interface State {
  error: Error | null;
}

export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error(error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return <ServerError onRetry={() => this.setState({ error: null })} />;
    }
    return this.props.children;
  }
}
