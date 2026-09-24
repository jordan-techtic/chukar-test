import type {
  ForgotPasswordRequest,
  ForgotPasswordResponse,
  LoginRequest,
  LoginResponse,
} from '@/types/api';
import { apiClient } from './client';

export async function login(payload: LoginRequest): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>(
    '/api/v1/marketing-team-member/login',
    payload,
    { skipAuthRedirect: true },
  );
  return data;
}

export async function forgotPassword(payload: ForgotPasswordRequest): Promise<ForgotPasswordResponse> {
  const { data } = await apiClient.post<ForgotPasswordResponse>(
    '/api/v1/marketing-team-member/forgot-password',
    payload,
    { skipAuthRedirect: true },
  );
  return data;
}
