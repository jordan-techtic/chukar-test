import { useMutation } from '@tanstack/react-query';
import { forgotPassword } from '@/lib/api/auth';
import type { ForgotPasswordRequest } from '@/types/api';

export function useForgotPassword() {
  return useMutation({
    mutationFn: (payload: ForgotPasswordRequest) => forgotPassword(payload),
  });
}
