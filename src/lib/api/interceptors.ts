import type { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { apiClient, AUTH_TOKEN_KEY, AUTH_USER_KEY, SESSION_REJECTED_KEY } from './client';

export const UNAUTHORIZED_EVENT = 'auth:unauthorized';

declare module 'axios' {
  export interface AxiosRequestConfig {
    skipAuthRedirect?: boolean;
  }
}

export function setupInterceptors(): void {
  apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  apiClient.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      const status = error.response?.status;
      const config = error.config;

      if (status === 401 && !config?.skipAuthRedirect) {
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem(AUTH_USER_KEY);
        sessionStorage.setItem(SESSION_REJECTED_KEY, 'true');
        window.dispatchEvent(new CustomEvent(UNAUTHORIZED_EVENT));

        if (window.location.pathname !== '/login') {
          window.location.replace('/login');
        }
      }

      return Promise.reject(error);
    },
  );
}
