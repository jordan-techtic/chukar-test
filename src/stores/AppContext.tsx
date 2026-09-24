/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { getCalendar } from "@/lib/api/calendar";
import {
  clearSession,
  isSessionRejected,
  persistSession,
  readAccessToken,
  readAuthUser,
  rejectSession,
} from "@/lib/auth/storage";
import { getApiErrorCode } from "@/lib/api/errors";
import axios from "axios";
import type { AuthUser } from "@/types/api";

export type AuthStatus = "checking" | "anonymous" | "authenticated";

interface AppContextValue {
  status: AuthStatus;
  user: AuthUser | null;
  setSession: (token: string, user: AuthUser) => void;
  logout: () => void;
  ensureSession: () => void;
}

const AppContext = createContext<AppContextValue | undefined>(undefined);

function initialStatus(): AuthStatus {
  if (isSessionRejected() || !readAccessToken() || !readAuthUser()) return "anonymous";
  return "checking";
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>(initialStatus);
  const [user, setUser] = useState<AuthUser | null>(() =>
    initialStatus() === "anonymous" ? null : readAuthUser(),
  );
  const validation = useRef<"idle" | "running">("idle");

  useEffect(() => {
    const onUnauthorized = () => {
      setUser(null);
      setStatus("anonymous");
    };
    window.addEventListener("auth:unauthorized", onUnauthorized);
    return () => window.removeEventListener("auth:unauthorized", onUnauthorized);
  }, []);

  const ensureSession = useCallback(() => {
    if (status !== "checking" || validation.current === "running") return;
    validation.current = "running";
    getCalendar({ year: new Date().getFullYear() })
      .then(() => {
        setUser(readAuthUser());
        setStatus("authenticated");
      })
      .catch((error: unknown) => {
        const code = getApiErrorCode(error);
        const httpStatus = axios.isAxiosError(error) ? error.response?.status : undefined;
        if (httpStatus === 401 || code === "UNAUTHORIZED" || code === "INVALID_TOKEN") {
          rejectSession();
          setUser(null);
          setStatus("anonymous");
          return;
        }
        setUser(readAuthUser());
        setStatus("authenticated");
      });
  }, [status]);

  const value = useMemo<AppContextValue>(
    () => ({
      status,
      user,
      setSession: (token, nextUser) => {
        persistSession(token, nextUser);
        setUser(nextUser);
        setStatus("authenticated");
      },
      logout: () => {
        clearSession();
        setUser(null);
        setStatus("anonymous");
      },
      ensureSession,
    }),
    [status, user, ensureSession],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext(): AppContextValue {
  const value = useContext(AppContext);
  if (!value) {
    throw new Error("useAppContext must be used within AppProvider");
  }
  return value;
}
