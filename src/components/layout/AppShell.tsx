import { Outlet } from "react-router-dom";
import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";

export function AppShell() {
  return (
    <div className="flex h-svh flex-col bg-background xl:flex-row">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-card focus:px-3 focus:py-2 focus:ring-2 focus:ring-ring"
      >
        Skip to calendar
      </a>
      <Sidebar className="hidden w-60 shrink-0 border-r xl:flex" />
      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        <div className="border-b border-border bg-card xl:hidden">
          <Sidebar className="flex-row items-center justify-between border-0 py-3" />
        </div>
        <Header />
        <main id="main" className="min-h-0 flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
