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
  const [activeMarketplaces, setActiveMarketplaces] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('brands_marketplace_filter');
      if (saved) {
        const parsed = JSON.parse(saved) as unknown;
        if (Array.isArray(parsed) && parsed.length > 0 && parsed.every((v) => typeof v === 'string')) {
          return parsed as string[];
        }
      }
    } catch {
      // ignore malformed data
    }
    return ['ID', 'TH'];
  });
  const limit = 20;

  const toggleMarketplace = (mp: string) => {
    setActiveMarketplaces((prev) => {
      let next: string[];
      if (prev.includes(mp)) {
        // Don't allow deselecting all
        if (prev.length === 1) return prev;
        next = prev.filter((m) => m !== mp);
      } else {
        next = [...prev, mp];
      }
      localStorage.setItem('brands_marketplace_filter', JSON.stringify(next));
      return next;
    });
    setPage(1);
  };

  // Debounce search input (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const { data, isLoading, isError } = useBrands(page, limit, debouncedSearch, activeMarketplaces);

  const totalPages = data?.pages ?? 0;
  const hasBrands = (data?.total ?? 0) > 0;
  const isEmpty = !isLoading && !isError && !hasBrands && !debouncedSearch;
  const noResults = !isLoading && !isError && !hasBrands && !!debouncedSearch;

  return (
    <div className="p-8">
      <div className="mx-auto max-w-7xl">
        <h2 className="mb-6 text-2xl font-semibold text-foreground">{t('brands.title')}</h2>

        {/* Sync Status */}
        <div className="mb-6">
          <SyncStatus />
        </div>

        {/* Marketplace Filters */}
        <div className="mb-4 flex gap-2">
          <Button
            variant={activeMarketplaces.includes('ID') ? 'default' : 'outline'}
            size="sm"
            onClick={() => toggleMarketplace('ID')}
          >
            {t('brands.filterID', { defaultValue: '\ud83c\uddee\ud83c\udde9 Indonesia' })}
          </Button>
          <Button
            variant={activeMarketplaces.includes('TH') ? 'default' : 'outline'}
            size="sm"
            onClick={() => toggleMarketplace('TH')}
          >
            {t('brands.filterTH', { defaultValue: '\ud83c\uddf9\ud83c\udded Thailand' })}
          </Button>
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
      </div>
    </div>
  );
};
