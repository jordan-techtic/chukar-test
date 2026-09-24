import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import type { CalendarResponse } from "@/types/api";

export type CalendarFilters = {
  category?: string;
  activity_type?: string;
};

export function useCalendar(year: number, filters: CalendarFilters, enabled: boolean) {
  return useQuery({
    queryKey: ["calendar", year, filters.category ?? null, filters.activity_type ?? null],
    enabled,
    placeholderData: keepPreviousData,
    queryFn: async () => {
      const params: Record<string, string | number> = { year };
      if (filters.category) params.category = filters.category;
      if (filters.activity_type) params.activity_type = filters.activity_type;
      const response = await api.get<CalendarResponse>("/api/v1/marketing-team-member/calendar", {
        params,
      });
      return response.data;
    },
  });
}
