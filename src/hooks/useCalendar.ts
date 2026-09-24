import { useQuery } from "@tanstack/react-query";
import { getCalendar } from "@/lib/api/calendar";
import type { CalendarQuery } from "@/types/api";

export function useCalendar(query: CalendarQuery, enabled: boolean) {
  return useQuery({
    queryKey: ["calendar", query.year, query.activity_type ?? "", query.category ?? ""],
    queryFn: () => getCalendar(query),
    enabled,
  });
}
