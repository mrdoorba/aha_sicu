import { useCallback, useEffect, useMemo, useState } from 'react';
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

const VERDICT_LABEL_KEYS: Record<string, string> = {
  '✔️': 'verdict.approved',
  '❌': 'verdict.rejected',
  '❌ Non Mall': 'verdict.nonMall',
  '❌ No Brand': 'verdict.noBrand',
  '❌ Opex': 'verdict.opexIssue',
  '❌ Stock': 'verdict.stockInsufficient',
};

const HISTORY_MARKETPLACES = ['ID', 'TH'] as const;
const HISTORY_VERDICT_FILTERS = ['approved', 'non_approved'] as const;

type HistoryMarketplaceFilter = (typeof HISTORY_MARKETPLACES)[number];
type HistoryVerdictFilter = (typeof HISTORY_VERDICT_FILTERS)[number];

function getMarketplaceFlag(marketplace: 'ID' | 'TH'): string {
  return marketplace === 'TH' ? '🇹🇭' : '🇮🇩';
}

function parseFilterParam<T extends string>(
  rawValue: string | null,
  allowedValues: readonly T[],
): T[] {
  if (!rawValue) {
    return [...allowedValues];
  }

  const selected = rawValue
    .split(',')
    .map((value) => value.trim())
    .filter((value): value is T => allowedValues.includes(value as T));

  return selected.length > 0 ? Array.from(new Set(selected)) : [...allowedValues];
}

function areAllSelected<T extends string>(
  selected: T[],
  allowedValues: readonly T[],
): boolean {
  return allowedValues.every((value) => selected.includes(value));
}

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
            <span>{brand.brand_name}</span>
            <span
              className="inline-flex items-center gap-1 rounded-full border border-border/70 bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground"
              aria-label={`Marketplace ${brand.marketplace}`}
            >
              <span aria-hidden="true">{getMarketplaceFlag(brand.marketplace)}</span>
              <span>{brand.marketplace}</span>
            </span>
          </div>
        </TableCell>
        <TableCell>{t('history.table.evaluationCount', { count: brand.evaluation_count })}</TableCell>
        <TableCell>
          <span className="font-mono">
            {brand.top_score.toFixed(2)} {t(VERDICT_LABEL_KEYS[brand.top_verdict] ?? brand.top_verdict)}
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
                  {ev.final_score.toFixed(2)} {t(VERDICT_LABEL_KEYS[ev.verdict] ?? ev.verdict)}
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
  const selectedMarketplaces = parseFilterParam<HistoryMarketplaceFilter>(
    searchParams.get('marketplace'),
    HISTORY_MARKETPLACES,
  );
  const selectedVerdicts = parseFilterParam<HistoryVerdictFilter>(
    searchParams.get('verdict'),
    HISTORY_VERDICT_FILTERS,
  );
  const activeMarketplaces = areAllSelected(selectedMarketplaces, HISTORY_MARKETPLACES)
    ? undefined
    : selectedMarketplaces;
  const activeVerdicts = areAllSelected(selectedVerdicts, HISTORY_VERDICT_FILTERS)
    ? undefined
    : selectedVerdicts;
  const [searchInput, setSearchInput] = useState(searchFromUrl);

  // Debounce: update URL params after 300ms idle. Guard on a real diff so the
  // effect re-firing (setSearchParams changes identity on every navigation in
  // react-router v6) doesn't wipe the page param when only the URL changed.
  useEffect(() => {
    if (searchInput === searchFromUrl) return;
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
  }, [searchInput, searchFromUrl, setSearchParams]);

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

  const toggleMultiFilter = useCallback(
    <T extends string,>(
      key: string,
      value: T,
      allowedValues: readonly T[],
    ) => {
      setSearchParams((prev) => {
        const p = new URLSearchParams(prev);
        const current = parseFilterParam<T>(p.get(key), allowedValues);
        const next = areAllSelected(current, allowedValues)
          ? [value]
          : current.includes(value)
            ? (current.length === 1 ? [...allowedValues] : current.filter((item) => item !== value))
            : allowedValues.filter((item) => current.includes(item) || item === value);

        if (areAllSelected(next, allowedValues)) {
          p.delete(key);
        } else {
          p.set(key, next.join(','));
        }
        p.delete('page');
        return p;
      }, { replace: true });
      setExpandedBrands(new Set());
    },
    [setSearchParams],
  );

  const clearFilters = useCallback(() => {
    setSearchInput('');
    setSearchParams({}, { replace: true });
    setExpandedBrands(new Set());
  }, [setSearchParams]);

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
    activeMarketplaces,
    activeVerdicts,
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

  const hasMarketplaceFilter = !areAllSelected(selectedMarketplaces, HISTORY_MARKETPLACES);
  const hasVerdictFilter = !areAllSelected(selectedVerdicts, HISTORY_VERDICT_FILTERS);
  const activeFilterCount = [
    Boolean(searchFromUrl),
    Boolean(dateFromUrl || dateToUrl),
    hasMarketplaceFilter,
    hasVerdictFilter,
  ].filter(Boolean).length;

  const filterBar = (
    <div className="mb-4 flex flex-wrap items-end gap-4">
      <div className="flex flex-wrap gap-2">
        <Button
          variant={selectedMarketplaces.includes('ID') ? 'default' : 'outline'}
          size="sm"
          onClick={() => toggleMultiFilter('marketplace', 'ID', HISTORY_MARKETPLACES)}
        >
          {t('history.table.filterMarketplaceId')}
        </Button>
        <Button
          variant={selectedMarketplaces.includes('TH') ? 'default' : 'outline'}
          size="sm"
          onClick={() => toggleMultiFilter('marketplace', 'TH', HISTORY_MARKETPLACES)}
        >
          {t('history.table.filterMarketplaceTh')}
        </Button>
      </div>
      <div className="flex flex-wrap gap-2">
        <Button
          variant={selectedVerdicts.includes('approved') ? 'default' : 'outline'}
          size="sm"
          onClick={() => toggleMultiFilter('verdict', 'approved', HISTORY_VERDICT_FILTERS)}
        >
          {t('history.table.filterVerdictApproved')}
        </Button>
        <Button
          variant={selectedVerdicts.includes('non_approved') ? 'default' : 'outline'}
          size="sm"
          onClick={() => toggleMultiFilter('verdict', 'non_approved', HISTORY_VERDICT_FILTERS)}
        >
          {t('history.table.filterVerdictNonApproved')}
        </Button>
      </div>
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
      {activeFilterCount > 0 && (
        <Button
          variant="ghost"
          size="sm"
          onClick={clearFilters}
        >
          {t('history.table.clearFilters')}
        </Button>
      )}
    </div>
  );

  if (!isLoading && brands.length === 0 && total === 0) {
    return (
      <div>
        {filterBar}
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <p className="text-muted-foreground">
            {activeFilterCount > 1
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
