import type { ReactNode } from "react";

export function EmptyState({
  title,
  description,
}: {
  title: string;
  description?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center gap-1 px-4 py-10 text-center">
      <p className="text-sm font-medium text-foreground">{title}</p>
      {description ? <p className="text-sm text-muted-foreground">{description}</p> : null}
    </div>
  );
}
