import { z } from 'zod';

export const activityFormSchema = z
  .object({
    title: z.string().min(1, 'Title is required.').max(100, 'Title must be 100 characters or fewer.'),
    start_date: z.string().min(1, 'Start date is required.'),
    end_date: z.string().optional(),
    activity_type: z.string().min(1, 'Activity type is required.'),
    details: z.string().max(500, 'Details must be 500 characters or fewer.').optional(),
    additional_info: z.string().max(500, 'Additional info must be 500 characters or fewer.').optional(),
  })
  .refine(
    (data) => {
      if (!data.end_date) return true;
      return data.end_date >= data.start_date;
    },
    {
      message: 'End date must be on or after start date.',
      path: ['end_date'],
    },
  );

export type ActivityFormValues = z.infer<typeof activityFormSchema>;
