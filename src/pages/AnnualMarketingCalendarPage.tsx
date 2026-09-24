import { useMemo, useState } from 'react';
import type { ActivityOut } from '@/types/api';
import { useCalendar } from '@/hooks/useCalendar';
import { parseIsoDate } from '@/lib/calendar-utils';
import { Spinner } from '@/components/ui/spinner';
import { CalendarNavigationControls } from '@/components/features/calendar/CalendarNavigationControls';
import { CalendarFilters } from '@/components/features/calendar/CalendarFilters';
import { AnnualCalendarGrid } from '@/components/features/calendar/AnnualCalendarGrid';
import { EmptyCalendarState } from '@/components/features/calendar/EmptyCalendarState';
import { CalendarErrorState } from '@/components/features/calendar/CalendarErrorState';
import { ActivityFormModal } from '@/components/features/calendar/ActivityFormModal';
import { getApiErrorMessage } from '@/lib/api/errors';

export function AnnualMarketingCalendarPage() {
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedActivityTypes, setSelectedActivityTypes] = useState<string[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingActivityId, setEditingActivityId] = useState<string | null>(null);

  const { data, isLoading, isError, error, refetch } = useCalendar({
    year,
    month,
    category: selectedCategories.length > 0 ? selectedCategories : undefined,
    activity_type: selectedActivityTypes.length > 0 ? selectedActivityTypes : undefined,
  });

  const metaLine = useMemo(() => {
    if (!data) return null;
    return [data.organization, data.role].filter(Boolean).join(' · ');
  }, [data]);

  const handleToday = () => {
    const todayStr = data?.today ?? `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    const parsed = parseIsoDate(todayStr);
    setYear(parsed.getFullYear());
    setMonth(parsed.getMonth() + 1);
  };

  const handleCreateActivity = () => {
    setEditingActivityId(null);
    setModalOpen(true);
  };

  const handleActivityClick = (activity: ActivityOut) => {
    setEditingActivityId(activity.id);
    setModalOpen(true);
  };

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Spinner label="Loading calendar" />
      </div>
    );
  }

  if (isError) {
    return (
      <CalendarErrorState
        message={getApiErrorMessage(error, 'Unable to load calendar. Please try again.')}
        onRetry={() => void refetch()}
      />
    );
  }

  const activities = data?.activities ?? [];
  const activityTypes = data?.activity_types ?? [];
  const todayIso = data?.today ?? '';

  return (
    <div>
      <div className="mb-6 flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight md:text-[28px] md:leading-9">
            Marketing Content Calendar
          </h1>
          {metaLine ? <p className="mt-1 text-sm text-muted-foreground">{metaLine}</p> : null}
        </div>
        <CalendarNavigationControls
          year={year}
          month={month}
          onYearChange={setYear}
          onMonthChange={setMonth}
          onToday={handleToday}
          onCreateActivity={handleCreateActivity}
        />
      </div>

      <div className="mb-4">
        <CalendarFilters
          activityTypes={activityTypes}
          selectedCategories={selectedCategories}
          selectedActivityTypes={selectedActivityTypes}
          onCategoriesChange={setSelectedCategories}
          onActivityTypesChange={setSelectedActivityTypes}
        />
      </div>

      {activities.length === 0 ? (
        <EmptyCalendarState />
      ) : (
        <AnnualCalendarGrid
          year={year}
          month={month}
          today={todayIso}
          activities={activities}
          onActivityClick={handleActivityClick}
        />
      )}

      <ActivityFormModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        activityId={editingActivityId}
        activityTypes={activityTypes}
      />
    </div>
  );
}
