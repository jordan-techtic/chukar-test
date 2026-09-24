import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { AuthUser } from "@/types/api";
import {
  clearSession,
  getAccessToken,
  getAuthUser,
  isSessionValidated,
  persistSession,
  purgeRejectedSession,
} from "@/lib/auth/storage";

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  ready: boolean;
  authenticated: boolean;
  login: (token: string, user: AuthUser) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    purgeRejectedSession();
    return isSessionValidated() ? getAuthUser() : null;
  });
  const [token, setToken] = useState<string | null>(() =>
    isSessionValidated() ? getAccessToken() : null,
  );
  const ready = true;

  useEffect(() => {
    const onUnauthorized = () => {
      setToken(null);
      setUser(null);
    };
    window.addEventListener("auth:unauthorized", onUnauthorized);
    return () => window.removeEventListener("auth:unauthorized", onUnauthorized);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      ready,
      authenticated: Boolean(ready && token && user),
      login: (nextToken, nextUser) => {
        persistSession(nextToken, nextUser);
        setToken(nextToken);
        setUser(nextUser);
      },
      logout: () => {
        clearSession();
        setToken(null);
        setUser(null);
        window.location.replace("/login");
      },
    }),
    [ready, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used within AuthProvider.");
  }
  return value;
}
