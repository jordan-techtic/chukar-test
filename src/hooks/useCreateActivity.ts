import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createActivity } from '@/lib/api/activities';
import type { ActivityCreateRequest } from '@/types/api';

export function useCreateActivity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ActivityCreateRequest) => createActivity(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['calendar'] });
    },
  });
}
