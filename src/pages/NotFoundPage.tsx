import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex min-h-svh items-center justify-center bg-background p-6">
      <div className="max-w-md">
        <h1 className="text-[28px] leading-9 font-semibold">404 — Page not found</h1>
        <p className="mt-2 text-muted-foreground">The page you are looking for does not exist.</p>
        <Link
          to="/"
          className="mt-4 inline-flex text-sm font-semibold text-primary underline-offset-4 hover:underline focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
        >
          Go home
        </Link>
      </div>
    </div>
  );
}
