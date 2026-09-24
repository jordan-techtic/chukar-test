import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import type {
  ActivityCreateRequest,
  ActivityCreateResponse,
  ActivityDeleteResponse,
  ActivityResponse,
  ActivityUpdateRequest,
} from "@/types/api";

export function useCreateActivity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: ActivityCreateRequest) => {
      const response = await api.post<ActivityCreateResponse>(
        "/api/v1/marketing-team-member/activities",
        body,
      );
      return response.data;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["calendar"] });
    },
  });
}

export function useUpdateActivity(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: ActivityUpdateRequest) => {
      const response = await api.put<ActivityResponse>(
        `/api/v1/marketing-team-member/activities/${id}`,
        body,
      );
      return response.data;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["calendar"] });
      await queryClient.invalidateQueries({ queryKey: ["activity", id] });
    },
  });
}

export function useDeleteActivity(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const response = await api.delete<ActivityDeleteResponse>(
        `/api/v1/marketing-team-member/activities/${id}`,
      );
      return response.data;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["calendar"] });
    },
  });
}
