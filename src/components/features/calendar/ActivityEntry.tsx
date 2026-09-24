import type { ActivityOut } from '@/types/api';
import { cn } from '@/lib/utils';

interface ActivityEntryProps {
  activity: ActivityOut;
  onClick: (activity: ActivityOut) => void;
}

export function ActivityEntry({ activity, onClick }: ActivityEntryProps) {
  return (
    <button
      type="button"
      onClick={() => onClick(activity)}
      className={cn(
        'mb-1 w-full truncate rounded-md px-2 py-1 text-left text-xs text-white',
        'cursor-pointer hover:brightness-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1',
      )}
      style={{ backgroundColor: activity.color }}
      title={activity.title}
    >
      {activity.title}
    </button>
  );
}
