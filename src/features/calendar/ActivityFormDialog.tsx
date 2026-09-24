import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { CalendarIcon, Copy } from "lucide-react";
import { useForm, useWatch, type FieldPath, type UseFormSetError } from "react-hook-form";
import { toast } from "@/components/ui/toast";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Calendar } from "@/components/ui/calendar";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { Spinner } from "@/components/ui/spinner";
import { getApiErrorMessage, getErrorCode, getErrorDetails } from "@/lib/api/errors";
import { humanizeEnum } from "@/lib/utils";
import { activityCreateSchema, activityUpdateSchema } from "@/features/calendar/activity-schema";
import { formatISODate, parseISODate } from "@/features/calendar/dates";
import { useActivity } from "@/features/calendar/use-activity";
import {
  useCreateActivity,
  useDeleteActivity,
  useUpdateActivity,
} from "@/features/calendar/use-activity-mutations";
import type { ActivityStatus, ActivityTypeOption } from "@/types/api";

type FormValues = {
  title: string;
  start_date: string;
  end_date: string;
  activity_type: string;
  details: string;
  status: ActivityStatus;
  extra: Record<string, string>;
};

const EMPTY: FormValues = {
  title: "",
  start_date: "",
  end_date: "",
  activity_type: "",
  details: "",
  status: "pending",
  extra: {},
};

const FIELD_MAP: Record<string, FieldPath<FormValues>> = {
  title: "title",
  start_date: "start_date",
  activity_date: "start_date",
  date: "start_date",
  end_date: "end_date",
  activity_type: "activity_type",
  type: "activity_type",
  details: "details",
  notes: "details",
  description: "details",
  additional_info: "extra.additional_info",
  status: "status",
};

function applyServerErrors(error: unknown, setError: UseFormSetError<FormValues>) {
  for (const detail of getErrorDetails(error)) {
    const path = FIELD_MAP[detail.field];
    if (path) setError(path, { message: detail.message });
  }
}

export function ActivityFormDialog({
  open,
  activityId,
  activityTypes,
  onOpenChange,
}: {
  open: boolean;
  activityId: string | null;
  activityTypes: ActivityTypeOption[];
  onOpenChange: (open: boolean) => void;
}) {
  const queryClient = useQueryClient();
  const editing = Boolean(activityId);
  const activityQuery = useActivity(activityId, open && editing);
  const createActivity = useCreateActivity();
  const updateActivity = useUpdateActivity(activityId ?? "new");
  const deleteActivity = useDeleteActivity(activityId ?? "new");
  const [confirmDelete, setConfirmDelete] = useState(false);
  const form = useForm<FormValues>({ defaultValues: EMPTY });
  const pending = createActivity.isPending || updateActivity.isPending || deleteActivity.isPending;
  const activityTypeValue = useWatch({ control: form.control, name: "activity_type" });
  const selectedType = activityTypes.find((option) => option.value === activityTypeValue);
  const activity = activityQuery.data?.data;

  useEffect(() => {
    if (!open) return;
    if (!activityId) {
      form.reset(EMPTY);
      return;
    }
    if (!activity) return;
    form.reset({
      title: activity.title,
      start_date: activity.start_date,
      end_date: activity.end_date === activity.start_date ? "" : activity.end_date,
      activity_type: activity.activity_type,
      details: activity.details ?? activity.notes ?? activity.description ?? "",
      status: activity.status,
      extra: { additional_info: activity.additional_info ?? "" },
    });
  }, [activity, activityId, form, open]);

  async function copyCampaignCode() {
    if (!activity?.campaign_code) return;
    try {
      await navigator.clipboard.writeText(activity.campaign_code);
      toast.success("Campaign code copied.");
    } catch {
      toast.error("Unable to copy the campaign code.");
    }
  }

  async function onSubmit(values: FormValues) {
    form.clearErrors();
    const option = activityTypes.find((item) => item.value === values.activity_type);
    let invalid = false;
    for (const field of option?.fields ?? []) {
      const current = values.extra[field.name] ?? "";
      const path = `extra.${field.name}` as FieldPath<FormValues>;
      if (field.required && current.trim().length === 0) {
        form.setError(path, { message: `${field.label} is required.` });
        invalid = true;
      } else if (current.length > field.max_length) {
        form.setError(path, {
          message: `${field.label} must be ${field.max_length} characters or fewer.`,
        });
        invalid = true;
      }
    }

    const additionalInfo = values.extra.additional_info ?? "";
    if (editing) {
      const parsed = activityUpdateSchema.safeParse({
        title: values.title,
        start_date: values.start_date,
        end_date: values.end_date,
        activity_type: values.activity_type,
        details: values.details,
        additional_info: additionalInfo,
        updated_at: activity?.updated_at,
      });
      if (!parsed.success) {
        for (const issue of parsed.error.issues) {
          const key = String(issue.path[0] ?? "");
          const path = key === "additional_info" ? "extra.additional_info" : FIELD_MAP[key];
          if (path) form.setError(path, { message: issue.message });
        }
        return;
      }
      if (invalid || !activityId) return;
      try {
        const result = await updateActivity.mutateAsync({
          title: values.title.trim(),
          start_date: values.start_date,
          end_date: values.end_date || values.start_date,
          activity_type: values.activity_type,
          details: values.details.trim() || null,
          additional_info: additionalInfo.trim() || null,
          category: option?.category ?? null,
          status: values.status,
          updated_at: activity?.updated_at ?? null,
        });
        toast.success(result.message);
        onOpenChange(false);
      } catch (error) {
        toast.error(getApiErrorMessage(error));
        applyServerErrors(error, form.setError);
        if (getErrorCode(error) === "STALE_UPDATE") {
          await queryClient.invalidateQueries({ queryKey: ["activity", activityId] });
        }
      }
      return;
    }

    const parsed = activityCreateSchema.safeParse({
      title: values.title,
      start_date: values.start_date,
      activity_type: values.activity_type,
      end_date: values.end_date,
      details: values.details,
      additional_info: additionalInfo,
    });
    if (!parsed.success) {
      for (const issue of parsed.error.issues) {
        const key = String(issue.path[0] ?? "");
        const path = key === "additional_info" ? "extra.additional_info" : FIELD_MAP[key];
        if (path) form.setError(path, { message: issue.message });
      }
      return;
    }
    if (invalid) return;
    try {
      const result = await createActivity.mutateAsync({
        title: parsed.data.title,
        start_date: parsed.data.start_date,
        activity_type: parsed.data.activity_type,
        end_date: parsed.data.end_date || null,
        details: parsed.data.details.trim() || null,
        additional_info: parsed.data.additional_info.trim() || null,
        category: option?.category ?? null,
      });
      toast.success(result.message);
      onOpenChange(false);
    } catch (error) {
      toast.error(getApiErrorMessage(error));
      applyServerErrors(error, form.setError);
    }
  }

  async function onDelete() {
    if (!activityId) return;
    try {
      const result = await deleteActivity.mutateAsync();
      toast.success(result.message);
      setConfirmDelete(false);
      onOpenChange(false);
    } catch (error) {
      toast.error(getApiErrorMessage(error));
    }
  }

  return (
    <>
      <Dialog
        open={open}
        onOpenChange={(next) => {
          if (pending) return;
          onOpenChange(next);
        }}
      >
        <DialogContent
          onEscapeKeyDown={(event) => {
            if (pending) event.preventDefault();
          }}
          onInteractOutside={(event) => {
            if (pending) event.preventDefault();
          }}
        >
          <DialogHeader>
            <DialogTitle>{editing ? "Edit activity" : "Create activity"}</DialogTitle>
            <DialogDescription>
              {editing
                ? "Update the activity details. Saving a published activity returns it to pending."
                : "Add a marketing activity to the calendar."}
            </DialogDescription>
          </DialogHeader>
          {editing && activityQuery.isLoading ? (
            <Spinner label="Loading activity" />
          ) : (
            <Form {...form}>
              <form className="grid gap-4" onSubmit={form.handleSubmit(onSubmit)} noValidate>
                <FormField
                  control={form.control}
                  name="activity_type"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Activity type</FormLabel>
                      <Select
                        value={field.value || undefined}
                        onValueChange={field.onChange}
                        disabled={pending}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select an activity type" />
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
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="title"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Title</FormLabel>
                      <FormControl>
                        <Input {...field} disabled={pending} maxLength={100} />
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
                      <FormLabel>Start date</FormLabel>
                      <DateControl
                        id="start-date"
                        value={field.value}
                        disabled={pending}
                        onChange={field.onChange}
                      />
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="end_date"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>End date</FormLabel>
                      <DateControl
                        id="end-date"
                        value={field.value}
                        disabled={pending}
                        onChange={field.onChange}
                      />
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="details"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Details</FormLabel>
                      <FormControl>
                        <Textarea {...field} disabled={pending} maxLength={500} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                {(selectedType?.fields ?? []).map((field) => (
                  <FormField
                    key={field.name}
                    control={form.control}
                    name={`extra.${field.name}` as FieldPath<FormValues>}
                    render={({ field: input }) => (
                      <FormItem>
                        <FormLabel>{field.label}</FormLabel>
                        <FormControl>
                          <Input
                            name={input.name}
                            ref={input.ref}
                            onBlur={input.onBlur}
                            onChange={input.onChange}
                            value={typeof input.value === "string" ? input.value : ""}
                            disabled={pending}
                            maxLength={field.max_length}
                            required={field.required}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                ))}
                {editing && activity ? (
                  <div className="grid gap-1.5">
                    <label htmlFor="campaign-code" className="text-sm font-medium">
                      Campaign code
                    </label>
                    <div className="flex gap-2">
                      <Input id="campaign-code" value={activity.campaign_code} readOnly />
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            type="button"
                            variant="outline"
                            size="icon"
                            aria-label="Copy campaign code"
                            onClick={() => void copyCampaignCode()}
                          >
                            <Copy aria-hidden />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Copy campaign code</TooltipContent>
                      </Tooltip>
                    </div>
                  </div>
                ) : null}
                {editing ? (
                  <FormField
                    control={form.control}
                    name="status"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Status</FormLabel>
                        <Select value={field.value} onValueChange={field.onChange} disabled={pending}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {(["pending", "published", "archived"] as const).map((status) => (
                              <SelectItem key={status} value={status}>
                                {humanizeEnum(status)}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                ) : null}
                <DialogFooter>
                  {editing ? (
                    <Button
                      type="button"
                      variant="destructive"
                      disabled={pending}
                      onClick={() => setConfirmDelete(true)}
                    >
                      Delete activity
                    </Button>
                  ) : null}
                  <Button type="submit" loading={createActivity.isPending || updateActivity.isPending}>
                    {createActivity.isPending || updateActivity.isPending ? "Saving…" : "Save"}
                  </Button>
                </DialogFooter>
              </form>
            </Form>
          )}
        </DialogContent>
      </Dialog>
      <ConfirmDialog
        open={confirmDelete}
        title="Delete activity?"
        description="This will permanently delete the activity. This action cannot be undone."
        confirmLabel="Delete"
        pendingLabel="Deleting…"
        destructive
        isLoading={deleteActivity.isPending}
        onOpenChange={setConfirmDelete}
        onConfirm={() => void onDelete()}
      />
    </>
  );
}

function DateControl({
  id,
  value,
  disabled,
  onChange,
}: {
  id: string;
  value: string;
  disabled: boolean;
  onChange: (value: string) => void;
}) {
  const selected = value ? (parseISODate(value) ?? undefined) : undefined;
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          id={id}
          type="button"
          variant="outline"
          disabled={disabled}
          className="w-full justify-start font-normal"
        >
          <CalendarIcon aria-hidden />
          {value || "Select date"}
        </Button>
      </PopoverTrigger>
      <PopoverContent>
        <Calendar
          mode="single"
          selected={selected}
          defaultMonth={selected}
          onSelect={(date) => onChange(date ? formatISODate(date) : "")}
        />
      </PopoverContent>
    </Popover>
  );
}
