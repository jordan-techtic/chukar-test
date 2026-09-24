import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import type { LoginRequest, LoginResponse } from "@/types/api";

export function useLogin() {
  return useMutation({
    mutationFn: async (body: LoginRequest) => {
      const response = await api.post<LoginResponse>(
        "/api/v1/marketing-team-member/login",
        body,
        { skipAuthRedirect: true },
      );
      return response.data;
    },
  });
}
