import { describe, expect, it } from "vitest";
import { resolveApiOrigin } from "@/lib/api/client";

describe("resolveApiOrigin", () => {
  it("strips a trailing /api from the configured base URL", () => {
    expect(resolveApiOrigin("http://174.138.72.184:8989/api")).toBe(
      "http://174.138.72.184:8989",
    );
  });

  it("strips a trailing slash after /api", () => {
    expect(resolveApiOrigin("http://174.138.72.184:8989/api/")).toBe(
      "http://174.138.72.184:8989",
    );
  });

  it("leaves an origin without /api unchanged", () => {
    expect(resolveApiOrigin("http://174.138.72.184:8989")).toBe("http://174.138.72.184:8989");
  });
});
