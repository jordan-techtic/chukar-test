import type { CalendarQueryParams, CalendarResponse } from '@/types/api';
import { apiClient } from './client';

export async function getCalendar(params: CalendarQueryParams): Promise<CalendarResponse> {
  const { data } = await apiClient.get<CalendarResponse>(
    '/api/v1/marketing-team-member/calendar',
    {
      params: {
        year: params.year,
        month: params.month,
        category: params.category,
        activity_type: params.activity_type,
      },
      paramsSerializer: {
        indexes: null,
      },
    },
  );
  return data;
}
