import type { Activity } from "@/types/api";
import { ActivityEntry } from "@/features/calendar/ActivityEntry";
import {
  MONTHS,
  WEEKDAYS,
  activityCovers,
  formatISODate,
  monthWeeks,
} from "@/features/calendar/dates";

export function CalendarYear({
  year,
  activities,
  onSelect,
}: {
  year: number;
  activities: Activity[];
  onSelect: (activity: Activity) => void;
}) {
  return (
    <div className="flex flex-col gap-8">
      {MONTHS.map((month, monthIndex) => {
        const weeks = monthWeeks(year, monthIndex);
        const monthActivities = activities.filter((activity) =>
          weeks.some((week) =>
            week.some((date) => date && activityCovers(activity, formatISODate(date))),
          ),
        );
        return (
          <section key={month} id={`month-${monthIndex + 1}`} className="scroll-mt-4">
            <h2 className="mb-3 text-lg font-semibold">{month}</h2>
            <div className="md:hidden">
              {monthActivities.length === 0 ? (
                <p className="text-sm text-muted-foreground">No activities this month.</p>
              ) : (
                <ul className="flex flex-col gap-3">
                  {weeks.flat().map((date) => {
                    if (!date) return null;
                    const iso = formatISODate(date);
                    const dayActivities = activities.filter((activity) => activityCovers(activity, iso));
                    if (dayActivities.length === 0) return null;
                    return (
                      <li key={iso} className="rounded-md border border-border bg-card p-3">
                        <p className="mb-2 text-sm font-medium">
                          {month} {date.getDate()}
                        </p>
                        <div className="flex flex-col gap-1">
                          {dayActivities.map((activity) => (
                            <ActivityEntry key={activity.id} activity={activity} onSelect={onSelect} />
                          ))}
                        </div>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
            <div className="hidden overflow-x-auto md:block">
              <div className="min-w-[42rem]">
                <div className="grid grid-cols-7 border-b border-border">
                  {WEEKDAYS.map((day) => (
                    <div key={day} className="px-2 py-2 text-xs font-medium text-muted-foreground">
                      {day}
                    </div>
                  ))}
                </div>
                {weeks.map((week, weekIndex) => (
                  <div key={`${month}-${weekIndex}`} className="grid grid-cols-7 border-b border-border">
                    {week.map((date, dayIndex) => {
                      const iso = date ? formatISODate(date) : "";
                      const dayActivities = date
                        ? activities.filter((activity) => activityCovers(activity, iso))
                        : [];
                      return (
                        <div
                          key={`${month}-${weekIndex}-${dayIndex}`}
                          className="min-h-24 border-r border-border bg-card p-1 last:border-r-0"
                        >
                          {date ? (
                            <>
                              <p className="px-1 text-xs text-muted-foreground">{date.getDate()}</p>
                              <div className="mt-1 flex flex-col gap-1">
                                {dayActivities.map((activity) => (
                                  <ActivityEntry
                                    key={activity.id}
                                    activity={activity}
                                    onSelect={onSelect}
                                  />
                                ))}
                              </div>
                            </>
                          ) : null}
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          </section>
        );
      })}
    </div>
  );
}
