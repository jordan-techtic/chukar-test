import { useMutation } from "@tanstack/react-query";
import { forgotPassword, login } from "@/lib/api/auth";
import type { ForgotPasswordRequest, LoginRequest } from "@/types/api";

export function useLogin() {
  return useMutation({
    mutationFn: (body: LoginRequest) => login(body),
  });
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: (body: ForgotPasswordRequest) => forgotPassword(body),
  });
}
