import type { AuthUser } from "@/types/api";

export const ACCESS_TOKEN_KEY = "access_token";
export const AUTH_USER_KEY = "auth_user";
export const SESSION_REJECTED_KEY = "session_rejected";
export const SESSION_VALIDATED_KEY = "session_validated";

export function isAuthUser(value: unknown): value is AuthUser {
  if (!value || typeof value !== "object") return false;
  const record = value as Record<string, unknown>;
  return (
    typeof record.id === "string" &&
    typeof record.email === "string" &&
    typeof record.username === "string" &&
    typeof record.role === "string"
  );
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getAuthUser(): AuthUser | null {
  const raw = localStorage.getItem(AUTH_USER_KEY);
  if (!raw) return null;
  try {
    const parsed: unknown = JSON.parse(raw);
    return isAuthUser(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

export function isSessionValidated(): boolean {
  return (
    sessionStorage.getItem(SESSION_VALIDATED_KEY) === "true" &&
    sessionStorage.getItem(SESSION_REJECTED_KEY) !== "true" &&
    Boolean(getAccessToken())
  );
}

export function persistSession(token: string, user: AuthUser): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, token);
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
  sessionStorage.setItem(SESSION_VALIDATED_KEY, "true");
  sessionStorage.removeItem(SESSION_REJECTED_KEY);
}

export function clearSession(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
  sessionStorage.removeItem(SESSION_VALIDATED_KEY);
}

export function rejectSession(): void {
  clearSession();
  sessionStorage.setItem(SESSION_REJECTED_KEY, "true");
}

export function purgeRejectedSession(): void {
  if (sessionStorage.getItem(SESSION_REJECTED_KEY) === "true") {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    sessionStorage.removeItem(SESSION_VALIDATED_KEY);
  }
}
