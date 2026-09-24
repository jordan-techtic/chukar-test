import { createBrowserRouter, Navigate } from "react-router-dom";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AnnualMarketingCalendar } from "@/components/features/calendar/AnnualMarketingCalendar";
import { LoginPage } from "@/components/features/login/LoginPage";
import { AppShell } from "@/components/layout/AppShell";
import { NotFound } from "@/pages/NotFound";
import { ServerError } from "@/pages/ServerError";
import { HomeRedirect } from "@/routes/HomeRedirect";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [{ path: "/calendar", element: <AnnualMarketingCalendar /> }],
      },
    ],
  },
  { path: "/", element: <HomeRedirect /> },
  { path: "/404", element: <NotFound /> },
  { path: "/500", element: <ServerError /> },
  { path: "*", element: <Navigate to="/404" replace /> },
]);
