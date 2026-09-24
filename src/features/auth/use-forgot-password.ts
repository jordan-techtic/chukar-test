import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import type { ForgotPasswordRequest, ForgotPasswordResponse } from "@/types/api";

export function useForgotPassword() {
  return useMutation({
    mutationFn: async (body: ForgotPasswordRequest) => {
      const response = await api.post<ForgotPasswordResponse>(
        "/api/v1/marketing-team-member/forgot-password",
        body,
        { skipAuthRedirect: true },
      );
      return response.data;
    },
  });
}
