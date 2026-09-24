import type { AxiosError } from "axios";
import { rejectSession } from "@/lib/auth/storage";
import { queryClient } from "@/lib/queryClient";
import { api, type ApiRequestConfig } from "@/lib/api/client";
import { readAccessToken } from "@/lib/auth/storage";

let redirecting = false;

export function attachInterceptors(): void {
  api.interceptors.request.use((config) => {
    const request = config as ApiRequestConfig;
    const token = readAccessToken();
    if (token && !request.skipAuthRedirect && !request.headers.Authorization) {
      request.headers.Authorization = `Bearer ${token}`;
    }
    return request;
  });

  api.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      const status = error.response?.status;
      const config = error.config as ApiRequestConfig | undefined;
      if (status === 401 && !config?.skipAuthRedirect) {
        rejectSession();
        queryClient.clear();
        window.dispatchEvent(new Event("auth:unauthorized"));
        if (!redirecting && window.location.pathname !== "/login") {
          redirecting = true;
          window.location.replace("/login");
        }
      }
      return Promise.reject(error);
    },
  );
}
