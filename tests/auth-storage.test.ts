import { beforeEach, describe, expect, it } from "vitest";
import {
  ACCESS_TOKEN_KEY,
  AUTH_USER_KEY,
  SESSION_REJECTED_KEY,
  SESSION_VALIDATED_KEY,
  clearSession,
  getAccessToken,
  getAuthUser,
  isSessionValidated,
  persistSession,
  purgeRejectedSession,
  rejectSession,
} from "@/lib/auth/storage";

const user = {
  id: "user-1",
  email: "ada@example.com",
  username: "ada",
  role: "admin",
};

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
});

describe("auth storage", () => {
  it("persists the access token and user after login", () => {
    persistSession("token-1", user);
    expect(getAccessToken()).toBe("token-1");
    expect(getAuthUser()).toEqual(user);
    expect(isSessionValidated()).toBe(true);
  });

  it("clears the session on logout", () => {
    persistSession("token-1", user);
    clearSession();
    expect(localStorage.getItem(ACCESS_TOKEN_KEY)).toBeNull();
    expect(localStorage.getItem(AUTH_USER_KEY)).toBeNull();
    expect(sessionStorage.getItem(SESSION_VALIDATED_KEY)).toBeNull();
    expect(isSessionValidated()).toBe(false);
  });

  it("rejects a dead session so a reload cannot restore the token", () => {
    persistSession("token-1", user);
    rejectSession();
    expect(sessionStorage.getItem(SESSION_REJECTED_KEY)).toBe("true");
    localStorage.setItem(ACCESS_TOKEN_KEY, "token-1");
    purgeRejectedSession();
    expect(localStorage.getItem(ACCESS_TOKEN_KEY)).toBeNull();
    expect(isSessionValidated()).toBe(false);
  });
});
