import { api } from "@/lib/api/client";
import type {
  ActivityCreateRequest,
  ActivityCreateResponse,
  ActivityDeleteResponse,
  ActivityGetResponse,
  ActivityUpdateRequest,
  ActivityUpdateResponse,
} from "@/types/api";

export async function createActivity(body: ActivityCreateRequest): Promise<ActivityCreateResponse> {
  const response = await api.post<ActivityCreateResponse>(
    "/api/v1/marketing-team-member/activities",
    body,
  );
  return response.data;
}

export async function getActivity(id: string): Promise<ActivityGetResponse> {
  const response = await api.get<ActivityGetResponse>(
    `/api/v1/marketing-team-member/activities/${id}`,
  );
  return response.data;
}

export async function updateActivity(
  id: string,
  body: ActivityUpdateRequest,
): Promise<ActivityUpdateResponse> {
  const response = await api.put<ActivityUpdateResponse>(
    `/api/v1/marketing-team-member/activities/${id}`,
    body,
  );
  return response.data;
}

export async function deleteActivity(id: string): Promise<ActivityDeleteResponse> {
  const response = await api.delete<ActivityDeleteResponse>(
    `/api/v1/marketing-team-member/activities/${id}`,
  );
  return response.data;
}
