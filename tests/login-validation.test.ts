import { describe, expect, it } from "vitest";
import { loginSchema, recoverySchema } from "@/lib/validation/login";

describe("login validation", () => {
  it("requires both fields", () => {
    const result = loginSchema.safeParse({ email_or_username: "", password: "" });
    expect(result.success).toBe(false);
  });

  it("accepts a username and password", () => {
    const result = loginSchema.safeParse({ email_or_username: "alex", password: "secret" });
    expect(result.success).toBe(true);
  });

  it("rejects a password longer than 128 characters", () => {
    const result = loginSchema.safeParse({
      email_or_username: "alex",
      password: "a".repeat(129),
    });
    expect(result.success).toBe(false);
  });

  it("requires a valid recovery email", () => {
    expect(recoverySchema.safeParse({ email: "not-an-email" }).success).toBe(false);
    expect(recoverySchema.safeParse({ email: "alex@example.com" }).success).toBe(true);
  });
});
