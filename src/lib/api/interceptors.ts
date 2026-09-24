import axios from "axios";
import { getAccessToken, rejectSession } from "@/lib/auth/storage";
import { api } from "@/lib/api/client";

let installed = false;

export function installInterceptors(): void {
  if (installed) return;
  installed = true;

  api.interceptors.request.use((config) => {
    if (!config.skipAuthRedirect) {
      const token = getAccessToken();
      if (token) {
        config.headers.set("Authorization", `Bearer ${token}`);
      }
    }
    return config;
  });

  api.interceptors.response.use(
    (response) => response,
    (error: unknown) => {
      if (
        axios.isAxiosError(error) &&
        error.response?.status === 401 &&
        !error.config?.skipAuthRedirect
      ) {
        rejectSession();
        window.dispatchEvent(new CustomEvent("auth:unauthorized"));
        if (window.location.pathname !== "/login") {
          window.location.replace("/login");
        }
      }
      return Promise.reject(error);
    },
  );
}
