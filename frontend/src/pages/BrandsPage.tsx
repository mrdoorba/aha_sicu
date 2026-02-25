import { useState, useEffect } from 'react';
import { Search, ChevronLeft, ChevronRight, RefreshCw, XCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { SyncStatus } from '../components/sync/SyncStatus';
import { BrandTable } from '../components/brands/BrandTable';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { useBrands } from '../hooks/useBrands';

export const BrandsPage = () => {
  const { t } = useTranslation();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const limit = 20;

  // Debounce search input (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const { data, isLoading, isError } = useBrands(page, limit, debouncedSearch);

  const totalPages = data?.pages ?? 0;
  const hasBrands = (data?.total ?? 0) > 0;
  const isEmpty = !isLoading && !isError && !hasBrands && !debouncedSearch;
  const noResults = !isLoading && !isError && !hasBrands && !!debouncedSearch;

  return (
    <div className="p-8">
      <main id="main-content" tabIndex={-1} className="mx-auto max-w-7xl">
        <h2 className="mb-6 text-2xl font-semibold text-foreground">{t('brands.title')}</h2>

        {/* Sync Status */}
        <div className="mb-6">
          <SyncStatus />
        </div>

        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
          <Input
            type="search"
            placeholder={t('brands.searchPlaceholder')}
            aria-label={t('brands.searchLabel')}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Brand Table */}
        <Card>
          <CardContent className="p-0">
            {isError ? (
              <div className="flex flex-col items-center gap-3 py-16 text-center">
                <XCircle className="size-10 text-destructive" aria-hidden="true" />
                <p className="text-muted-foreground">
                  {t('brands.errorLoading')}
                </p>
              </div>
            ) : isEmpty ? (
              <div className="flex flex-col items-center gap-3 py-16 text-center">
                <RefreshCw className="size-10 text-muted-foreground" aria-hidden="true" />
                <p className="text-muted-foreground">
                  {t('brands.emptyState')}
                </p>
              </div>
            ) : noResults ? (
              <div className="py-16 text-center">
                <p className="text-muted-foreground">
                  {t('brands.noResults', { search: debouncedSearch })}
                </p>
              </div>
            ) : (
              <BrandTable
                brands={data?.items ?? []}
                isLoading={isLoading}
              />
            )}
          </CardContent>
        </Card>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-4 flex items-center justify-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
            >
              <ChevronLeft className="size-4" aria-hidden="true" />
              {t('common.previous')}
            </Button>
            <span className="text-sm text-muted-foreground">
              {t('common.pageOf', { page, totalPages })}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
            >
              {t('common.next')}
              <ChevronRight className="size-4" aria-hidden="true" />
            </Button>
          </div>
        )}
      </main>
    </div>
  );
};
