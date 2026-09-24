import { useMemo, useState } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { toast } from '@/components/ui/sonner';
import type { ActivityOut, ActivityTypeOption } from '@/types/api';
import { useActivity } from '@/hooks/useActivity';
import { useCreateActivity } from '@/hooks/useCreateActivity';
import { useUpdateActivity } from '@/hooks/useUpdateActivity';
import { useDeleteActivity } from '@/hooks/useDeleteActivity';
import { getApiErrorMessage, getErrorCode, mapFieldErrors } from '@/lib/api/errors';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/ui/spinner';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Form } from '@/components/ui/form';
import { ConfirmDialog } from '@/components/shared/ConfirmDialog';
import { ActivityFormFields } from './ActivityFormFields';
import { activityFormSchema, type ActivityFormValues } from './activityFormSchema';

interface ActivityFormModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  activityId: string | null;
  activityTypes: ActivityTypeOption[];
  defaultStartDate?: string;
}

function mapActivityToFormValues(activity: ActivityOut): ActivityFormValues {
  return {
    title: activity.title,
    start_date: activity.start_date || activity.date,
    end_date: activity.end_date || '',
    activity_type: activity.activity_type || activity.type,
    details: activity.details || activity.description || activity.notes || '',
    additional_info: activity.additional_info || '',
  };
}

function buildCreateFormValues(defaultStartDate?: string): ActivityFormValues {
  return {
    title: '',
    start_date: defaultStartDate ?? '',
    end_date: '',
    activity_type: '',
    details: '',
    additional_info: '',
  };
}

interface ActivityFormBodyProps {
  activityId: string | null;
  activity: ActivityOut | undefined;
  activityTypes: ActivityTypeOption[];
  defaultStartDate?: string;
  onClose: () => void;
  onDeleteRequest: () => void;
}

function ActivityFormBody({
  activityId,
  activity,
  activityTypes,
  defaultStartDate,
  onClose,
  onDeleteRequest,
}: ActivityFormBodyProps) {
  const isEdit = !!activityId;
  const createMutation = useCreateActivity();
  const updateMutation = useUpdateActivity(activityId ?? '');
  const deleteMutation = useDeleteActivity();

  const initialValues = isEdit && activity
    ? mapActivityToFormValues(activity)
    : buildCreateFormValues(defaultStartDate);

  const form = useForm<ActivityFormValues>({
    resolver: zodResolver(activityFormSchema),
    defaultValues: initialValues,
  });

  const watchedType = useWatch({ control: form.control, name: 'activity_type' });
  const selectedType = useMemo(
    () => activityTypes.find((t) => t.value === watchedType),
    [activityTypes, watchedType],
  );

  const onSubmit = form.handleSubmit(async (values) => {
    try {
      if (isEdit && activity) {
        const response = await updateMutation.mutateAsync({
          title: values.title,
          start_date: values.start_date,
          end_date: values.end_date || null,
          activity_type: values.activity_type,
          details: values.details || null,
          additional_info: values.additional_info || null,
          updated_at: activity.updated_at,
        });
        toast.success(response.message || 'Activity updated successfully.');
        onClose();
        return;
      }

      const response = await createMutation.mutateAsync({
        title: values.title,
        start_date: values.start_date,
        end_date: values.end_date || null,
        activity_type: values.activity_type,
        details: values.details || null,
        additional_info: values.additional_info || null,
        category: selectedType?.category ?? null,
      });

      if (response.success) {
        toast.success(response.message || 'Activity created successfully.');
        onClose();
      }
    } catch (error) {
      const code = getErrorCode(error);
      mapFieldErrors(error).forEach(({ field, message }) => {
        const formField = field as keyof ActivityFormValues;
        if (formField in activityFormSchema.shape) {
          form.setError(formField, { message });
        }
      });

      if (code === 'ACTIVITY_TYPE_CONFLICT') {
        form.setError('activity_type', {
          message: getApiErrorMessage(error, 'This activity type conflicts on the selected date.'),
        });
      }

      if (code === 'STALE_UPDATE') {
        toast.error(getApiErrorMessage(error, 'This activity was updated elsewhere. Please refresh.'));
        return;
      }

      toast.error(getApiErrorMessage(error, 'Unable to save activity. Please try again.'));
    }
  });

  const isSubmitting = createMutation.isPending || updateMutation.isPending;
  const canDelete = isEdit && activity?.status === 'pending';

  return (
    <Form {...form}>
      <form onSubmit={onSubmit} className="space-y-4">
        <ActivityFormFields
          control={form.control}
          activityTypes={activityTypes}
          selectedType={selectedType}
          onActivityTypeChange={() => undefined}
        />

        <DialogFooter className="gap-2 sm:justify-between">
          {canDelete ? (
            <Button
              type="button"
              variant="destructive"
              onClick={onDeleteRequest}
              disabled={isSubmitting || deleteMutation.isPending}
            >
              Delete
            </Button>
          ) : (
            <span />
          )}
          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button type="submit" loading={isSubmitting}>
              {isEdit ? 'Save changes' : 'Create activity'}
            </Button>
          </div>
        </DialogFooter>
      </form>
    </Form>
  );
}

export function ActivityFormModal({
  open,
  onOpenChange,
  activityId,
  activityTypes,
  defaultStartDate,
}: ActivityFormModalProps) {
  const isEdit = !!activityId;
  const [deleteOpen, setDeleteOpen] = useState(false);

  const { data: activity, isLoading: activityLoading } = useActivity(activityId, open && isEdit);
  const deleteMutation = useDeleteActivity();

  const handleClose = () => {
    onOpenChange(false);
  };

  const handleDelete = async () => {
    if (!activityId) return;
    try {
      const response = await deleteMutation.mutateAsync(activityId);
      toast.success(response.message || 'Activity deleted successfully.');
      setDeleteOpen(false);
      handleClose();
    } catch (error) {
      const code = getErrorCode(error);
      if (code === 'ACTIVITY_PUBLISHED') {
        toast.error(getApiErrorMessage(error, 'Published activities cannot be deleted.'));
        setDeleteOpen(false);
        return;
      }
      toast.error(getApiErrorMessage(error, 'Unable to delete activity. Please try again.'));
    }
  };

  const formKey = isEdit
    ? `edit-${activityId}-${activity?.updated_at ?? 'loading'}`
    : `create-${defaultStartDate ?? 'new'}`;

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{isEdit ? 'Edit Activity' : 'Add Activity'}</DialogTitle>
          </DialogHeader>

          {isEdit && activityLoading ? (
            <div className="flex justify-center py-8">
              <Spinner label="Loading activity" />
            </div>
          ) : open && (!isEdit || activity) ? (
            <ActivityFormBody
              key={formKey}
              activityId={activityId}
              activity={activity}
              activityTypes={activityTypes}
              defaultStartDate={defaultStartDate}
              onClose={handleClose}
              onDeleteRequest={() => setDeleteOpen(true)}
            />
          ) : null}
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        title="Delete activity?"
        description="This will permanently delete the activity. This action cannot be undone."
        confirmLabel="Delete"
        variant="destructive"
        isLoading={deleteMutation.isPending}
        onConfirm={handleDelete}
      />
    </>
  );
}
