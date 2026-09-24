import { useMutation, useQueryClient } from '@tanstack/react-query';
import { deleteActivity } from '@/lib/api/activities';

export function useDeleteActivity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteActivity(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['calendar'] });
    },
  });
}
