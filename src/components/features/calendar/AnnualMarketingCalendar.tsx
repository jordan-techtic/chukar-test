import axios from "axios";
import { Eye, MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { ActivityDetailDialog } from "@/components/features/calendar/ActivityDetailDialog";
import { CalendarNavigation } from "@/components/features/calendar/CalendarNavigation";
import { CreateActivityDialog } from "@/components/features/calendar/CreateActivityDialog";
import { EmptyState } from "@/components/features/calendar/EmptyState";
import { ErrorState, ForbiddenState } from "@/components/features/calendar/ErrorState";
import { MonthGrid } from "@/components/features/calendar/MonthGrid";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { DataTable, type DataColumn } from "@/components/shared/data-table";
import { PageHeader } from "@/components/shared/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useCalendar } from "@/hooks/useCalendar";
import { useDeleteActivityAction } from "@/hooks/useActivityMutations";
import { getApiErrorCode, getApiErrorMessage } from "@/lib/api/errors";
import { canMutateActivities, formatDisplayDate, humanize } from "@/lib/format";
import { useAppContext } from "@/stores/AppContext";
import type { ActivityOut } from "@/types/api";

const ALL = "all";

export function AnnualMarketingCalendar() {
  const { user } = useAppContext();
  const canEdit = canMutateActivities(user?.role);
  const [year, setYear] = useState(() => new Date().getFullYear());
  const [focusMonth, setFocusMonth] = useState(() => new Date().getMonth() + 1);
  const [pendingMonth, setPendingMonth] = useState<number | null>(null);
  const [activityType, setActivityType] = useState(ALL);
  const [category, setCategory] = useState(ALL);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const [detailId, setDetailId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const remove = useDeleteActivityAction();

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedSearch(search), 300);
    return () => window.clearTimeout(timer);
  }, [search]);

  const query = useCalendar(
    {
      year,
      activity_type: activityType === ALL ? undefined : activityType,
      category: category === ALL ? undefined : category,
    },
    true,
  );

  const calendar = query.data?.data;
  const activities = useMemo(() => calendar?.activities ?? [], [calendar]);
  const forbidden =
    axios.isAxiosError(query.error) &&
    (query.error.response?.status === 403 || getApiErrorCode(query.error) === "FORBIDDEN");

  useEffect(() => {
    if (!pendingMonth || query.isFetching) return;
    document.getElementById(`month-${pendingMonth}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
    setPendingMonth(null);
  }, [pendingMonth, query.isFetching, calendar]);

  const filtered = useMemo(() => {
    const term = debouncedSearch.trim().toLowerCase();
    if (!term) return activities;
    return activities.filter((activity) =>
      [activity.title, activity.activity_type, activity.category, activity.campaign_code, activity.status]
        .join(" ")
        .toLowerCase()
        .includes(term),
    );
  }, [activities, debouncedSearch]);

  const categories = useMemo(() => {
    const values = new Set<string>();
    for (const option of calendar?.activity_types ?? []) values.add(option.category);
    for (const activity of activities) if (activity.category) values.add(activity.category);
    return [...values].sort((a, b) => a.localeCompare(b));
  }, [calendar?.activity_types, activities]);

  function scrollToMonth(month: number) {
    const next = Math.min(12, Math.max(1, month));
    setFocusMonth(next);
    document.getElementById(`month-${next}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function goToday() {
    const today = calendar?.today ?? new Date().toISOString().slice(0, 10);
    const [todayYear, todayMonth] = today.split("-").map((part) => Number(part));
    setFocusMonth(todayMonth);
    if (todayYear === year) scrollToMonth(todayMonth);
    else {
      setYear(todayYear);
      setPendingMonth(todayMonth);
    }
  }

  async function confirmDelete() {
    if (!deleteId) return;
    try {
      const result = await remove.mutateAsync(deleteId);
      toast.success(result.message || "Activity deleted successfully.");
      setDeleteId(null);
      if (detailId === deleteId) setDetailId(null);
    } catch (error) {
      if (getApiErrorCode(error) === "ACTIVITY_PUBLISHED") {
        toast.error(getApiErrorMessage(error));
        return;
      }
      toast.error(getApiErrorMessage(error, "Unable to delete the activity. Please try again."));
    }
  }

  const columns: DataColumn<ActivityOut>[] = [
    {
      id: "title",
      header: "Title",
      sortable: true,
      sortValue: (row) => row.title,
      cell: (row) => <span className="font-medium">{row.title}</span>,
    },
    {
      id: "date",
      header: "Date",
      sortable: true,
      hideable: true,
      sortValue: (row) => row.start_date,
      cell: (row) => formatDisplayDate(row.start_date),
    },
    {
      id: "end_date",
      header: "End Date",
      sortable: true,
      hideable: true,
      sortValue: (row) => row.end_date,
      cell: (row) => formatDisplayDate(row.end_date),
    },
    {
      id: "activity_type",
      header: "Activity Type",
      sortable: true,
      hideable: true,
      sortValue: (row) => row.activity_type,
      cell: (row) => humanize(row.activity_type),
    },
    {
      id: "category",
      header: "Category",
      sortable: true,
      hideable: true,
      sortValue: (row) => row.category,
      cell: (row) => humanize(row.category),
    },
    {
      id: "status",
      header: "Status",
      sortable: true,
      hideable: true,
      sortValue: (row) => row.status,
      cell: (row) => (
        <Badge variant={row.status === "published" ? "success" : row.status === "pending" ? "warning" : "secondary"}>
          {humanize(row.status)}
        </Badge>
      ),
    },
    {
      id: "campaign_code",
      header: "Campaign Code",
      sortable: true,
      hideable: true,
      sortValue: (row) => row.campaign_code,
      cell: (row) => row.campaign_code,
    },
    {
      id: "organization",
      header: "Organization",
      hideable: true,
      sortable: true,
      sortValue: (row) => row.organization,
      cell: (row) => row.organization,
    },
    {
      id: "role",
      header: "Role",
      hideable: true,
      sortable: true,
      sortValue: (row) => row.role,
      cell: (row) => humanize(row.role),
    },
    {
      id: "details",
      header: "Details",
      hideable: true,
      sortable: true,
      sortValue: (row) => row.details,
      cell: (row) => row.details ?? "—",
    },
    {
      id: "actions",
      header: "Actions",
      cell: (row) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button type="button" variant="ghost" size="icon" aria-label={`Actions for ${row.title}`}>
              <MoreHorizontal aria-hidden="true" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onSelect={() => setDetailId(row.id)}>
              <Eye className="size-4" aria-hidden="true" />
              View
            </DropdownMenuItem>
            {canEdit ? (
              <DropdownMenuItem onSelect={() => setDetailId(row.id)}>
                <Pencil className="size-4" aria-hidden="true" />
                Edit
              </DropdownMenuItem>
            ) : null}
            {canEdit && row.status !== "published" ? (
              <DropdownMenuItem className="text-destructive" onSelect={() => setDeleteId(row.id)}>
                <Trash2 className="size-4" aria-hidden="true" />
                Delete
              </DropdownMenuItem>
            ) : null}
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ];

  return (
    <div className="space-y-4 p-4 md:p-6" aria-busy={query.isPending || undefined}>
      <PageHeader
        title="Annual Marketing Calendar"
        description="Plan and review marketing activities across the year."
      />
      <div className="sticky top-0 z-10 -mx-4 border-b border-border bg-background px-4 py-3 md:-mx-6 md:px-6">
        <div className="flex flex-wrap items-center gap-2">
          <CalendarNavigation
            year={calendar?.year ?? year}
            onPreviousYear={() => setYear((current) => current - 1)}
            onNextYear={() => setYear((current) => current + 1)}
            onToday={goToday}
            onPreviousMonth={() => scrollToMonth(focusMonth - 1)}
            onNextMonth={() => scrollToMonth(focusMonth + 1)}
          />
          <Input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search activities"
            aria-label="Search activities"
            className="h-10 w-full sm:w-56"
          />
          <Select value={activityType} onValueChange={setActivityType}>
            <SelectTrigger aria-label="Activity type" className="w-full sm:w-48">
              <SelectValue placeholder="Activity type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={ALL}>All types</SelectItem>
              {(calendar?.activity_types ?? []).map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={category} onValueChange={setCategory}>
            <SelectTrigger aria-label="Category" className="w-full sm:w-44">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={ALL}>All categories</SelectItem>
              {categories.map((value) => (
                <SelectItem key={value} value={value}>
                  {humanize(value)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {canEdit ? (
            <Button type="button" className="sm:ml-auto" onClick={() => setCreateOpen(true)}>
              Add Activity
            </Button>
          ) : null}
        </div>
      </div>

      {calendar ? (
        <p className="text-sm text-muted-foreground">
          {calendar.organization} · {humanize(calendar.role)} · Week starts {calendar.week_start}
        </p>
      ) : null}

      {query.isPending ? (
        <div className="grid gap-4 xl:grid-cols-3" aria-busy="true">
          {Array.from({ length: 6 }, (_, index) => (
            <Skeleton key={index} className="h-64" />
          ))}
          <span className="sr-only">Loading calendar</span>
        </div>
      ) : forbidden ? (
        <ForbiddenState />
      ) : query.isError ? (
        <ErrorState
          message={getApiErrorMessage(query.error, "Unable to load the calendar. Please try again.")}
          onRetry={() => {
            void query.refetch();
          }}
        />
      ) : (
        <div className="space-y-4">
          {activities.length === 0 ? <EmptyState year={calendar?.year ?? year} /> : null}
          <div className="grid gap-4 xl:grid-cols-3">
            {Array.from({ length: 12 }, (_, index) => (
              <MonthGrid
                key={index + 1}
                year={calendar?.year ?? year}
                month={index + 1}
                today={calendar?.today ?? ""}
                activities={filtered}
                onOpen={(activity) => setDetailId(activity.id)}
              />
            ))}
          </div>
          <DataTable
            key={`${debouncedSearch}-${activityType}-${category}-${year}`}
            columns={columns}
            rows={filtered}
            getRowId={(row) => row.id}
            empty={<p className="py-6 text-sm text-muted-foreground">No activities match these filters.</p>}
          />
        </div>
      )}

      <CreateActivityDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        activityTypes={calendar?.activity_types ?? []}
      />
      <ActivityDetailDialog
        activityId={detailId}
        open={Boolean(detailId)}
        canEdit={canEdit}
        activityTypes={calendar?.activity_types ?? []}
        onOpenChange={(next) => {
          if (!next) setDetailId(null);
        }}
        onMissing={() => {
          void query.refetch();
        }}
      />
      <ConfirmDialog
        open={Boolean(deleteId)}
        title="Delete activity?"
        description="This will permanently delete the activity. This action cannot be undone."
        confirmLabel="Delete"
        pendingLabel="Deleting…"
        isLoading={remove.isPending}
        onOpenChange={(next) => {
          if (!next) setDeleteId(null);
        }}
        onConfirm={() => {
          void confirmDelete();
        }}
      />
    </div>
  );
}
