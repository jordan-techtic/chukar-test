import axios from 'axios';
import type { ApiErrorDetail, ApiErrorResponse } from '@/types/api';

export function isApiError(error: unknown): error is { response: { data: ApiErrorResponse } } {
  return (
    axios.isAxiosError(error) &&
    error.response?.data != null &&
    typeof error.response.data === 'object' &&
    'success' in error.response.data &&
    error.response.data.success === false
  );
}

export function getErrorCode(error: unknown): string | null {
  if (isApiError(error)) {
    return error.response.data.error?.code ?? null;
  }
  return null;
}

export function getApiErrorMessage(error: unknown, fallback = 'Something went wrong. Please try again.'): string {
  if (isApiError(error)) {
    return error.response.data.message || fallback;
  }

  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return 'Unable to connect. Please check your connection.';
    }
    if (error.response.status === 401) {
      return 'Your session may have expired. Please sign in again.';
    }
    if (error.response.status >= 500) {
      return fallback;
    }
  }

  return fallback;
}

export function mapFieldErrors(error: unknown): ApiErrorDetail[] {
  if (!isApiError(error)) return [];

  const details = error.response.data.error?.details;
  if (Array.isArray(details)) {
    return details.filter(
      (item): item is ApiErrorDetail =>
        typeof item === 'object' &&
        item !== null &&
        'field' in item &&
        'message' in item &&
        typeof item.field === 'string' &&
        typeof item.message === 'string',
    );
  }

  return [];
}
