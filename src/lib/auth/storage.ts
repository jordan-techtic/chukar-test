import type { AuthUser } from "@/types/api";

const ACCESS_TOKEN_KEY = "access_token";
const AUTH_USER_KEY = "auth_user";
const SESSION_REJECTED_KEY = "session_rejected";

export function readAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function readAuthUser(): AuthUser | null {
  const raw = localStorage.getItem(AUTH_USER_KEY);
  if (!raw) return null;
  try {
    const parsed: unknown = JSON.parse(raw);
    if (!isAuthUser(parsed)) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function isSessionRejected(): boolean {
  return sessionStorage.getItem(SESSION_REJECTED_KEY) === "1";
}

export function persistSession(token: string, user: AuthUser): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, token);
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
  sessionStorage.removeItem(SESSION_REJECTED_KEY);
}

export function clearSession(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
}

export function rejectSession(): void {
  clearSession();
  sessionStorage.setItem(SESSION_REJECTED_KEY, "1");
}

function isAuthUser(value: unknown): value is AuthUser {
  if (!value || typeof value !== "object") return false;
  const record = value as Record<string, unknown>;
  return (
    typeof record.id === "string" &&
    typeof record.email === "string" &&
    typeof record.username === "string" &&
    typeof record.role === "string"
  );
}
