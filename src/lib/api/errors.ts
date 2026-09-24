import axios from "axios";
import type { ErrorDetail, ErrorEnvelope } from "@/types/api";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

export function isErrorEnvelope(value: unknown): value is ErrorEnvelope {
  if (!isRecord(value) || value.success !== false || typeof value.message !== "string") {
    return false;
  }
  if (!isRecord(value.error) || typeof value.error.code !== "string") return false;
  return true;
}

export function getErrorDetails(error: unknown): ErrorDetail[] {
  if (!axios.isAxiosError(error)) return [];
  const data: unknown = error.response?.data;
  if (!isErrorEnvelope(data) || !Array.isArray(data.error.details)) return [];
  return data.error.details.filter(
    (detail): detail is ErrorDetail =>
      isRecord(detail) &&
      typeof detail.field === "string" &&
      typeof detail.message === "string",
  );
}

export function getErrorCode(error: unknown): string | null {
  if (!axios.isAxiosError(error)) return null;
  const data: unknown = error.response?.data;
  return isErrorEnvelope(data) ? data.error.code : null;
}

function envelopeMessage(error: unknown): string | null {
  if (!axios.isAxiosError(error)) return null;
  const data: unknown = error.response?.data;
  if (!isErrorEnvelope(data)) return null;
  const message = data.message.trim();
  if (!message) return null;
  if (/axioserror|request failed with status/i.test(message)) return null;
  return message;
}

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return "Unable to connect. Please check your connection.";
    }
    const status = error.response.status;
    const message = envelopeMessage(error);
    if (status === 401) {
      return message ?? "Your session may have expired. Please sign in again.";
    }
    if (message) return message;
    if (status >= 500 || error.code === "ECONNABORTED") {
      return "Something went wrong. Please try again.";
    }
    return "Something went wrong. Please try again.";
  }
  return "Something went wrong. Please try again.";
}
