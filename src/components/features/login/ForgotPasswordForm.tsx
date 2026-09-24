import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import { useForm } from "react-hook-form";
import { toast } from "@/components/ui/sonner";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useForgotPassword } from "@/hooks/useLogin";
import { getApiFieldErrors, getApiErrorMessage } from "@/lib/api/errors";
import { recoverySchema, type RecoveryFormValues } from "@/lib/validation/login";

export function ForgotPasswordForm() {
  const mutation = useForgotPassword();
  const form = useForm<RecoveryFormValues>({
    resolver: zodResolver(recoverySchema),
    defaultValues: { email: "" },
    mode: "onChange",
  });

  async function onSubmit(values: RecoveryFormValues) {
    try {
      const result = await mutation.mutateAsync(values);
      toast.info(result.message || "If that email is registered, recovery instructions are on the way.");
      form.reset();
    } catch (error) {
      const fields = getApiFieldErrors(error);
      if (fields.email) form.setError("email", { message: fields.email });
      if (!axios.isAxiosError(error) || !error.response) {
        toast.error("Unable to connect. Please check your connection.");
        return;
      }
      toast.error(getApiErrorMessage(error, "Unable to send the recovery email. Please try again."));
    }
  }

  return (
    <Form {...form}>
      <form className="mt-2 space-y-4 border-t border-border pt-4" onSubmit={form.handleSubmit(onSubmit)} noValidate>
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel htmlFor="recovery-email">Email</FormLabel>
              <FormControl>
                <Input {...field} id="recovery-email" type="email" autoComplete="email" disabled={mutation.isPending} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" className="w-full" loading={mutation.isPending} disabled={!form.formState.isValid}>
          {mutation.isPending ? "Sending…" : "Send recovery email"}
        </Button>
      </form>
    </Form>
  );
}
