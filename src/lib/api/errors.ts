import axios from "axios";
import type { ApiErrorResponse } from "@/types/api";

const FIELD_ALIASES: Record<string, string> = {
  activity_date: "start_date",
  date: "start_date",
  type: "activity_type",
  notes: "details",
  description: "details",
};

export function isApiErrorResponse(value: unknown): value is ApiErrorResponse {
  if (!value || typeof value !== "object") return false;
  const record = value as Record<string, unknown>;
  return record.success === false && typeof record.message === "string";
}

export function getApiErrorCode(error: unknown): string | undefined {
  if (!axios.isAxiosError(error)) return undefined;
  const data: unknown = error.response?.data;
  if (!isApiErrorResponse(data)) return undefined;
  return data.error?.code;
}

export function getApiFieldErrors(error: unknown): Record<string, string> {
  if (!axios.isAxiosError(error)) return {};
  const data: unknown = error.response?.data;
  if (!isApiErrorResponse(data) || !data.error?.details) return {};
  const fields: Record<string, string> = {};
  for (const detail of data.error.details) {
    const key = FIELD_ALIASES[detail.field] ?? detail.field;
    if (!fields[key]) fields[key] = detail.message;
  }
  return fields;
}

export function getApiErrorMessage(error: unknown, fallback = "Something went wrong. Please try again."): string {
  if (!axios.isAxiosError(error)) return fallback;
  if (!error.response) {
    return "Unable to connect. Please check your connection.";
  }
  const status = error.response.status;
  const data: unknown = error.response.data;
  const message = isApiErrorResponse(data) ? data.message.trim() : "";
  if (status === 401) {
    return message || "Your session may have expired. Please sign in again.";
  }
  if (status === 429 && message) return message;
  if (status >= 500 || error.code === "ECONNABORTED") {
    return "Something went wrong. Please try again.";
  }
  if (message) return message;
  return fallback;
}
