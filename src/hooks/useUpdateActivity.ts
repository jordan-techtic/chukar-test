import { useMutation, useQueryClient } from '@tanstack/react-query';
import { updateActivity } from '@/lib/api/activities';
import type { ActivityUpdateRequest } from '@/types/api';

export function useUpdateActivity(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ActivityUpdateRequest) => updateActivity(id, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['calendar'] });
      void queryClient.invalidateQueries({ queryKey: ['activity', id] });
    },
  });
}
