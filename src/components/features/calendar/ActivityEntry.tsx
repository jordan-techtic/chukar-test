import type { ActivityOut } from "@/types/api";
import { textOnColor } from "@/lib/format";

export function ActivityEntry({
  activity,
  date,
  onOpen,
}: {
  activity: ActivityOut;
  date: string;
  onOpen: (activity: ActivityOut) => void;
}) {
  return (
    <button
      type="button"
      className="w-full truncate rounded-sm px-1 py-0.5 text-left text-xs font-medium hover:underline hover:brightness-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      style={{ backgroundColor: activity.color, color: textOnColor(activity.color) }}
      title={activity.title}
      aria-label={`${activity.title}, ${date}, ${activity.activity_type}`}
      onClick={() => onOpen(activity)}
    >
      {activity.title}
    </button>
  );
}
