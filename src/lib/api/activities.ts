import type {
  ActivityCreateRequest,
  ActivityCreateResponse,
  ActivityDeleteResponse,
  ActivityGetResponse,
  ActivityUpdateRequest,
  ActivityUpdateResponse,
} from '@/types/api';
import { apiClient } from './client';

export async function createActivity(
  payload: ActivityCreateRequest,
): Promise<ActivityCreateResponse> {
  const { data } = await apiClient.post<ActivityCreateResponse>(
    '/api/v1/marketing-team-member/activities',
    payload,
  );
  return data;
}

export async function getActivityById(id: string): Promise<ActivityGetResponse> {
  const { data } = await apiClient.get<ActivityGetResponse>(
    `/api/v1/marketing-team-member/activities/${id}`,
  );
  return data;
}

export async function updateActivity(
  id: string,
  payload: ActivityUpdateRequest,
): Promise<ActivityUpdateResponse> {
  const { data } = await apiClient.put<ActivityUpdateResponse>(
    `/api/v1/marketing-team-member/activities/${id}`,
    payload,
  );
  return data;
}

export async function deleteActivity(id: string): Promise<ActivityDeleteResponse> {
  const { data } = await apiClient.delete<ActivityDeleteResponse>(
    `/api/v1/marketing-team-member/activities/${id}`,
  );
  return data;
}
