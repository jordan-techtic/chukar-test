import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createActivity, deleteActivity, getActivity, updateActivity } from "@/lib/api/activities";
import type { ActivityCreateRequest, ActivityUpdateRequest } from "@/types/api";

export function useActivity(id: string | null, enabled: boolean) {
  return useQuery({
    queryKey: ["activity", id],
    queryFn: () => getActivity(id ?? ""),
    enabled: enabled && Boolean(id),
  });
}

export function useCreateActivity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: ActivityCreateRequest) => createActivity(body),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["calendar"] });
    },
  });
}

export function useUpdateActivity(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: ActivityUpdateRequest) => updateActivity(id, body),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["calendar"] });
      await queryClient.invalidateQueries({ queryKey: ["activity", id] });
    },
  });
}

export function useDeleteActivity(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => deleteActivity(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["calendar"] });
      queryClient.removeQueries({ queryKey: ["activity", id] });
    },
  });
}

export function useDeleteActivityAction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteActivity(id),
    onSuccess: async (_data, id) => {
      await queryClient.invalidateQueries({ queryKey: ["calendar"] });
      queryClient.removeQueries({ queryKey: ["activity", id] });
    },
  });
}
