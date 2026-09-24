import { z } from "zod";

const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;

export function utcToday(): string {
  return new Date().toISOString().slice(0, 10);
}

const dateField = z.string().regex(DATE_PATTERN, "Enter a date as YYYY-MM-DD.");

export const activityCreateSchema = z
  .object({
    title: z
      .string()
      .trim()
      .min(1, "Title is required.")
      .max(100, "Title must be 100 characters or fewer."),
    start_date: dateField.refine((value) => value >= utcToday(), "Start date cannot be before today."),
    activity_type: z.string().min(1, "Please select an activity type."),
    end_date: z.string(),
    details: z.string().max(500, "Details must be 500 characters or fewer."),
    additional_info: z.string().max(500, "Additional info must be 500 characters or fewer."),
  })
  .superRefine((value, ctx) => {
    if (!value.end_date) return;
    if (!DATE_PATTERN.test(value.end_date)) {
      ctx.addIssue({
        code: "custom",
        path: ["end_date"],
        message: "Enter a date as YYYY-MM-DD.",
      });
      return;
    }
    if (value.end_date < value.start_date) {
      ctx.addIssue({
        code: "custom",
        path: ["end_date"],
        message: "End date must be on or after the start date.",
      });
    }
  });

export const activityUpdateSchema = z
  .object({
    title: z.string().trim().max(100, "Title must be 100 characters or fewer.").optional(),
    start_date: z.string().optional(),
    activity_type: z.string().optional(),
    end_date: z.string().optional(),
    details: z.string().max(500, "Details must be 500 characters or fewer.").optional(),
    additional_info: z.string().max(500, "Additional info must be 500 characters or fewer.").optional(),
    updated_at: z.string().optional(),
  })
  .superRefine((value, ctx) => {
    if (value.start_date && !DATE_PATTERN.test(value.start_date)) {
      ctx.addIssue({
        code: "custom",
        path: ["start_date"],
        message: "Enter a date as YYYY-MM-DD.",
      });
    }
    if (value.start_date && DATE_PATTERN.test(value.start_date) && value.start_date < utcToday()) {
      ctx.addIssue({
        code: "custom",
        path: ["start_date"],
        message: "Start date cannot be before today.",
      });
    }
    if (value.end_date && !DATE_PATTERN.test(value.end_date)) {
      ctx.addIssue({
        code: "custom",
        path: ["end_date"],
        message: "Enter a date as YYYY-MM-DD.",
      });
    }
    if (
      value.start_date &&
      value.end_date &&
      DATE_PATTERN.test(value.start_date) &&
      DATE_PATTERN.test(value.end_date) &&
      value.end_date < value.start_date
    ) {
      ctx.addIssue({
        code: "custom",
        path: ["end_date"],
        message: "End date must be on or after the start date.",
      });
    }
  });

export type ActivityCreateInput = z.infer<typeof activityCreateSchema>;
