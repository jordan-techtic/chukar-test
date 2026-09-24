import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import type { ActivityResponse } from "@/types/api";

export function useActivity(id: string | null, enabled: boolean) {
  return useQuery({
    queryKey: ["activity", id],
    enabled: enabled && Boolean(id),
    queryFn: async () => {
      const response = await api.get<ActivityResponse>(
        `/api/v1/marketing-team-member/activities/${id}`,
      );
      return response.data;
    },
  });
}
