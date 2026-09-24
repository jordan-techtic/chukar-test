import axios from 'axios';

function resolveBaseUrl(): string {
  const envUrl = import.meta.env.VITE_API_BASE_URL ?? '';
  if (!envUrl) return '';
  return envUrl.replace(/\/api\/?$/, '');
}

export const apiClient = axios.create({
  baseURL: resolveBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

export const AUTH_TOKEN_KEY = 'access_token';
export const AUTH_USER_KEY = 'auth_user';
export const SESSION_REJECTED_KEY = 'session_rejected';
