import type { ReactNode } from "react";

export function PageHeader({ title, description }: { title: string; description: string }) {
  return (
    <header className="space-y-1">
      <h1 className="text-[28px] font-semibold leading-9 tracking-normal text-foreground">{title}</h1>
      <p className="text-sm text-muted-foreground">{description}</p>
    </header>
  );
}

export function ErrorMessage({ children }: { children: ReactNode }) {
  return (
    <p role="alert" className="rounded-md border border-destructive/30 bg-card px-3 py-2 text-sm text-destructive">
      {children}
    </p>
  );
}
