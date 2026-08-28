import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Search, Loader2 } from 'lucide-react';
import { useBrands } from '../../hooks/useBrands';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Card, CardContent } from '../ui/card';

const SEARCH_RESULT_LIMIT = 10;

interface BrandSearchProps {
  onSelect: (brandId: number) => void;
}

export const BrandSearch = ({ onSelect }: BrandSearchProps) => {
  const { t } = useTranslation();
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const { data, isLoading } = useBrands(1, SEARCH_RESULT_LIMIT, debouncedSearch);

  return (
    <div className="flex w-full flex-col items-center justify-center space-y-8 py-20">
      <div className="space-y-4 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-6xl">
          {t('brandSearch.title')}
        </h1>
        <p className="text-lg text-muted-foreground">
          {t('brandSearch.subtitle')}
        </p>
      </div>

      <div className="relative w-full max-w-2xl">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 size-5 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            placeholder={t('brandSearch.placeholder')}
            className="h-14 pl-12 pr-4 text-lg shadow-lg transition-shadow focus-visible:ring-primary"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            autoFocus
          />
          {isLoading && search && (
            <Loader2 className="absolute right-4 top-1/2 size-5 -translate-y-1/2 animate-spin text-primary" />
          )}
        </div>

        {debouncedSearch && (
          <Card className="absolute left-0 right-0 top-full z-50 mt-2 overflow-hidden shadow-2xl">
            <CardContent className="p-0">
              {data?.items && data.items.length > 0 ? (
                <>
                  <ul className="divide-y divide-border">
                    {data.items.map((brand) => (
                      <li key={brand.id}>
                        <button
                          className="flex w-full items-center gap-3 px-4 py-4 text-left transition-colors hover:bg-muted"
                          onClick={() => onSelect(brand.id)}
                        >
                          <span className="flex-1 font-semibold text-foreground">
                            {brand.brand_name}
                          </span>
                          <Badge variant="secondary">
                            {brand.marketplace === 'TH' ? '🇹🇭' : '🇮🇩'} {brand.marketplace}
                          </Badge>
                        </button>
                      </li>
                    ))}
                  </ul>
                  {data.total > data.items.length && (
                    <p className="border-t border-border px-4 py-2 text-center text-xs text-muted-foreground">
                      {t('brandSearch.showingCount', {
                        shown: data.items.length,
                        total: data.total,
                      })}
                    </p>
                  )}
                </>
              ) : !isLoading ? (
                <div className="px-4 py-8 text-center text-muted-foreground">
                  {t('brandSearch.noResults', { query: debouncedSearch })}
                </div>
              ) : null}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
