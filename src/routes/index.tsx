import { createBrowserRouter, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { AppShell } from '@/components/layout/AppShell';
import { RootRedirectPage } from '@/pages/RootRedirectPage';
import { LoginPage } from '@/pages/LoginPage';
import { AnnualMarketingCalendarPage } from '@/pages/AnnualMarketingCalendarPage';
import { DemoPlaceholderPage } from '@/pages/DemoPlaceholderPage';
import { NotFoundPage } from '@/pages/NotFoundPage';
import { ServerErrorPage } from '@/pages/ServerErrorPage';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <RootRedirectPage />,
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          {
            path: '/calendar',
            element: <AnnualMarketingCalendarPage />,
          },
          {
            path: '/demo',
            element: <DemoPlaceholderPage />,
          },
        ],
      },
    ],
  },
  {
    path: '/404',
    element: <NotFoundPage />,
  },
  {
    path: '/500',
    element: <ServerErrorPage />,
  },
  {
    path: '*',
    element: <Navigate to="/404" replace />,
  },
]);
