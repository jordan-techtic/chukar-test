import axios, { type InternalAxiosRequestConfig } from "axios";

export interface ApiRequestConfig extends InternalAxiosRequestConfig {
  skipAuthRedirect?: boolean;
}

const rawBase = import.meta.env.VITE_API_BASE_URL ?? "";
const trimmed = rawBase.replace(/\/$/, "");
const origin = trimmed.endsWith("/api") ? trimmed.slice(0, -4) : trimmed;

export const api = axios.create({
  baseURL: origin,
});
