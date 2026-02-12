import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  useReactTable,
  getCoreRowModel,
  type ColumnDef,
  type SortingState,
  flexRender,
} from '@tanstack/react-table';
import { ArrowUpDown, ArrowUp, ArrowDown, ChevronLeft, ChevronRight, AlertCircle, Search, X } from 'lucide-react';
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '../ui/table';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import {
  useEvaluationHistory,
  type SortBy,
  type SortOrder,
} from '../../hooks/useEvaluationHistory';

const dateFormatter = new Intl.DateTimeFormat('id-ID', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  timeZone: 'Asia/Jakarta',
});

function formatTemplate(template: string): string {
  return template === 'non_fashion' ? 'Non-Fashion' : 'Fashion';
}

interface EvaluationRow {
  id: number;
  brand_name: string;
  final_score: number;
  verdict: string;
  template: string;
  evaluator_email: string;
  created_at: string;
}

const columns: ColumnDef<EvaluationRow>[] = [
  {
    accessorKey: 'brand_name',
    header: 'Brand',
    enableSorting: false,
  },
  {
    accessorKey: 'final_score',
    header: 'Score',
    enableSorting: true,
    cell: ({ row }) => (
      <span className="font-mono">
        {row.original.final_score.toFixed(2)} {row.original.verdict}
      </span>
    ),
  },
  {
    accessorKey: 'template',
    header: 'Template',
    enableSorting: false,
    cell: ({ row }) => (
      <Badge variant="secondary">{formatTemplate(row.original.template)}</Badge>
    ),
  },
  {
    accessorKey: 'evaluator_email',
    header: 'Evaluator',
    enableSorting: false,
  },
  {
    accessorKey: 'created_at',
    header: 'Date',
    enableSorting: true,
    cell: ({ row }) => dateFormatter.format(new Date(row.original.created_at)),
  },
];

function SearchInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="relative mb-4 max-w-sm">
      <Search
        className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
        aria-hidden="true"
      />
      <Input
        aria-label="Search evaluations by brand name"
        placeholder="Search by brand name..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="pl-9 pr-9"
      />
      {value && (
        <Button
          variant="ghost"
          size="sm"
          className="absolute right-1 top-1/2 size-7 -translate-y-1/2 p-0"
          aria-label="Clear search"
          onClick={() => onChange('')}
        >
          <X className="size-4" aria-hidden="true" />
        </Button>
      )}
    </div>
  );
}

export const EvaluationHistoryTable = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const page = Math.max(1, Number(searchParams.get('page')) || 1);
  const limit = 20;
  const sortBy: SortBy =
    (searchParams.get('sort_by') as SortBy) || 'created_at';
  const sortOrder: SortOrder =
    (searchParams.get('sort_order') as SortOrder) || 'desc';
  const searchFromUrl = searchParams.get('search') ?? '';

  const [searchInput, setSearchInput] = useState(searchFromUrl);
  const isInitialMount = useRef(true);

  // Debounce: update URL params after 300ms idle (skip initial mount)
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    const timer = setTimeout(() => {
      setSearchParams((prev) => {
        const p = new URLSearchParams(prev);
        if (searchInput) {
          p.set('search', searchInput);
        } else {
          p.delete('search');
        }
        p.delete('page'); // Reset page on search change
        return p;
      }, { replace: true });
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput, setSearchParams]);

  // Sync input when URL changes externally (e.g., browser back)
  useEffect(() => {
    setSearchInput(searchFromUrl);
  }, [searchFromUrl]);

  const sorting: SortingState = [
    { id: sortBy, desc: sortOrder === 'desc' },
  ];

  const setPage = useCallback(
    (updater: number | ((prev: number) => number)) => {
      const next = typeof updater === 'function' ? updater(page) : updater;
      setSearchParams((prev) => {
        const p = new URLSearchParams(prev);
        if (next <= 1) p.delete('page');
        else p.set('page', String(next));
        return p;
      });
    },
    [page, setSearchParams],
  );

  const setSorting = useCallback(
    (updater: SortingState | ((old: SortingState) => SortingState)) => {
      const next = typeof updater === 'function' ? updater(sorting) : updater;
      const newSortBy = (next[0]?.id as SortBy) || 'created_at';
      const newSortOrder: SortOrder = next[0]?.desc ? 'desc' : 'asc';
      setSearchParams((prev) => {
        const p = new URLSearchParams(prev);
        // Reset page on sort change
        p.delete('page');
        if (newSortBy === 'created_at') p.delete('sort_by');
        else p.set('sort_by', newSortBy);
        if (newSortOrder === 'desc') p.delete('sort_order');
        else p.set('sort_order', newSortOrder);
        return p;
      });
    },
    [sorting, setSearchParams],
  );

  const {
    evaluations,
    total,
    pages,
    isLoading,
    isError,
    error,
    refetch,
    isPlaceholderData,
  } = useEvaluationHistory(page, limit, sortBy, sortOrder, searchFromUrl || undefined);

  const table = useReactTable({
    data: evaluations,
    columns,
    getCoreRowModel: getCoreRowModel(),
    manualPagination: true,
    manualSorting: true,
    pageCount: pages,
    state: {
      sorting,
      pagination: { pageIndex: page - 1, pageSize: limit },
    },
    onSortingChange: setSorting,
  });

  if (isError) {
    return (
      <div className="flex flex-col items-center gap-3 py-16 text-center">
        <AlertCircle className="size-10 text-destructive" aria-hidden="true" />
        <p className="text-muted-foreground">
          {error?.message || 'Failed to load evaluations'}
        </p>
        <Button variant="outline" onClick={() => refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  if (!isLoading && evaluations.length === 0 && total === 0) {
    return (
      <div>
        <SearchInput
          value={searchInput}
          onChange={setSearchInput}
        />
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <p className="text-muted-foreground">
            {searchFromUrl
              ? `No evaluations found for '${searchFromUrl}'`
              : 'No evaluations found'}
          </p>
          {!searchFromUrl && (
            <p className="text-sm text-muted-foreground">
              Start evaluating brands to see history here.
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div>
      <SearchInput
        value={searchInput}
        onChange={setSearchInput}
        isLoading={isLoading || isPlaceholderData}
      />
      <Table
        aria-label="Evaluation history"
        aria-busy={isLoading || isPlaceholderData}
        className={isPlaceholderData ? 'opacity-60 transition-opacity' : ''}
      >
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <TableHead key={header.id} className="text-xs uppercase">
                  {header.column.getCanSort() ? (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="-ml-3 h-8 text-xs uppercase"
                      aria-label={`Sort by ${header.column.columnDef.header}${header.column.getIsSorted() === 'asc' ? ', sorted ascending' : header.column.getIsSorted() === 'desc' ? ', sorted descending' : ''}`}
                      onClick={() =>
                        header.column.toggleSorting(
                          header.column.getIsSorted() === 'asc',
                        )
                      }
                    >
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext(),
                      )}
                      {header.column.getIsSorted() === 'asc' ? (
                        <ArrowUp className="ml-1 size-3.5" aria-hidden="true" />
                      ) : header.column.getIsSorted() === 'desc' ? (
                        <ArrowDown className="ml-1 size-3.5" aria-hidden="true" />
                      ) : (
                        <ArrowUpDown className="ml-1 size-3.5" aria-hidden="true" />
                      )}
                    </Button>
                  ) : (
                    flexRender(
                      header.column.columnDef.header,
                      header.getContext(),
                    )
                  )}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {isLoading
            ? Array.from({ length: 10 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><div className="h-4 w-32 animate-pulse rounded bg-muted" /></TableCell>
                  <TableCell><div className="h-4 w-20 animate-pulse rounded bg-muted" /></TableCell>
                  <TableCell><div className="h-4 w-20 animate-pulse rounded bg-muted" /></TableCell>
                  <TableCell><div className="h-4 w-36 animate-pulse rounded bg-muted" /></TableCell>
                  <TableCell><div className="h-4 w-28 animate-pulse rounded bg-muted" /></TableCell>
                </TableRow>
              ))
            : table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.original.id}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => navigate(`/history/${row.original.id}`)}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
        </TableBody>
      </Table>

      {!isLoading && total > 0 && (
        <div className="flex items-center justify-center gap-4 py-4">
          {pages > 1 && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
            >
              <ChevronLeft className="size-4" aria-hidden="true" />
              Previous
            </Button>
          )}
          <span className="text-sm text-muted-foreground">
            {pages > 1 ? `Page ${page} of ${pages}` : `${total} evaluation${total !== 1 ? 's' : ''}`}
          </span>
          {pages > 1 && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(pages, p + 1))}
              disabled={page >= pages}
            >
              Next
              <ChevronRight className="size-4" aria-hidden="true" />
            </Button>
          )}
        </div>
      )}
    </div>
  );
};
