import { z } from "zod";

export const loginSchema = z.object({
  email_or_username: z
    .string()
    .trim()
    .min(1, "Email or username is required.")
    .max(255, "Email or username must be 255 characters or fewer."),
  password: z
    .string()
    .min(1, "Password is required.")
    .max(128, "Password must be 128 characters or fewer."),
});

export type LoginFormValues = z.infer<typeof loginSchema>;

export const recoverySchema = z.object({
  email: z.string().trim().min(1, "Email is required.").email("Please enter a valid email address."),
});

export type RecoveryFormValues = z.infer<typeof recoverySchema>;
