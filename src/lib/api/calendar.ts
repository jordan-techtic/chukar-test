import { api } from "@/lib/api/client";
import type { CalendarQuery, CalendarResponse } from "@/types/api";

export async function getCalendar(query: CalendarQuery): Promise<CalendarResponse> {
  const params: Record<string, string | number> = { year: query.year };
  if (query.activity_type) params.activity_type = query.activity_type;
  if (query.category) params.category = query.category;
  const response = await api.get<CalendarResponse>("/api/v1/marketing-team-member/calendar", {
    params,
  });
  return response.data;
}
