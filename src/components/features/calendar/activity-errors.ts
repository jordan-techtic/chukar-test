import type { UseFormReturn } from "react-hook-form";
import { toast } from "@/components/ui/sonner";
import { getApiErrorCode, getApiErrorMessage, getApiFieldErrors } from "@/lib/api/errors";
import { emptyActivityForm, type ActivityFormValues } from "@/lib/validation/activity";

export function applyActivityErrors(
  error: unknown,
  form: UseFormReturn<ActivityFormValues>,
  handlers?: { onNotFound?: () => void; onStale?: () => void },
) {
  const code = getApiErrorCode(error);
  const fields = getApiFieldErrors(error);
  for (const [key, message] of Object.entries(fields)) {
    if (key in emptyActivityForm) {
      form.setError(key as keyof ActivityFormValues, { message });
    }
  }
  if (code === "DATE_IN_PAST" && !fields.start_date) {
    form.setError("start_date", { message: "Start date cannot be in the past." });
  }
  if (code === "ACTIVITY_TYPE_CONFLICT" && !fields.activity_type) {
    form.setError("activity_type", { message: getApiErrorMessage(error) });
  }
  if (code === "STALE_UPDATE") {
    toast.error("This activity was updated elsewhere.");
    handlers?.onStale?.();
    return;
  }
  if (code === "ACTIVITY_NOT_FOUND") {
    toast.error(getApiErrorMessage(error));
    handlers?.onNotFound?.();
    return;
  }
  toast.error(getApiErrorMessage(error));
}
