import { ArrowDown, ArrowUp, ArrowUpDown, Columns3 } from "lucide-react";
import { useMemo, useState, type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { cn } from "@/lib/cn";

export interface DataColumn<T> {
  id: string;
  header: string;
  sortable?: boolean;
  hideable?: boolean;
  cell: (row: T) => ReactNode;
  sortValue?: (row: T) => string | number | boolean | null;
}

type SortState = { id: string; direction: "asc" | "desc" } | null;

interface DataTableProps<T> {
  columns: DataColumn<T>[];
  rows: T[];
  getRowId: (row: T) => string;
  toolbar?: ReactNode;
  empty?: ReactNode;
  pageSizeOptions?: number[];
}

function compareValues(left: string | number | boolean | null, right: string | number | boolean | null): number {
  if (left === null && right === null) return 0;
  if (left === null) return 1;
  if (right === null) return -1;
  if (typeof left === "boolean" && typeof right === "boolean") return Number(left) - Number(right);
  if (typeof left === "number" && typeof right === "number") return left - right;
  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: "base" });
}

export function DataTable<T>({
  columns,
  rows,
  getRowId,
  toolbar,
  empty,
  pageSizeOptions = [10, 20, 50],
}: DataTableProps<T>) {
  const [sort, setSort] = useState<SortState>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(pageSizeOptions[0] ?? 10);
  const [hidden, setHidden] = useState<Record<string, boolean>>({});

  const visibleColumns = columns.filter((column) => !column.hideable || !hidden[column.id]);

  const sorted = useMemo(() => {
    if (!sort) return rows;
    const column = columns.find((item) => item.id === sort.id);
    if (!column?.sortValue) return rows;
    const next = [...rows].sort((a, b) => compareValues(column.sortValue?.(a) ?? null, column.sortValue?.(b) ?? null));
    return sort.direction === "desc" ? next.reverse() : next;
  }, [columns, rows, sort]);

  const pageCount = Math.max(1, Math.ceil(sorted.length / pageSize));
  const safePage = Math.min(page, pageCount);
  const start = sorted.length === 0 ? 0 : (safePage - 1) * pageSize;
  const pageRows = sorted.slice(start, start + pageSize);

  function cycleSort(id: string) {
    setSort((current) => {
      if (!current || current.id !== id) return { id, direction: "asc" };
      if (current.direction === "asc") return { id, direction: "desc" };
      return null;
    });
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">{toolbar}</div>
      <div className="overflow-hidden rounded-lg border border-border bg-card">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-muted">
              {visibleColumns.map((column) => {
                const active = sort?.id === column.id ? sort.direction : null;
                return (
                  <TableHead key={column.id} aria-sort={active === "asc" ? "ascending" : active === "desc" ? "descending" : "none"}>
                    {column.sortable ? (
                      <button
                        type="button"
                        className="inline-flex items-center gap-1 rounded-sm font-medium text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                        onClick={() => cycleSort(column.id)}
                      >
                        {column.header}
                        {active === "asc" ? (
                          <ArrowUp className="size-3.5" aria-hidden="true" />
                        ) : active === "desc" ? (
                          <ArrowDown className="size-3.5" aria-hidden="true" />
                        ) : (
                          <ArrowUpDown className="size-3.5 opacity-70" aria-hidden="true" />
                        )}
                      </button>
                    ) : (
                      column.header
                    )}
                  </TableHead>
                );
              })}
            </TableRow>
          </TableHeader>
          <TableBody>
            {pageRows.length === 0 ? (
              <TableRow className="hover:bg-transparent">
                <TableCell colSpan={visibleColumns.length}>{empty}</TableCell>
              </TableRow>
            ) : (
              pageRows.map((row) => (
                <TableRow key={getRowId(row)}>
                  {visibleColumns.map((column) => (
                    <TableCell key={column.id}>{column.cell(row)}</TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
        <p className="text-muted-foreground">
          {sorted.length === 0
            ? "0 of 0"
            : `${start + 1}–${Math.min(start + pageSize, sorted.length)} of ${sorted.length}`}
        </p>
        <div className="flex flex-wrap items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" type="button">
                <Columns3 className="size-4" aria-hidden="true" />
                Columns
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {columns
                .filter((column) => column.hideable)
                .map((column) => (
                  <DropdownMenuCheckboxItem
                    key={column.id}
                    checked={!hidden[column.id]}
                    onCheckedChange={(checked) =>
                      setHidden((current) => ({ ...current, [column.id]: checked !== true }))
                    }
                    onSelect={(event) => event.preventDefault()}
                  >
                    {column.header}
                  </DropdownMenuCheckboxItem>
                ))}
            </DropdownMenuContent>
          </DropdownMenu>
          <Select
            value={String(pageSize)}
            onValueChange={(value) => {
              setPageSize(Number(value));
              setPage(1);
            }}
          >
            <SelectTrigger aria-label="Rows per page" className="h-8 w-[110px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {pageSizeOptions.map((size) => (
                <SelectItem key={size} value={String(size)}>
                  {size} / page
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <nav aria-label="Pagination" className="flex items-center gap-1">
            {Array.from({ length: pageCount }, (_, index) => index + 1).map((number) => (
              <button
                key={number}
                type="button"
                aria-current={number === safePage ? "page" : undefined}
                className={cn(
                  "inline-flex h-8 min-w-8 items-center justify-center rounded-md px-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  number === safePage ? "bg-primary text-primary-foreground" : "text-foreground hover:bg-muted",
                )}
                onClick={() => setPage(number)}
              >
                {number}
              </button>
            ))}
          </nav>
        </div>
      </div>
    </div>
  );
}
