import type { UseFormReturn } from "react-hook-form";
import { DatePicker } from "@/components/ui/date-picker";
import { FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import type { ActivityFormValues } from "@/lib/validation/activity";
import type { ActivityTypeOption } from "@/types/api";

export function ActivityFields({
  form,
  activityTypes,
  disabled,
}: {
  form: UseFormReturn<ActivityFormValues>;
  activityTypes: ActivityTypeOption[];
  disabled?: boolean;
}) {
  const selected = activityTypes.find((option) => option.value === form.watch("activity_type"));
  const extraFields = selected?.fields ?? [];

  return (
    <div className="space-y-4">
      <FormField
        control={form.control}
        name="title"
        render={({ field }) => (
          <FormItem>
            <FormLabel htmlFor="activity-title">Title</FormLabel>
            <FormControl>
              <Input {...field} id="activity-title" maxLength={100} disabled={disabled} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="start_date"
        render={({ field }) => (
          <FormItem>
            <FormLabel htmlFor="activity-start-date">Start date</FormLabel>
            <FormControl>
              <DatePicker
                id="activity-start-date"
                value={field.value}
                onChange={field.onChange}
                disabled={disabled}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="end_date"
        render={({ field }) => (
          <FormItem>
            <FormLabel htmlFor="activity-end-date">End date</FormLabel>
            <FormControl>
              <DatePicker
                id="activity-end-date"
                value={field.value}
                onChange={field.onChange}
                disabled={disabled}
                placeholder="Optional"
              />
            </FormControl>
            <FormDescription>Defaults to the start date.</FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="activity_type"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Activity type</FormLabel>
            <Select
              value={field.value || undefined}
              onValueChange={field.onChange}
              disabled={disabled || activityTypes.length === 0}
            >
              <FormControl>
                <SelectTrigger aria-label="Activity type">
                  <SelectValue
                    placeholder={
                      activityTypes.length === 0
                        ? "No activity types are available."
                        : "Select an activity type"
                    }
                  />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {activityTypes.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {activityTypes.length === 0 ? (
              <p className="text-sm text-muted-foreground">No activity types are available.</p>
            ) : null}
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="details"
        render={({ field }) => (
          <FormItem>
            <FormLabel htmlFor="activity-details">Details</FormLabel>
            <FormControl>
              <Textarea {...field} id="activity-details" maxLength={500} disabled={disabled} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      {extraFields.map((extra) => (
        <FormField
          key={extra.name}
          control={form.control}
          name="additional_info"
          render={({ field }) => (
            <FormItem>
              <FormLabel htmlFor={`activity-${extra.name}`}>
                {extra.label}
                {extra.required ? " *" : ""}
              </FormLabel>
              <FormControl>
                <Input
                  {...field}
                  id={`activity-${extra.name}`}
                  name={extra.name}
                  maxLength={extra.max_length}
                  disabled={disabled}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      ))}
    </div>
  );
}
