import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import type { AuthUser } from '@/types/api';
import {
  AUTH_TOKEN_KEY,
  AUTH_USER_KEY,
  SESSION_REJECTED_KEY,
} from '@/lib/api/client';
import { UNAUTHORIZED_EVENT } from '@/lib/api/interceptors';

export type AuthStatus = 'checking' | 'authenticated' | 'unauthenticated';

interface AppContextValue {
  status: AuthStatus;
  user: AuthUser | null;
  setSession: (token: string, user: AuthUser) => void;
  logout: () => void;
}

const AppContext = createContext<AppContextValue | null>(null);

function readStoredUser(): AuthUser | null {
  const raw = localStorage.getItem(AUTH_USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

function getInitialAuthState(): { status: AuthStatus; user: AuthUser | null } {
  const rejected = sessionStorage.getItem(SESSION_REJECTED_KEY) === 'true';
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  const storedUser = readStoredUser();

  if (rejected || !token || !storedUser) {
    if (token || storedUser) {
      localStorage.removeItem(AUTH_TOKEN_KEY);
      localStorage.removeItem(AUTH_USER_KEY);
    }
    return { status: 'unauthenticated', user: null };
  }

  return { status: 'authenticated', user: storedUser };
}

export function AppProvider({ children }: { children: ReactNode }) {
  const initialAuth = getInitialAuthState();
  const [status, setStatus] = useState<AuthStatus>(initialAuth.status);
  const [user, setUser] = useState<AuthUser | null>(initialAuth.user);

  const clearSession = useCallback(() => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    setUser(null);
    setStatus('unauthenticated');
  }, []);

  const setSession = useCallback((token: string, authUser: AuthUser) => {
    sessionStorage.removeItem(SESSION_REJECTED_KEY);
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(authUser));
    setUser(authUser);
    setStatus('authenticated');
  }, []);

  const logout = useCallback(() => {
    sessionStorage.setItem(SESSION_REJECTED_KEY, 'true');
    clearSession();
  }, [clearSession]);

  useEffect(() => {
    const handleUnauthorized = () => {
      clearSession();
    };
    window.addEventListener(UNAUTHORIZED_EVENT, handleUnauthorized);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, handleUnauthorized);
  }, [clearSession]);

  const value = useMemo(
    () => ({ status, user, setSession, logout }),
    [status, user, setSession, logout],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext(): AppContextValue {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
}
