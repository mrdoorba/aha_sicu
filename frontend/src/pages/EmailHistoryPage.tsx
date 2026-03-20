import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ChevronLeft, ChevronRight, AlertCircle, Search, X, Trash2 } from 'lucide-react';
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '../components/ui/table';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import { useEmailHistory } from '../hooks/useEmailHistory';
import { useDeleteEmailHistory } from '../hooks/useDeleteEmailHistory';
import { useCurrentUser } from '../hooks/useCurrentUser';
import { getIntlLocale } from '../lib/languages';
import { toast } from 'sonner';

const STATUS_BADGE_STYLES: Record<string, string> = {
  sent: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  delivered: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  opened: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
  clicked: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400',
  bounced: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  failed: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  deferred: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
  spam: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
  blocked: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
  invalid: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
};

const STATUS_I18N_KEYS: Record<string, string> = {
  sent: 'emailHistory.statusSent',
  delivered: 'emailHistory.statusDelivered',
  opened: 'emailHistory.statusOpened',
  clicked: 'emailHistory.statusClicked',
  bounced: 'emailHistory.statusBounced',
  failed: 'emailHistory.statusFailed',
  deferred: 'emailHistory.statusDeferred',
  spam: 'emailHistory.statusSpam',
  blocked: 'emailHistory.statusBlocked',
  invalid: 'emailHistory.statusInvalid',
};

const FILTER_STATUSES = ['sent', 'delivered', 'bounced', 'opened', 'deferred', 'failed', 'spam'] as const;

export const EmailHistoryPage = () => {
  const { t, i18n } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();
  const { profile } = useCurrentUser();
  const isAdmin = profile?.role === 'admin';

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
  const statusFromUrl = searchParams.get('status') ?? '';
  const [searchInput, setSearchInput] = useState(searchFromUrl);
  const isInitialMount = useRef(true);

  // Selection state
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [confirmOpen, setConfirmOpen] = useState(false);

  const deleteMutation = useDeleteEmailHistory();

  // Clear selection when page/filters change
  useEffect(() => {
    setSelected(new Set());
  }, [page, searchFromUrl, dateFromUrl, dateToUrl, statusFromUrl]);

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
    (value: string) => {
      setSearchParams((prev) => {
        const p = new URLSearchParams(prev);
        if (value) {
          p.set('date_from', value);
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
    (value: string) => {
      setSearchParams((prev) => {
        const p = new URLSearchParams(prev);
        if (value) {
          p.set('date_to', value);
        } else {
          p.delete('date_to');
        }
        p.delete('page');
        return p;
      }, { replace: true });
    },
    [setSearchParams],
  );

  const setStatus = useCallback(
    (value: string) => {
      setSearchParams((prev) => {
        const p = new URLSearchParams(prev);
        if (value && value !== 'all') {
          p.set('status', value);
        } else {
          p.delete('status');
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
    },
    [page, setSearchParams],
  );

  const {
    items,
    total,
    pages,
    isLoading,
    isError,
    refetch,
    isPlaceholderData,
  } = useEmailHistory(
    page, limit,
    searchFromUrl || undefined,
    dateFromUrl || undefined,
    dateToUrl || undefined,
    statusFromUrl || undefined,
  );

  const toggleItem = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleAll = () => {
    if (selected.size === items.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(items.map((i) => i.id)));
    }
  };

  const handleDelete = () => {
    const ids = Array.from(selected);
    deleteMutation.mutate(ids, {
      onSuccess: (data) => {
        toast.success(t('emailHistory.deleteSuccess', { count: data.deleted }));
        setSelected(new Set());
        setConfirmOpen(false);
      },
      onError: () => {
        toast.error(t('emailHistory.deleteError'));
        setConfirmOpen(false);
      },
    });
  };

  if (isError) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold tracking-tight mb-6">{t('emailHistory.title')}</h2>
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <AlertCircle className="size-10 text-destructive" aria-hidden="true" />
          <p className="text-muted-foreground">{t('emailHistory.error')}</p>
          <Button variant="outline" onClick={() => refetch()}>
            {t('emailHistory.retry')}
          </Button>
        </div>
      </div>
    );
  }

  const filterBar = (
    <div className="mb-4 flex flex-wrap items-end gap-4">
      <div className="relative max-w-sm">
        <Search
          className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
          aria-hidden="true"
        />
        <Input
          aria-label={t('emailHistory.aria.searchInput')}
          placeholder={t('emailHistory.searchPlaceholder')}
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          className="pl-9 pr-9"
        />
        {searchInput && (
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-1 top-1/2 size-7 -translate-y-1/2 p-0"
            aria-label={t('emailHistory.aria.clearSearch')}
            onClick={() => setSearchInput('')}
          >
            <X className="size-4" aria-hidden="true" />
          </Button>
        )}
      </div>
      <div className="flex items-center gap-2">
        <Input
          type="date"
          aria-label={t('emailHistory.dateFrom')}
          value={dateFromUrl}
          onChange={(e) => setDateFrom(e.target.value)}
          max={dateToUrl || undefined}
          className="w-[160px]"
        />
        <span className="text-muted-foreground text-sm">–</span>
        <Input
          type="date"
          aria-label={t('emailHistory.dateTo')}
          value={dateToUrl}
          onChange={(e) => setDateTo(e.target.value)}
          min={dateFromUrl || undefined}
          className="w-[160px]"
        />
      </div>
      <Select value={statusFromUrl || 'all'} onValueChange={setStatus}>
        <SelectTrigger className="w-[140px]" aria-label={t('emailHistory.status')}>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">{t('emailHistory.statusAll')}</SelectItem>
          {FILTER_STATUSES.map((s) => (
            <SelectItem key={s} value={s}>{t(STATUS_I18N_KEYS[s])}</SelectItem>
          ))}
        </SelectContent>
      </Select>
      {isAdmin && selected.size > 0 && (
        <Button
          variant="destructive"
          size="sm"
          onClick={() => setConfirmOpen(true)}
          disabled={deleteMutation.isPending}
        >
          <Trash2 className="mr-1.5 size-4" aria-hidden="true" />
          {t('emailHistory.deleteSelected', { count: selected.size })}
        </Button>
      )}
    </div>
  );

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      <h2 className="text-2xl font-bold tracking-tight mb-6">{t('emailHistory.title')}</h2>
      {filterBar}

      {!isLoading && items.length === 0 && total === 0 ? (
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <p className="text-muted-foreground">{t('emailHistory.empty')}</p>
        </div>
      ) : (
        <>
          <div className="rounded-md border bg-card">
            <Table
              aria-label={t('emailHistory.aria.table')}
              aria-busy={isLoading || isPlaceholderData}
              className={isPlaceholderData ? 'opacity-60 transition-opacity' : ''}
            >
              <TableHeader>
                <TableRow>
                  {isAdmin && (
                    <TableHead className="w-10">
                      <input
                        type="checkbox"
                        className="size-4 rounded border-gray-300 accent-primary"
                        checked={items.length > 0 && selected.size === items.length}
                        onChange={toggleAll}
                        aria-label={t('emailHistory.aria.selectAll')}
                      />
                    </TableHead>
                  )}
                  <TableHead className="text-xs uppercase">{t('emailHistory.recipient')}</TableHead>
                  <TableHead className="text-xs uppercase">{t('emailHistory.subject')}</TableHead>
                  <TableHead className="text-xs uppercase">{t('emailHistory.statusLabel')}</TableHead>
                  <TableHead className="text-xs uppercase">{t('emailHistory.sentAt')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading
                  ? Array.from({ length: 10 }).map((_, i) => (
                      <TableRow key={i}>
                        {isAdmin && <TableCell><div className="h-4 w-4 animate-pulse rounded bg-muted" /></TableCell>}
                        <TableCell><div className="h-4 w-40 animate-pulse rounded bg-muted" /></TableCell>
                        <TableCell><div className="h-4 w-48 animate-pulse rounded bg-muted" /></TableCell>
                        <TableCell><div className="h-4 w-16 animate-pulse rounded bg-muted" /></TableCell>
                        <TableCell><div className="h-4 w-32 animate-pulse rounded bg-muted" /></TableCell>
                      </TableRow>
                    ))
                  : items.map((item) => (
                      <TableRow key={item.id} className={selected.has(item.id) ? 'bg-muted/50' : ''}>
                        {isAdmin && (
                          <TableCell>
                            <input
                              type="checkbox"
                              className="size-4 rounded border-gray-300 accent-primary"
                              checked={selected.has(item.id)}
                              onChange={() => toggleItem(item.id)}
                              aria-label={t('emailHistory.aria.selectRow')}
                            />
                          </TableCell>
                        )}
                        <TableCell className="font-medium">{item.recipient_email}</TableCell>
                        <TableCell>{item.subject}</TableCell>
                        <TableCell>
                          <span
                            className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                              STATUS_BADGE_STYLES[item.status] ?? 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400'
                            }`}
                          >
                            {t(STATUS_I18N_KEYS[item.status] ?? 'emailHistory.statusSent')}
                          </span>
                        </TableCell>
                        <TableCell className="text-muted-foreground text-sm">
                          {dateFormatter.format(new Date(item.sent_at))}
                        </TableCell>
                      </TableRow>
                    ))}
              </TableBody>
            </Table>
          </div>

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
                {t('common.pageOf', { page, totalPages: pages })}
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
        </>
      )}

      {/* Delete confirmation dialog */}
      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{t('emailHistory.deleteConfirmTitle')}</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            {t('emailHistory.deleteConfirmMessage', { count: selected.size })}
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmOpen(false)} disabled={deleteMutation.isPending}>
              {t('common.cancel')}
            </Button>
            <Button variant="destructive" onClick={handleDelete} disabled={deleteMutation.isPending}>
              {deleteMutation.isPending ? t('common.deleting') : t('common.delete')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
