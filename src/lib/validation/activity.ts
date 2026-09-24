import { z } from "zod";

export function utcToday(): string {
  return new Date().toISOString().slice(0, 10);
}

export const activitySchema = z
  .object({
    title: z
      .string()
      .trim()
      .min(1, "Title is required.")
      .max(100, "Title must be 100 characters or fewer."),
    start_date: z.string().min(1, "Start date is required."),
    end_date: z.string(),
    activity_type: z.string().min(1, "Please select an activity type."),
    details: z.string().max(500, "Details must be 500 characters or fewer."),
    additional_info: z.string().max(500, "Additional info must be 500 characters or fewer."),
  })
  .superRefine((value, ctx) => {
    if (value.start_date && value.start_date < utcToday()) {
      ctx.addIssue({
        code: "custom",
        path: ["start_date"],
        message: "Start date cannot be in the past.",
      });
    }
    if (value.end_date && value.start_date && value.end_date < value.start_date) {
      ctx.addIssue({
        code: "custom",
        path: ["end_date"],
        message: "End date must be on or after the start date.",
      });
    }
  });

export type ActivityFormValues = z.infer<typeof activitySchema>;

export const emptyActivityForm: ActivityFormValues = {
  title: "",
  start_date: "",
  end_date: "",
  activity_type: "",
  details: "",
  additional_info: "",
};
