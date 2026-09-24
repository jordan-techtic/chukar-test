import { api, type ApiRequestConfig } from "@/lib/api/client";
import type { ForgotPasswordRequest, ForgotPasswordResponse, LoginRequest, LoginResponse } from "@/types/api";

export async function login(body: LoginRequest): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>("/api/v1/marketing-team-member/login", body, {
    skipAuthRedirect: true,
  } as ApiRequestConfig);
  return response.data;
}

export async function forgotPassword(body: ForgotPasswordRequest): Promise<ForgotPasswordResponse> {
  const response = await api.post<ForgotPasswordResponse>(
    "/api/v1/marketing-team-member/forgot-password",
    body,
    { skipAuthRedirect: true } as ApiRequestConfig,
  );
  return response.data;
}
