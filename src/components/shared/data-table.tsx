import { useMemo, useState, type ReactNode } from "react";
import { ArrowDown, ArrowUp, ArrowUpDown, Columns3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { EmptyState } from "@/components/shared/empty-state";

export type SortValue = string | number | boolean | null;

export type DataColumn<T> = {
  id: string;
  header: string;
  sortable?: boolean;
  hideable?: boolean;
  defaultVisible?: boolean;
  cell: (row: T) => ReactNode;
  sortValue?: (row: T) => SortValue;
};

type SortState = { id: string; direction: "asc" | "desc" } | null;

const PAGE_SIZES = [10, 20, 50] as const;

function compareSortValues(left: SortValue, right: SortValue): number {
  if (left == null && right == null) return 0;
  if (left == null) return 1;
  if (right == null) return -1;
  if (typeof left === "number" && typeof right === "number") return left - right;
  if (typeof left === "boolean" && typeof right === "boolean") return Number(left) - Number(right);
  return String(left).localeCompare(String(right), undefined, {
    numeric: true,
    sensitivity: "base",
  });
}

export function DataTable<T>({
  rows,
  columns,
  getRowId,
  resetKey,
  emptyTitle,
  emptyDescription,
}: {
  rows: T[];
  columns: DataColumn<T>[];
  getRowId: (row: T) => string;
  resetKey: string;
  emptyTitle: string;
  emptyDescription?: string;
}) {
  const [sort, setSort] = useState<SortState>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState<(typeof PAGE_SIZES)[number]>(10);
  const [pageScope, setPageScope] = useState(`${resetKey}:${pageSize}`);
  const [hidden, setHidden] = useState<Record<string, boolean>>(() => {
    const initial: Record<string, boolean> = {};
    for (const column of columns) {
      if (column.hideable && column.defaultVisible === false) initial[column.id] = true;
    }
    return initial;
  });

  const nextScope = `${resetKey}:${pageSize}`;
  if (pageScope !== nextScope) {
    setPageScope(nextScope);
    setPage(1);
  }

  const visibleColumns = columns.filter((column) => !hidden[column.id]);

  const sorted = useMemo(() => {
    if (!sort) return rows;
    const column = columns.find((item) => item.id === sort.id);
    if (!column?.sortValue) return rows;
    const copy = [...rows];
    copy.sort((left, right) => {
      const result = compareSortValues(column.sortValue?.(left) ?? null, column.sortValue?.(right) ?? null);
      return sort.direction === "asc" ? result : -result;
    });
    return copy;
  }, [columns, rows, sort]);

  const pageCount = Math.max(1, Math.ceil(sorted.length / pageSize));
  const currentPage = Math.min(page, pageCount);
  const startIndex = sorted.length === 0 ? 0 : (currentPage - 1) * pageSize;
  const pageRows = sorted.slice(startIndex, startIndex + pageSize);
  const rangeStart = sorted.length === 0 ? 0 : startIndex + 1;
  const rangeEnd = startIndex + pageRows.length;

  function cycleSort(id: string) {
    setSort((current) => {
      if (!current || current.id !== id) return { id, direction: "asc" };
      if (current.direction === "asc") return { id, direction: "desc" };
      return null;
    });
  }

  const pageNumbers = buildPageNumbers(currentPage, pageCount);

  return (
    <div className="rounded-md border border-border bg-card">
      <div className="flex items-center justify-end border-b border-border px-3 py-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button type="button" variant="outline" size="sm">
              <Columns3 aria-hidden />
              Columns
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Columns</DropdownMenuLabel>
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
      </div>
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            {visibleColumns.map((column) => (
              <TableHead key={column.id}>
                {column.sortable ? (
                  <button
                    type="button"
                    className="inline-flex items-center gap-1 rounded-sm text-xs font-medium text-muted-foreground hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
                    aria-sort={
                      sort?.id === column.id
                        ? sort.direction === "asc"
                          ? "ascending"
                          : "descending"
                        : "none"
                    }
                    onClick={() => cycleSort(column.id)}
                  >
                    {column.header}
                    {sort?.id !== column.id ? (
                      <ArrowUpDown className="size-3.5 text-muted-foreground" aria-hidden />
                    ) : sort.direction === "asc" ? (
                      <ArrowUp className="size-3.5" aria-hidden />
                    ) : (
                      <ArrowDown className="size-3.5" aria-hidden />
                    )}
                  </button>
                ) : (
                  column.header
                )}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {pageRows.length === 0 ? (
            <TableRow className="hover:bg-transparent">
              <TableCell colSpan={visibleColumns.length}>
                <EmptyState title={emptyTitle} description={emptyDescription} />
              </TableCell>
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
      <div className="flex flex-col gap-3 border-t border-border px-3 py-3 text-sm sm:flex-row sm:items-center sm:justify-between">
        <p className="text-muted-foreground">
          {rangeStart}–{rangeEnd} of {sorted.length}
        </p>
        <div className="flex flex-wrap items-center gap-2">
          <Select
            value={String(pageSize)}
            onValueChange={(value) => setPageSize(Number(value) as (typeof PAGE_SIZES)[number])}
          >
            <SelectTrigger className="w-[5.5rem]" aria-label="Rows per page">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {PAGE_SIZES.map((size) => (
                <SelectItem key={size} value={String(size)}>
                  {size}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={currentPage <= 1}
            onClick={() => setPage(currentPage - 1)}
          >
            Previous
          </Button>
          {pageNumbers.map((item, index) =>
            item === "gap" ? (
              <span key={`gap-${index}`} className="px-1 text-muted-foreground">
                …
              </span>
            ) : (
              <Button
                key={item}
                type="button"
                size="sm"
                variant={item === currentPage ? "default" : "outline"}
                aria-current={item === currentPage ? "page" : undefined}
                onClick={() => setPage(item)}
              >
                {item}
              </Button>
            ),
          )}
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={currentPage >= pageCount}
            onClick={() => setPage(currentPage + 1)}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}

function buildPageNumbers(current: number, total: number): Array<number | "gap"> {
  if (total <= 7) return Array.from({ length: total }, (_, index) => index + 1);
  const pages = new Set<number>([1, total, current - 1, current, current + 1]);
  const sorted = [...pages].filter((page) => page >= 1 && page <= total).sort((a, b) => a - b);
  const result: Array<number | "gap"> = [];
  for (let index = 0; index < sorted.length; index += 1) {
    const page = sorted[index];
    const previous = sorted[index - 1];
    if (previous !== undefined && page - previous > 1) result.push("gap");
    result.push(page);
  }
  return result;
}
