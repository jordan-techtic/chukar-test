import { Outlet } from "react-router-dom";
import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";

export function AppShell() {
  return (
    <div className="min-h-svh bg-background lg:grid lg:grid-cols-[15rem_minmax(0,1fr)] lg:grid-rows-[4rem_minmax(0,1fr)]">
      <div className="lg:col-start-2 lg:row-start-1">
        <Header />
      </div>
      <div className="lg:col-start-1 lg:row-start-1 lg:row-span-2">
        <Sidebar />
      </div>
      <main className="min-w-0 p-4 md:p-6 lg:col-start-2 lg:row-start-2">
        <Outlet />
      </main>
    </div>
  );
}
