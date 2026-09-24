import { useQuery } from '@tanstack/react-query';
import { getCalendar } from '@/lib/api/calendar';
import type { CalendarQueryParams } from '@/types/api';

export function useCalendar(params: CalendarQueryParams) {
  const categoryKey = params.category?.slice().sort().join(',') ?? '';
  const activityTypeKey = params.activity_type?.slice().sort().join(',') ?? '';

  return useQuery({
    queryKey: ['calendar', params.year, params.month, categoryKey, activityTypeKey],
    queryFn: async () => {
      const response = await getCalendar(params);
      if (!response.success) {
        throw new Error(response.message);
      }
      return response.data;
    },
    enabled: params.year != null,
  });
}
