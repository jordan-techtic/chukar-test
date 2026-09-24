import type { Activity } from "@/types/api";
import { activityChipStyle, cn } from "@/lib/utils";

export function ActivityEntry({
  activity,
  onSelect,
}: {
  activity: Activity;
  onSelect: (activity: Activity) => void;
}) {
  const style = activityChipStyle(activity.color);
  return (
    <button
      type="button"
      onClick={() => onSelect(activity)}
      style={style}
      className={cn(
        "block w-full truncate rounded-sm px-1.5 py-1 text-left text-xs font-medium",
        "hover:brightness-105 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none",
      )}
    >
      <span className="block truncate">{activity.title}</span>
      {activity.campaign_code ? (
        <span className="block truncate text-[11px] opacity-80">{activity.campaign_code}</span>
      ) : null}
    </button>
  );
}
