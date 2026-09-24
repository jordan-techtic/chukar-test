import { describe, expect, it } from "vitest";
import { activityCreateSchema } from "@/features/calendar/activity-schema";

describe("activityCreateSchema", () => {
  it("accepts a future activity", () => {
    const parsed = activityCreateSchema.safeParse({
      title: "Summer email",
      start_date: "2099-06-01",
      activity_type: "email_send",
      end_date: "2099-06-02",
      details: "Launch copy",
      additional_info: "Audience: all",
    });
    expect(parsed.success).toBe(true);
  });

  it("rejects an empty title", () => {
    const parsed = activityCreateSchema.safeParse({
      title: " ",
      start_date: "2099-06-01",
      activity_type: "email_send",
      end_date: "",
      details: "",
      additional_info: "",
    });
    expect(parsed.success).toBe(false);
  });

  it("rejects a start date before today", () => {
    const parsed = activityCreateSchema.safeParse({
      title: "Past post",
      start_date: "2000-01-01",
      activity_type: "blog_post",
      end_date: "",
      details: "",
      additional_info: "",
    });
    expect(parsed.success).toBe(false);
  });

  it("rejects an end date before the start date", () => {
    const parsed = activityCreateSchema.safeParse({
      title: "Range",
      start_date: "2099-06-10",
      activity_type: "social_post",
      end_date: "2099-06-01",
      details: "",
      additional_info: "",
    });
    expect(parsed.success).toBe(false);
  });
});
