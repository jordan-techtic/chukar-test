import { useEffect, useMemo, useRef, useState } from "react";
import { Eye, MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { ErrorMessage } from "@/components/shared/error-message";
import { PageHeader } from "@/components/shared/page-header";
import { DataTable, type DataColumn } from "@/components/shared/data-table";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { getApiErrorMessage } from "@/lib/api/errors";
import { humanizeEnum, joinMeta } from "@/lib/utils";
import { ActivityFormDialog } from "@/features/calendar/ActivityFormDialog";
import { CalendarNavigation } from "@/features/calendar/CalendarNavigation";
import { CalendarYear } from "@/features/calendar/CalendarYear";
import { clampYear, parseISODate } from "@/features/calendar/dates";
import { useCalendar } from "@/features/calendar/use-calendar";
import { useDeleteActivity } from "@/features/calendar/use-activity-mutations";
import { useAuth } from "@/stores/AppContext";
import type { Activity } from "@/types/api";
import { toast } from "@/components/ui/toast";

function statusVariant(status: Activity["status"]): "warning" | "success" | "secondary" {
  if (status === "published") return "success";
  if (status === "pending") return "warning";
  return "secondary";
}

export function CalendarPage() {
  const { authenticated } = useAuth();
  const [year, setYear] = useState(() => clampYear(new Date().getFullYear()));
  const [category, setCategory] = useState("");
  const [activityType, setActivityType] = useState("");
  const pendingMonth = useRef<number | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const calendar = useCalendar(
    year,
    { category: category || undefined, activity_type: activityType || undefined },
    authenticated,
  );
  const deleteActivity = useDeleteActivity(deleteId ?? "new");
  const data = calendar.data?.data;
  const activities = data?.activities ?? [];

  useEffect(() => {
    const month = pendingMonth.current;
    if (month == null || !data) return;
    document.getElementById(`month-${month}`)?.scrollIntoView({ block: "start" });
    pendingMonth.current = null;
  }, [data]);

  const categories = useMemo(() => {
    const values = new Set<string>();
    for (const option of data?.activity_types ?? []) {
      if (option.category) values.add(option.category);
    }
    if (category) values.add(category);
    return [...values].sort((a, b) => a.localeCompare(b));
  }, [category, data?.activity_types]);

  const typeOptions = useMemo(() => {
    const values = new Map<string, string>();
    for (const option of data?.activity_types ?? []) values.set(option.value, option.label);
    if (activityType && !values.has(activityType)) values.set(activityType, humanizeEnum(activityType));
    return [...values.entries()];
  }, [activityType, data?.activity_types]);

  function openCreate() {
    setEditingId(null);
    setDialogOpen(true);
  }

  function openEdit(activity: Activity) {
    setEditingId(activity.id);
    setDialogOpen(true);
  }

  function goToday() {
    const today = data?.today ? parseISODate(data.today) : new Date();
    const next = today ?? new Date();
    const month = next.getMonth() + 1;
    pendingMonth.current = month;
    setYear(clampYear(next.getFullYear()));
    const node = document.getElementById(`month-${month}`);
    if (node) {
      node.scrollIntoView({ block: "start" });
      pendingMonth.current = null;
    }
  }

  const description = joinMeta([
    data?.organization,
    data?.role ? humanizeEnum(data.role) : "",
    data?.week_start ? humanizeEnum(data.week_start) : "",
  ]);

  const columns: DataColumn<Activity>[] = [
    {
      id: "title",
      header: "Title",
      sortable: true,
      hideable: false,
      sortValue: (row) => row.title,
      cell: (row) => <span className="font-medium">{row.title}</span>,
    },
    {
      id: "start_date",
      header: "Start date",
      sortable: true,
      hideable: true,
      sortValue: (row) => row.start_date,
      cell: (row) => row.start_date,
    },
    {
      id: "end_date",
      header: "End date",
      sortable: true,
      hideable: true,
      sortValue: (row) => row.end_date,
      cell: (row) => row.end_date,
    },
    {
      id: "activity_type",
      header: "Type",
      sortable: true,
      hideable: true,
      sortValue: (row) => row.activity_type,
      cell: (row) => humanizeEnum(row.activity_type),
    },
    {
      id: "status",
      header: "Status",
      sortable: true,
      hideable: true,
      sortValue: (row) => row.status,
      cell: (row) => <Badge variant={statusVariant(row.status)}>{humanizeEnum(row.status)}</Badge>,
    },
    {
      id: "category",
      header: "Category",
      sortable: true,
      hideable: true,
      defaultVisible: false,
      sortValue: (row) => row.category,
      cell: (row) => humanizeEnum(row.category),
    },
    {
      id: "campaign_code",
      header: "Campaign code",
      sortable: true,
      hideable: true,
      sortValue: (row) => row.campaign_code,
      cell: (row) => row.campaign_code,
    },
    {
      id: "organization",
      header: "Organization",
      sortable: true,
      hideable: true,
      defaultVisible: false,
      sortValue: (row) => row.organization,
      cell: (row) => row.organization,
    },
    {
      id: "role",
      header: "Role",
      sortable: true,
      hideable: true,
      defaultVisible: false,
      sortValue: (row) => row.role,
      cell: (row) => humanizeEnum(row.role),
    },
    {
      id: "actions",
      header: "Actions",
      hideable: false,
      cell: (row) => (
        <DropdownMenu>
          <Tooltip>
            <TooltipTrigger asChild>
              <DropdownMenuTrigger asChild>
                <Button type="button" variant="ghost" size="icon" aria-label={`Actions for ${row.title}`}>
                  <MoreHorizontal aria-hidden />
                </Button>
              </DropdownMenuTrigger>
            </TooltipTrigger>
            <TooltipContent>Actions</TooltipContent>
          </Tooltip>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onSelect={() => openEdit(row)}>
              <Eye aria-hidden />
              View
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => openEdit(row)}>
              <Pencil aria-hidden />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-destructive focus:text-destructive"
              onSelect={() => setDeleteId(row.id)}
            >
              <Trash2 aria-hidden />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ];

  async function confirmDelete() {
    if (!deleteId) return;
    try {
      const result = await deleteActivity.mutateAsync();
      toast.success(result.message);
      setDeleteId(null);
    } catch (error) {
      toast.error(getApiErrorMessage(error));
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <PageHeader title="Annual marketing calendar" description={description || undefined} />
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <CalendarNavigation
          year={year}
          onYearChange={(next) => setYear(clampYear(next))}
          onToday={goToday}
          onMonthSelect={(month) => {
            const node = document.getElementById(`month-${month}`);
            if (node) {
              node.scrollIntoView({ block: "start" });
              pendingMonth.current = null;
              return;
            }
            pendingMonth.current = month;
          }}
        />
        <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
          <Select value={category || "all"} onValueChange={(value) => setCategory(value === "all" ? "" : value)}>
            <SelectTrigger className="w-full sm:w-44" aria-label="Category">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All categories</SelectItem>
              {categories.map((value) => (
                <SelectItem key={value} value={value}>
                  {humanizeEnum(value)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={activityType || "all"}
            onValueChange={(value) => setActivityType(value === "all" ? "" : value)}
          >
            <SelectTrigger className="w-full sm:w-48" aria-label="Activity type">
              <SelectValue placeholder="Activity type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All activity types</SelectItem>
              {typeOptions.map(([value, label]) => (
                <SelectItem key={value} value={value}>
                  {label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button type="button" onClick={openCreate}>
            Add Activity
          </Button>
        </div>
      </div>
      {calendar.isFetching && !calendar.isLoading ? (
        <p className="text-sm text-muted-foreground" role="status">
          Updating calendar…
        </p>
      ) : null}
      {calendar.isLoading ? (
        <div className="grid gap-3">
          <Spinner label="Loading calendar" />
          <Skeleton className="h-8 w-40" />
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-48 w-full" />
        </div>
      ) : null}
      {calendar.isError ? (
        <ErrorMessage
          message={
            getApiErrorMessage(calendar.error) === "Something went wrong. Please try again."
              ? "Could not load the calendar."
              : getApiErrorMessage(calendar.error)
          }
          onRetry={() => void calendar.refetch()}
        />
      ) : null}
      {!calendar.isLoading && !calendar.isError && data ? (
        <>
          {activities.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No marketing activities are scheduled for {data.year}.
            </p>
          ) : null}
          <CalendarYear year={data.year} activities={activities} onSelect={openEdit} />
          <DataTable
            rows={activities}
            columns={columns}
            getRowId={(row) => row.id}
            resetKey={`${year}:${category}:${activityType}`}
            emptyTitle="No activities found."
            emptyDescription="Activities you add will show up in this list."
          />
        </>
      ) : null}
      <ActivityFormDialog
        open={dialogOpen}
        activityId={editingId}
        activityTypes={data?.activity_types ?? []}
        onOpenChange={setDialogOpen}
      />
      <ConfirmDialog
        open={Boolean(deleteId)}
        title="Delete activity?"
        description="This will permanently delete the activity. This action cannot be undone."
        confirmLabel="Delete"
        pendingLabel="Deleting…"
        destructive
        isLoading={deleteActivity.isPending}
        onOpenChange={(open) => {
          if (!open) setDeleteId(null);
        }}
        onConfirm={() => void confirmDelete()}
      />
    </div>
  );
}
