import { describe, expect, it } from "vitest";
import { activitySchema, utcToday } from "@/lib/validation/activity";

const valid = {
  title: "Summer email",
  start_date: "2099-06-01",
  end_date: "",
  activity_type: "email_send",
  details: "",
  additional_info: "",
};

describe("activity validation", () => {
  it("accepts a complete activity", () => {
    expect(activitySchema.safeParse(valid).success).toBe(true);
  });

  it("requires a title", () => {
    expect(activitySchema.safeParse({ ...valid, title: " " }).success).toBe(false);
  });

  it("rejects a past start date", () => {
    const result = activitySchema.safeParse({ ...valid, start_date: "2000-01-01" });
    expect(result.success).toBe(false);
  });

  it("rejects an end date before the start date", () => {
    const result = activitySchema.safeParse({
      ...valid,
      start_date: "2099-06-10",
      end_date: "2099-06-01",
    });
    expect(result.success).toBe(false);
  });

  it("uses a UTC today stamp", () => {
    expect(utcToday()).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
});
