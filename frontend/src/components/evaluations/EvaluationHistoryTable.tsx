import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  useReactTable,
  getCoreRowModel,
  type ColumnDef,
  type SortingState,
  flexRender,
} from '@tanstack/react-table';
import { ArrowUpDown, ArrowUp, ArrowDown, ChevronLeft, ChevronRight, AlertCircle } from 'lucide-react';
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

export const EvaluationHistoryTable = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const limit = 20;
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'created_at', desc: true },
  ]);

  const sortBy: SortBy = (sorting[0]?.id as SortBy) || 'created_at';
  const sortOrder: SortOrder = sorting[0]?.desc ? 'desc' : 'asc';

  const {
    evaluations,
    total,
    pages,
    isLoading,
    isError,
    error,
    refetch,
    isPlaceholderData,
  } = useEvaluationHistory(page, limit, sortBy, sortOrder);

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
    onSortingChange: (updater) => {
      setSorting(updater);
      setPage(1);
    },
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
      <div className="flex flex-col items-center gap-3 py-16 text-center">
        <p className="text-muted-foreground">No evaluations found</p>
        <p className="text-sm text-muted-foreground">
          Start evaluating brands to see history here.
        </p>
      </div>
    );
  }

  return (
    <div>
      <Table
        aria-label="Evaluation history"
        aria-busy={isLoading}
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
                        <ArrowUp className="ml-1 size-3.5" />
                      ) : header.column.getIsSorted() === 'desc' ? (
                        <ArrowDown className="ml-1 size-3.5" />
                      ) : (
                        <ArrowUpDown className="ml-1 size-3.5" />
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

      {pages > 1 && (
        <div className="flex items-center justify-center gap-4 py-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            <ChevronLeft className="size-4" aria-hidden="true" />
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {pages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.min(pages, p + 1))}
            disabled={page >= pages}
          >
            Next
            <ChevronRight className="size-4" aria-hidden="true" />
          </Button>
        </div>
      )}
    </div>
  );
};
