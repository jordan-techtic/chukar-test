import { useQuery } from '@tanstack/react-query';
import { getActivityById } from '@/lib/api/activities';

export function useActivity(id: string | null, enabled: boolean) {
  return useQuery({
    queryKey: ['activity', id],
    queryFn: async () => {
      if (!id) throw new Error('Activity id is required');
      const response = await getActivityById(id);
      if (!response.success) {
        throw new Error(response.message);
      }
      return response.data;
    },
    enabled: enabled && !!id,
  });
}
