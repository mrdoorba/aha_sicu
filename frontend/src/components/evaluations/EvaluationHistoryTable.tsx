import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ChevronLeft, ChevronRight, ChevronDown, ChevronUp, AlertCircle, Search, X, CalendarIcon, Loader2 } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '../ui/table';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { cn } from '../../lib/utils';
import { Calendar } from '../ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';
import { useGroupedEvaluations, type GroupedEvaluationItem } from '../../hooks/useGroupedEvaluations';
import { useBrandEvaluations } from '../../hooks/useBrandEvaluations';
import { getIntlLocale } from '../../lib/languages';

function SearchInput({
  value,
  onChange,
  ariaLabel,
  placeholder,
  clearLabel,
}: {
  value: string;
  onChange: (value: string) => void;
  ariaLabel: string;
  placeholder: string;
  clearLabel: string;
}) {
  return (
    <div className="relative max-w-sm">
      <Search
        className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
        aria-hidden="true"
      />
      <Input
        aria-label={ariaLabel}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="pl-9 pr-9"
      />
      {value && (
        <Button
          variant="ghost"
          size="sm"
          className="absolute right-1 top-1/2 size-7 -translate-y-1/2 p-0"
          aria-label={clearLabel}
          onClick={() => onChange('')}
        >
          <X className="size-4" aria-hidden="true" />
        </Button>
      )}
    </div>
  );
}

function DatePickerField({
  label,
  value,
  onChange,
  clearLabel,
  disableBefore,
  disableAfter,
}: {
  label: string;
  value: Date | undefined;
  onChange: (date: Date | undefined) => void;
  clearLabel: string;
  disableBefore?: Date;
  disableAfter?: Date;
}) {
  const [open, setOpen] = useState(false);

  const disabled: Array<{ before: Date } | { after: Date }> = [];
  if (disableBefore) disabled.push({ before: disableBefore });
  if (disableAfter) disabled.push({ after: disableAfter });

  return (
    <div className="flex items-center gap-1">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              'w-[180px] justify-start text-left font-normal',
              !value && 'text-muted-foreground',
            )}
            aria-label={label}
          >
            <CalendarIcon className="mr-2 size-4" aria-hidden="true" />
            {value ? format(value, 'MMM d, yyyy') : label}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="single"
            selected={value}
            onSelect={(date) => {
              onChange(date);
              setOpen(false);
            }}
            autoFocus
            disabled={disabled.length > 0 ? disabled : undefined}
          />
        </PopoverContent>
      </Popover>
      {value && (
        <Button
          variant="ghost"
          size="sm"
          className="size-7 p-0"
          aria-label={clearLabel}
          onClick={() => onChange(undefined)}
        >
          <X className="size-4" aria-hidden="true" />
        </Button>
      )}
    </div>
  );
}

function BrandAccordionRow({
  brand,
  isExpanded,
  onToggle,
  dateFrom,
  dateTo,
  dateFormatter,
  t,
}: {
  brand: GroupedEvaluationItem;
  isExpanded: boolean;
  onToggle: () => void;
  dateFrom?: string;
  dateTo?: string;
  dateFormatter: Intl.DateTimeFormat;
  t: (key: string, params?: Record<string, unknown>) => string;
}) {
  const navigate = useNavigate();
  const [showAll, setShowAll] = useState(false);

  // When collapsed, always reset to limited view
  const effectiveShowAll = isExpanded && showAll;
  const limit = effectiveShowAll ? undefined : 5;
  const { evaluations, total, isLoading, isError } = useBrandEvaluations(
    brand.brand_id,
    limit,
    dateFrom,
    dateTo,
    isExpanded,
  );

  return (
    <>
      <TableRow
        className="cursor-pointer hover:bg-muted/50"
        onClick={onToggle}
        aria-expanded={isExpanded}
      >
        <TableCell className="font-medium">
          <div className="flex items-center gap-2">
            {isExpanded
              ? <ChevronUp className="size-4 text-muted-foreground" aria-hidden="true" />
              : <ChevronDown className="size-4 text-muted-foreground" aria-hidden="true" />
            }
            {brand.brand_name}
          </div>
        </TableCell>
        <TableCell>{t('history.table.evaluationCount', { count: brand.evaluation_count })}</TableCell>
        <TableCell>
          <span className="font-mono">
            {brand.top_score.toFixed(2)} {brand.top_verdict}
          </span>
        </TableCell>
        <TableCell>{dateFormatter.format(new Date(brand.latest_date))}</TableCell>
      </TableRow>

      {isExpanded && (
        <>
          {isLoading && (
            <TableRow>
              <TableCell colSpan={4} className="py-4 text-center">
                <Loader2 className="mx-auto size-5 animate-spin text-muted-foreground" />
              </TableCell>
            </TableRow>
          )}

          {isError && (
            <TableRow>
              <TableCell colSpan={4} className="py-4 text-center text-destructive">
                {t('history.table.failedLoadEvaluations')}
              </TableCell>
            </TableRow>
          )}

          {!isLoading && !isError && evaluations.map((ev) => (
            <TableRow
              key={ev.id}
              className="cursor-pointer bg-muted/30 hover:bg-muted/50"
              onClick={() => navigate(`/history/${ev.id}`)}
            >
              <TableCell className="pl-10 text-muted-foreground">—</TableCell>
              <TableCell>
                <span className="font-mono">
                  {ev.final_score.toFixed(2)} {ev.verdict}
                </span>
              </TableCell>
              <TableCell>{ev.evaluator_email}</TableCell>
              <TableCell>{dateFormatter.format(new Date(ev.created_at))}</TableCell>
            </TableRow>
          ))}

          {!isLoading && !isError && !showAll && total > 5 && (
            <TableRow>
              <TableCell colSpan={4} className="py-2 text-center">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowAll(true);
                  }}
                >
                  {t('history.table.showAll', { count: total })}
                </Button>
              </TableCell>
            </TableRow>
          )}
        </>
      )}
    </>
  );
}

export const EvaluationHistoryTable = () => {
  const { t, i18n } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();
  const [expandedBrands, setExpandedBrands] = useState<Set<number>>(new Set());

  const dateFormatter = useMemo(
    () => new Intl.DateTimeFormat(getIntlLocale(i18n.language), {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Asia/Jakarta',
    }),
    [i18n.language],
  );

  const page = Math.max(1, Number(searchParams.get('page')) || 1);
  const limit = 20;
  const searchFromUrl = searchParams.get('search') ?? '';
  const dateFromUrl = searchParams.get('date_from') ?? '';
  const dateToUrl = searchParams.get('date_to') ?? '';
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
        p.delete('page');
        return p;
      }, { replace: true });
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput, setSearchParams]);

  // Sync input when URL changes externally (e.g., browser back)
  useEffect(() => {
    setSearchInput(searchFromUrl);
  }, [searchFromUrl]);

  const setDateFrom = useCallback(
    (date: Date | undefined) => {
      setSearchParams((prev) => {
        const p = new URLSearchParams(prev);
        if (date) {
          p.set('date_from', format(date, 'yyyy-MM-dd'));
        } else {
          p.delete('date_from');
        }
        p.delete('page');
        return p;
      }, { replace: true });
    },
    [setSearchParams],
  );

  const setDateTo = useCallback(
    (date: Date | undefined) => {
      setSearchParams((prev) => {
        const p = new URLSearchParams(prev);
        if (date) {
          p.set('date_to', format(date, 'yyyy-MM-dd'));
        } else {
          p.delete('date_to');
        }
        p.delete('page');
        return p;
      }, { replace: true });
    },
    [setSearchParams],
  );

  const setPage = useCallback(
    (updater: number | ((prev: number) => number)) => {
      const next = typeof updater === 'function' ? updater(page) : updater;
      setSearchParams((prev) => {
        const p = new URLSearchParams(prev);
        if (next <= 1) p.delete('page');
        else p.set('page', String(next));
        return p;
      });
      // Collapse all accordions when changing page
      setExpandedBrands(new Set());
    },
    [page, setSearchParams],
  );

  const toggleBrand = useCallback((brandId: number) => {
    setExpandedBrands((prev) => {
      const next = new Set(prev);
      if (next.has(brandId)) next.delete(brandId);
      else next.add(brandId);
      return next;
    });
  }, []);

  const {
    brands,
    total,
    pages,
    isLoading,
    isError,
    error,
    refetch,
    isPlaceholderData,
  } = useGroupedEvaluations(
    page, limit,
    searchFromUrl || undefined,
    dateFromUrl || undefined,
    dateToUrl || undefined,
  );

  if (isError) {
    return (
      <div className="flex flex-col items-center gap-3 py-16 text-center">
        <AlertCircle className="size-10 text-destructive" aria-hidden="true" />
        <p className="text-muted-foreground">
          {error?.message || t('history.table.failedLoadHistory')}
        </p>
        <Button variant="outline" onClick={() => refetch()}>
          {t('common.retry')}
        </Button>
      </div>
    );
  }

  const filterBar = (
    <div className="mb-4 flex flex-wrap items-end gap-4">
      <SearchInput
        value={searchInput}
        onChange={setSearchInput}
        ariaLabel={t('history.table.aria.searchInput')}
        placeholder={t('history.table.searchPlaceholder')}
        clearLabel={t('history.table.aria.clearSearch')}
      />
      <div className="flex items-center gap-2">
        <DatePickerField
          label={t('history.table.aria.dateFrom')}
          value={dateFromUrl ? parseISO(dateFromUrl) : undefined}
          onChange={setDateFrom}
          clearLabel={t('history.table.aria.clearDateFrom')}
          disableAfter={dateToUrl ? parseISO(dateToUrl) : undefined}
        />
        <span className="text-muted-foreground text-sm">–</span>
        <DatePickerField
          label={t('history.table.aria.dateTo')}
          value={dateToUrl ? parseISO(dateToUrl) : undefined}
          onChange={setDateTo}
          clearLabel={t('history.table.aria.clearDateTo')}
          disableBefore={dateFromUrl ? parseISO(dateFromUrl) : undefined}
        />
      </div>
    </div>
  );

  if (!isLoading && brands.length === 0 && total === 0) {
    return (
      <div>
        {filterBar}
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <p className="text-muted-foreground">
            {[searchFromUrl, dateFromUrl || dateToUrl].filter(Boolean).length > 1
              ? t('history.table.noMatchFilter')
              : searchFromUrl
                ? t('history.table.noMatchSearch', { search: searchFromUrl })
                : dateFromUrl || dateToUrl
                  ? t('history.table.noMatchDate')
                  : t('history.table.emptyState')}
          </p>
          {!searchFromUrl && !dateFromUrl && !dateToUrl && (
            <p className="text-sm text-muted-foreground">
              {t('history.table.emptyStateHint')}
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div>
      {filterBar}
      <Table
        aria-label={t('history.table.aria.table')}
        aria-busy={isLoading || isPlaceholderData}
        className={isPlaceholderData ? 'opacity-60 transition-opacity' : ''}
      >
        <TableHeader>
          <TableRow>
            <TableHead className="text-xs uppercase">{t('history.table.brand')}</TableHead>
            <TableHead className="text-xs uppercase">{t('history.table.evaluations')}</TableHead>
            <TableHead className="text-xs uppercase">{t('history.table.topScore')}</TableHead>
            <TableHead className="text-xs uppercase">{t('history.table.latest')}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading
            ? Array.from({ length: 10 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><div className="h-4 w-32 animate-pulse rounded bg-muted" /></TableCell>
                  <TableCell><div className="h-4 w-20 animate-pulse rounded bg-muted" /></TableCell>
                  <TableCell><div className="h-4 w-24 animate-pulse rounded bg-muted" /></TableCell>
                  <TableCell><div className="h-4 w-28 animate-pulse rounded bg-muted" /></TableCell>
                </TableRow>
              ))
            : brands.map((brand) => (
                <BrandAccordionRow
                  key={brand.brand_id}
                  brand={brand}
                  isExpanded={expandedBrands.has(brand.brand_id)}
                  onToggle={() => toggleBrand(brand.brand_id)}
                  dateFrom={dateFromUrl || undefined}
                  dateTo={dateToUrl || undefined}
                  dateFormatter={dateFormatter}
                  t={t}
                />
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
              {t('common.previous')}
            </Button>
          )}
          <span className="text-sm text-muted-foreground">
            {pages > 1 ? t('common.pageOf', { page, totalPages: pages }) : t('history.table.brandCount', { count: total })}
          </span>
          {pages > 1 && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(pages, p + 1))}
              disabled={page >= pages}
            >
              {t('common.next')}
              <ChevronRight className="size-4" aria-hidden="true" />
            </Button>
          )}
        </div>
      )}
    </div>
  );
};
