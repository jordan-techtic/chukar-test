import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, useLocation } from 'react-router-dom';
import { toast } from '@/components/ui/sonner';
import { useLogin } from '@/hooks/useLogin';
import { useAppContext } from '@/stores/AppContext';
import { getApiErrorMessage, getErrorCode, mapFieldErrors } from '@/lib/api/errors';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { PasswordInput } from '@/components/ui/password-input';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { ForgotPasswordDialog } from './ForgotPasswordDialog';

const loginSchema = z.object({
  email_or_username: z.string().min(1, 'Email or username is required.'),
  password: z.string().min(1, 'Password is required.'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export function LoginForm() {
  const navigate = useNavigate();
  const location = useLocation();
  const { setSession } = useAppContext();
  const loginMutation = useLogin();
  const [forgotOpen, setForgotOpen] = useState(false);

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email_or_username: '',
      password: '',
    },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    try {
      const response = await loginMutation.mutateAsync(values);
      if (!response.success) {
        toast.error(response.message || 'Unable to sign in. Please try again.');
        return;
      }

      setSession(response.data.access_token, response.data.user);
      toast.success('Signed in successfully.');
      const from = (location.state as { from?: string } | null)?.from ?? '/calendar';
      navigate(from, { replace: true });
    } catch (error) {
      const fieldErrors = mapFieldErrors(error);
      fieldErrors.forEach(({ field, message }) => {
        if (field === 'email_or_username' || field === 'password') {
          form.setError(field, { message });
        }
      });

      const code = getErrorCode(error);
      const message = getApiErrorMessage(error, 'Unable to sign in. Please try again.');
      toast.error(code === 'INVALID_CREDENTIALS' ? message : message);
    }
  });

  return (
    <>
      <Form {...form}>
        <form onSubmit={onSubmit} className="space-y-4">
          <FormField
            control={form.control}
            name="email_or_username"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email or username</FormLabel>
                <FormControl>
                  <Input autoComplete="username" placeholder="Enter email or username" {...field} />
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
                <FormLabel>Password</FormLabel>
                <FormControl>
                  <PasswordInput autoComplete="current-password" placeholder="Enter password" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" className="w-full" loading={loginMutation.isPending}>
            Log in
          </Button>
          <Button
            type="button"
            variant="ghost"
            className="w-full"
            onClick={() => setForgotOpen(true)}
          >
            Forgot password
          </Button>
        </form>
      </Form>
      <ForgotPasswordDialog open={forgotOpen} onOpenChange={setForgotOpen} />
    </>
  );
}
