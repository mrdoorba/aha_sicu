import { useState, useEffect } from 'react';
import { Search, ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';
import { Header } from '../components/layout/Header';
import { SyncStatus } from '../components/sync/SyncStatus';
import { BrandTable } from '../components/brands/BrandTable';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { useBrands } from '../hooks/useBrands';

export const BrandsPage = () => {
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

  const { data, isLoading } = useBrands(page, limit, debouncedSearch);

  const totalPages = data?.pages ?? 0;
  const hasBrands = (data?.total ?? 0) > 0;
  const isEmpty = !isLoading && !hasBrands && !debouncedSearch;
  const noResults = !isLoading && !hasBrands && !!debouncedSearch;

  return (
    <div className="min-h-screen bg-muted">
      <Header />
      <main className="mx-auto max-w-7xl py-6 px-4 sm:px-6 lg:px-8">
        <h2 className="mb-6 text-2xl font-semibold text-foreground">Brands</h2>

        {/* Sync Status */}
        <div className="mb-6">
          <SyncStatus />
        </div>

        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search brands..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Brand Table */}
        <Card>
          <CardContent className="p-0">
            {isEmpty ? (
              <div className="flex flex-col items-center gap-3 py-16 text-center">
                <RefreshCw className="size-10 text-muted-foreground" />
                <p className="text-muted-foreground">
                  No brands synced yet. Click &quot;Sync Now&quot; to get
                  started.
                </p>
              </div>
            ) : noResults ? (
              <div className="py-16 text-center">
                <p className="text-muted-foreground">
                  No brands found matching &quot;{debouncedSearch}&quot;
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
              <ChevronLeft className="size-4" />
              Previous
            </Button>
            <span className="text-sm text-muted-foreground">
              Page {page} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
            >
              Next
              <ChevronRight className="size-4" />
            </Button>
          </div>
        )}
      </main>
    </div>
  );
};
