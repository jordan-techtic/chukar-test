import { useMutation } from '@tanstack/react-query';
import { login } from '@/lib/api/auth';
import type { LoginRequest } from '@/types/api';

export function useLogin() {
  return useMutation({
    mutationFn: (payload: LoginRequest) => login(payload),
  });
}
