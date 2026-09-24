import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { toast } from "@/components/ui/toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { getApiErrorMessage, getErrorDetails } from "@/lib/api/errors";
import {
  forgotPasswordSchema,
  loginSchema,
  type ForgotPasswordFormValues,
  type LoginFormValues,
} from "@/features/auth/login-schema";
import { useForgotPassword } from "@/features/auth/use-forgot-password";
import { useLogin } from "@/features/auth/use-login";
import { useAuth } from "@/stores/AppContext";

function internalPath(state: unknown): string | null {
  if (!state || typeof state !== "object" || !("from" in state)) return null;
  const from = (state as { from: unknown }).from;
  if (typeof from !== "string") return null;
  if (!from.startsWith("/") || from.startsWith("//") || from.startsWith("/login")) return null;
  return from;
}

export function LoginPage() {
  const { ready, authenticated, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const loginMutation = useLogin();
  const forgotMutation = useForgotPassword();
  const [showPassword, setShowPassword] = useState(false);
  const [showForgot, setShowForgot] = useState(false);
  const [formError, setFormError] = useState("");

  const loginForm = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email_or_username: "", password: "" },
    mode: "onSubmit",
  });
  const forgotForm = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: "" },
  });

  const emailValue = useWatch({ control: loginForm.control, name: "email_or_username" });
  const passwordValue = useWatch({ control: loginForm.control, name: "password" });

  if (!ready) {
    return (
      <div className="flex min-h-svh items-center justify-center">
        <Spinner label="Loading session" />
      </div>
    );
  }
  if (authenticated) return <Navigate to="/calendar" replace />;

  async function onLogin(values: LoginFormValues) {
    setFormError("");
    try {
      const result = await loginMutation.mutateAsync(values);
      login(result.data.access_token, result.data.user);
      toast.success(result.message);
      navigate(internalPath(location.state) ?? "/calendar", { replace: true });
    } catch (error) {
      const message = getApiErrorMessage(error);
      setFormError(message);
      toast.error(message);
      for (const detail of getErrorDetails(error)) {
        if (detail.field === "email_or_username" || detail.field === "password") {
          loginForm.setError(detail.field, { message: detail.message });
        }
      }
    }
  }

  async function onForgot(values: ForgotPasswordFormValues) {
    try {
      const result = await forgotMutation.mutateAsync({ email: values.email });
      toast.info(result.message);
    } catch (error) {
      for (const detail of getErrorDetails(error)) {
        if (detail.field === "email") forgotForm.setError("email", { message: detail.message });
      }
      if (getErrorDetails(error).length === 0) {
        toast.error(getApiErrorMessage(error));
      }
    }
  }

  return (
    <div className="flex min-h-svh items-center justify-center bg-background p-6">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-[28px] leading-9">Marketing Content Calendar</CardTitle>
          <p className="text-sm text-muted-foreground">Sign in</p>
        </CardHeader>
        <CardContent>
          <Form {...loginForm}>
            <form className="grid gap-4" onSubmit={loginForm.handleSubmit(onLogin)} noValidate>
              {formError ? (
                <p role="alert" className="text-sm text-destructive">
                  {formError}
                </p>
              ) : null}
              <FormField
                control={loginForm.control}
                name="email_or_username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email or username</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        autoComplete="username"
                        disabled={loginMutation.isPending}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={loginForm.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password</FormLabel>
                    <div className="relative">
                      <FormControl>
                        <Input
                          {...field}
                          type={showPassword ? "text" : "password"}
                          autoComplete="current-password"
                          disabled={loginMutation.isPending}
                          className="pr-12"
                        />
                      </FormControl>
                      <button
                        type="button"
                        className="absolute top-1/2 right-1 inline-flex size-11 -translate-y-1/2 items-center justify-center rounded-md text-muted-foreground hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none md:size-8"
                        aria-label={showPassword ? "Hide password" : "Show password"}
                        aria-pressed={showPassword}
                        onClick={() => setShowPassword((current) => !current)}
                      >
                        {showPassword ? <EyeOff className="size-4" aria-hidden /> : <Eye className="size-4" aria-hidden />}
                      </button>
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button
                type="submit"
                className="w-full"
                aria-busy={loginMutation.isPending || undefined}
                disabled={!emailValue.trim() || !passwordValue || loginMutation.isPending}
              >
                {loginMutation.isPending ? <Spinner label="Signing in" visibleLabel={false} /> : null}
                {loginMutation.isPending ? "Signing in…" : "Sign in"}
              </Button>
            </form>
          </Form>
          <Button
            type="button"
            variant="ghost"
            className="mt-2 w-full"
            onClick={() => setShowForgot((current) => !current)}
          >
            Forgot password?
          </Button>
          {showForgot ? (
            <Form {...forgotForm}>
              <form className="mt-2 grid gap-4" onSubmit={forgotForm.handleSubmit(onForgot)} noValidate>
                <FormField
                  control={forgotForm.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type="email"
                          autoComplete="email"
                          disabled={forgotMutation.isPending}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button
                  type="submit"
                  variant="outline"
                  aria-busy={forgotMutation.isPending || undefined}
                  disabled={forgotMutation.isPending}
                >
                  {forgotMutation.isPending ? <Spinner label="Sending" visibleLabel={false} /> : null}
                  {forgotMutation.isPending ? "Sending…" : "Send recovery email"}
                </Button>
              </form>
            </Form>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
