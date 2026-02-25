import { useState, useEffect } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { useBrands } from '../../hooks/useBrands';
import { Input } from '../ui/input';
import { Card, CardContent } from '../ui/card';
import { cn } from '../../lib/utils';

interface BrandSearchProps {
  onSelect: (brandId: number) => void;
}

export const BrandSearch = ({ onSelect }: BrandSearchProps) => {
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const { data, isLoading } = useBrands(1, 10, debouncedSearch);

  return (
    <div className="flex w-full flex-col items-center justify-center space-y-8 py-20">
      <div className="space-y-4 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-6xl">
          Search for Brand
        </h1>
        <p className="text-lg text-muted-foreground">
          Enter a brand name to start the presentation hub.
        </p>
      </div>

      <div className="relative w-full max-w-2xl">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 size-5 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Type brand name..."
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
                <ul className="divide-y divide-border">
                  {data.items.map((brand) => (
                    <li key={brand.id}>
                      <button
                        className="flex w-full items-center px-4 py-4 text-left transition-colors hover:bg-muted"
                        onClick={() => onSelect(brand.id)}
                      >
                        <div className="flex-1">
                          <p className="font-semibold text-foreground">
                            {brand.brand_name}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {String(brand.raw_data?.['Store Name'] || brand.brand_name)}
                          </p>
                        </div>
                      </button>
                    </li>
                  ))}
                </ul>
              ) : !isLoading ? (
                <div className="px-4 py-8 text-center text-muted-foreground">
                  No brands found matching "{debouncedSearch}"
                </div>
              ) : null}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
