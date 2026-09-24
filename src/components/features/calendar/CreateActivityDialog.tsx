import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { toast } from "@/components/ui/sonner";
import { ActivityFields } from "@/components/features/calendar/ActivityFields";
import { applyActivityErrors } from "@/components/features/calendar/activity-errors";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Form } from "@/components/ui/form";
import { useCreateActivity } from "@/hooks/useActivityMutations";
import { activitySchema, emptyActivityForm, type ActivityFormValues } from "@/lib/validation/activity";
import type { ActivityCreateRequest, ActivityTypeOption } from "@/types/api";

export function CreateActivityDialog({
  open,
  onOpenChange,
  activityTypes,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  activityTypes: ActivityTypeOption[];
}) {
  const mutation = useCreateActivity();
  const form = useForm<ActivityFormValues>({
    resolver: zodResolver(activitySchema),
    defaultValues: emptyActivityForm,
  });

  async function onSubmit(values: ActivityFormValues) {
    const selected = activityTypes.find((option) => option.value === values.activity_type);
    const requiredExtra = selected?.fields.find((field) => field.required);
    if (requiredExtra && !values.additional_info.trim()) {
      form.setError("additional_info", { message: `${requiredExtra.label} is required.` });
      return;
    }
    const body: ActivityCreateRequest = {
      title: values.title.trim(),
      start_date: values.start_date,
      activity_type: values.activity_type,
    };
    if (values.end_date) body.end_date = values.end_date;
    if (values.details.trim()) body.details = values.details.trim();
    if (values.additional_info.trim()) body.additional_info = values.additional_info.trim();
    try {
      const result = await mutation.mutateAsync(body);
      toast.success(result.message || "Activity created successfully.");
      form.reset(emptyActivityForm);
      onOpenChange(false);
    } catch (error) {
      applyActivityErrors(error, form);
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        if (!next) form.reset(emptyActivityForm);
        onOpenChange(next);
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create activity</DialogTitle>
          <DialogDescription>Required fields are title, start date, and activity type.</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)} noValidate>
            <ActivityFields form={form} activityTypes={activityTypes} disabled={mutation.isPending} />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={mutation.isPending}>
                Cancel
              </Button>
              <Button type="submit" loading={mutation.isPending}>
                {mutation.isPending ? "Creating…" : "Create activity"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
