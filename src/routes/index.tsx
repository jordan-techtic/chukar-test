import { createBrowserRouter, Navigate } from "react-router-dom";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";
import { CalendarPage } from "@/pages/CalendarPage";
import { HomeRedirect } from "@/pages/HomeRedirect";
import { LoginPage } from "@/pages/LoginPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { ServerErrorPage } from "@/pages/ServerErrorPage";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  { path: "/", element: <HomeRedirect /> },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [{ path: "/calendar", element: <CalendarPage /> }],
      },
    ],
  },
  { path: "/404", element: <NotFoundPage /> },
  { path: "/500", element: <ServerErrorPage /> },
  { path: "*", element: <Navigate to="/404" replace /> },
]);
