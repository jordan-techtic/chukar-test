import type { HealthResponse } from '@/types/api';
import { apiClient } from './client';

export async function checkHealth(): Promise<HealthResponse> {
  const { data } = await apiClient.get<HealthResponse>('/api/v1/health');
  return data;
}
