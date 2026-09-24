import axios from "axios";

export function resolveApiOrigin(baseUrl: string | undefined): string {
  const raw = (baseUrl ?? "").trim() || "http://174.138.72.184:8989/api";
  return raw.replace(/\/api\/?$/, "");
}

export const api = axios.create({
  baseURL: resolveApiOrigin(import.meta.env.VITE_API_BASE_URL),
  headers: {
    "Content-Type": "application/json",
  },
});
