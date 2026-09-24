import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { toast } from "@/components/ui/toast";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { PasswordInput } from "@/components/ui/password-input";
import { ForgotPasswordForm } from "@/components/features/login/ForgotPasswordForm";
import { useLogin } from "@/hooks/useLogin";
import { getApiErrorCode, getApiErrorMessage, getApiFieldErrors } from "@/lib/api/errors";
import { loginSchema, type LoginFormValues } from "@/lib/validation/login";
import { useAppContext } from "@/stores/AppContext";
import { useState } from "react";

export function LoginPage() {
  const { status, setSession } = useAppContext();
  const navigate = useNavigate();
  const location = useLocation();
  const login = useLogin();
  const [showRecovery, setShowRecovery] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email_or_username: "", password: "" },
    mode: "onChange",
  });

  if (status === "authenticated") {
    const from = (location.state as { from?: string } | null)?.from;
    const target = from && from !== "/login" ? from : "/calendar";
    return <Navigate to={target} replace />;
  }

  async function onSubmit(values: LoginFormValues) {
    setFormError(null);
    try {
      const result = await login.mutateAsync(values);
      setSession(result.data.access_token, result.data.user);
      toast.success(result.message || "Login successful.");
      const from = (location.state as { from?: string } | null)?.from;
      navigate(from && from !== "/login" ? from : "/calendar", { replace: true });
    } catch (error) {
      const code = getApiErrorCode(error);
      const fields = getApiFieldErrors(error);
      if (fields.email_or_username) form.setError("email_or_username", { message: fields.email_or_username });
      if (fields.password) form.setError("password", { message: fields.password });
      if (!axios.isAxiosError(error) || !error.response) {
        toast.error("Unable to sign in. Check your connection.");
        return;
      }
      if (code === "INVALID_CREDENTIALS" || error.response.status === 401) {
        setFormError("Invalid credentials.");
        toast.error(getApiErrorMessage(error, "Invalid credentials."));
        return;
      }
      toast.error(getApiErrorMessage(error, "Unable to sign in. Please try again."));
    }
  }

  return (
    <main className="flex min-h-svh items-center justify-center bg-background px-4 py-8">
      <Card className="w-full max-w-md p-4 shadow-none sm:p-6">
        <div className="mb-6 flex justify-center">
          <img src="/brand-logo.png" alt="Marketing Content Calendar" className="h-10 w-auto" />
        </div>
        <h1 className="text-3xl font-semibold text-foreground">Marketing Content Calendar</h1>
        <p className="mt-2 text-sm text-muted-foreground">Sign in with your email or username.</p>
        <Form {...form}>
          <form className="mt-6 space-y-4" onSubmit={form.handleSubmit(onSubmit)} noValidate>
            <FormField
              control={form.control}
              name="email_or_username"
              render={({ field }) => (
                <FormItem>
                  <FormLabel htmlFor="email-or-username">Email or username</FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      id="email-or-username"
                      autoComplete="username"
                      disabled={login.isPending}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel htmlFor="password">Password</FormLabel>
                  <FormControl>
                    <PasswordInput
                      {...field}
                      id="password"
                      autoComplete="current-password"
                      disabled={login.isPending}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            {formError ? (
              <p role="alert" className="text-sm text-destructive">
                {formError}
              </p>
            ) : null}
            <Button type="submit" className="w-full" loading={login.isPending} disabled={!form.formState.isValid}>
              {login.isPending ? "Signing in…" : "Log in"}
            </Button>
          </form>
        </Form>
        <Button
          type="button"
          variant="ghost"
          className="mt-2 w-full"
          onClick={() => setShowRecovery((current) => !current)}
        >
          Forgot password
        </Button>
        {showRecovery ? <ForgotPasswordForm /> : null}
      </Card>
    </main>
  );
}
