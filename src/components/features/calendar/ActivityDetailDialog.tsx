import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "@/components/ui/toast";
import { ActivityFields } from "@/components/features/calendar/ActivityFields";
import { applyActivityErrors } from "@/components/features/calendar/activity-errors";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { Badge } from "@/components/ui/badge";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { useActivity, useDeleteActivity, useUpdateActivity } from "@/hooks/useActivityMutations";
import { getApiErrorCode, getApiErrorMessage } from "@/lib/api/errors";
import { activitySchema, emptyActivityForm, type ActivityFormValues } from "@/lib/validation/activity";
import type { ActivityTypeOption, ActivityUpdateRequest } from "@/types/api";

export function ActivityDetailDialog({
  activityId,
  open,
  canEdit,
  activityTypes,
  onOpenChange,
  onMissing,
}: {
  activityId: string | null;
  open: boolean;
  canEdit: boolean;
  activityTypes: ActivityTypeOption[];
  onOpenChange: (open: boolean) => void;
  onMissing: () => void;
}) {
  const query = useActivity(activityId, open);
  const update = useUpdateActivity(activityId ?? "");
  const remove = useDeleteActivity(activityId ?? "");
  const [confirmOpen, setConfirmOpen] = useState(false);
  const activity = query.data?.data;
  const form = useForm<ActivityFormValues>({
    resolver: zodResolver(activitySchema),
    defaultValues: emptyActivityForm,
  });

  useEffect(() => {
    if (!activity) return;
    form.reset({
      title: activity.title,
      start_date: activity.start_date,
      end_date: activity.end_date === activity.start_date ? "" : activity.end_date,
      activity_type: activity.activity_type,
      details: activity.details ?? "",
      additional_info: activity.additional_info ?? "",
    });
  }, [activity, form]);

  async function onSubmit(values: ActivityFormValues) {
    if (!activity) return;
    const body: ActivityUpdateRequest = { updated_at: activity.updated_at };
    if (values.title.trim() !== activity.title) body.title = values.title.trim();
    if (values.start_date !== activity.start_date) body.start_date = values.start_date;
    const nextEnd = values.end_date || values.start_date;
    if (nextEnd !== activity.end_date) body.end_date = nextEnd;
    if (values.activity_type !== activity.activity_type) body.activity_type = values.activity_type;
    if ((values.details.trim() || null) !== (activity.details ?? null)) {
      body.details = values.details.trim();
    }
    if ((values.additional_info.trim() || null) !== (activity.additional_info ?? null)) {
      body.additional_info = values.additional_info.trim();
    }
    try {
      const result = await update.mutateAsync(body);
      toast.success(result.message || "Changes saved successfully.");
      onOpenChange(false);
    } catch (error) {
      applyActivityErrors(error, form, {
        onStale: () => {
          void query.refetch();
        },
        onNotFound: () => {
          onOpenChange(false);
          onMissing();
        },
      });
    }
  }

  async function onDelete() {
    try {
      const result = await remove.mutateAsync();
      toast.success(result.message || "Activity deleted successfully.");
      setConfirmOpen(false);
      onOpenChange(false);
    } catch (error) {
      if (getApiErrorCode(error) === "ACTIVITY_PUBLISHED") {
        toast.error(getApiErrorMessage(error));
        setConfirmOpen(false);
        return;
      }
      if (getApiErrorCode(error) === "ACTIVITY_NOT_FOUND") {
        toast.error(getApiErrorMessage(error));
        setConfirmOpen(false);
        onOpenChange(false);
        onMissing();
        return;
      }
      toast.error(getApiErrorMessage(error, "Unable to delete the activity. Please try again."));
    }
  }

  const statusVariant =
    activity?.status === "published" ? "success" : activity?.status === "pending" ? "warning" : "secondary";

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit activity</DialogTitle>
            <DialogDescription>Required fields are title, start date, and activity type.</DialogDescription>
          </DialogHeader>
          {query.isPending ? (
            <div className="flex justify-center py-8" aria-busy="true">
              <Spinner label="Loading activity" />
            </div>
          ) : query.isError || !activity ? (
            <p role="alert" className="text-sm text-destructive">
              {getApiErrorMessage(query.error, "Unable to load this activity.")}
            </p>
          ) : (
            <Form {...form}>
              <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)} noValidate>
                <div className="space-y-1">
                  <Label htmlFor="campaign-code">Campaign code</Label>
                  <div className="flex gap-2">
                    <Input id="campaign-code" value={activity.campaign_code} readOnly />
                    <Button
                      type="button"
                      variant="outline"
                      aria-label="Copy campaign code"
                      onClick={() => {
                        void navigator.clipboard.writeText(activity.campaign_code);
                        toast.success("Campaign code copied.");
                      }}
                    >
                      Copy
                    </Button>
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium">Status</p>
                  <Badge variant={statusVariant}>{activity.status}</Badge>
                </div>
                <ActivityFields form={form} activityTypes={activityTypes} disabled={!canEdit || update.isPending} />
                <DialogFooter>
                  {canEdit && activity.status !== "published" ? (
                    <Button
                      type="button"
                      variant="outline"
                      className="text-destructive sm:mr-auto"
                      onClick={() => setConfirmOpen(true)}
                      disabled={remove.isPending}
                    >
                      Delete activity
                    </Button>
                  ) : null}
                  <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                    Cancel
                  </Button>
                  {canEdit ? (
                    <Button type="submit" loading={update.isPending}>
                      {update.isPending ? "Saving…" : "Save"}
                    </Button>
                  ) : null}
                </DialogFooter>
              </form>
            </Form>
          )}
        </DialogContent>
      </Dialog>
      <ConfirmDialog
        open={confirmOpen}
        title="Delete activity?"
        description="This will permanently delete the activity. This action cannot be undone."
        confirmLabel="Delete"
        pendingLabel="Deleting…"
        isLoading={remove.isPending}
        onOpenChange={setConfirmOpen}
        onConfirm={() => {
          void onDelete();
        }}
      />
    </>
  );
}
