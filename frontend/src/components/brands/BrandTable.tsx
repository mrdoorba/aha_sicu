import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '../ui/table';
import { Badge } from '../ui/badge';
import type { BrandListItem } from '../../hooks/useBrands';

interface BrandTableProps {
  brands: BrandListItem[];
  isLoading: boolean;
}

export const BrandTable = ({ brands, isLoading }: BrandTableProps) => {
  return (
    <Table aria-label="Brand list" aria-busy={isLoading}>
      <TableHeader>
        <TableRow>
          <TableHead className="text-xs uppercase">Brand Name</TableHead>
          <TableHead className="text-xs uppercase">Key Info</TableHead>
          <TableHead className="text-xs uppercase">Meeting Data</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {isLoading
          ? Array.from({ length: 10 }).map((_, i) => (
              <TableRow key={i}>
                <TableCell>
                  <div className="h-4 w-32 animate-pulse rounded bg-muted" />
                </TableCell>
                <TableCell>
                  <div className="h-4 w-48 animate-pulse rounded bg-muted" />
                </TableCell>
                <TableCell>
                  <div className="h-4 w-20 animate-pulse rounded bg-muted" />
                </TableCell>
              </TableRow>
            ))
          : brands.map((brand) => (
              <TableRow key={brand.id} className="hover:bg-muted/50">
                <TableCell className="font-medium">{brand.brand_name}</TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {summarizeRawData(brand.raw_data)}
                </TableCell>
                <TableCell>
                  {brand.meeting_raw_data ? (
                    <Badge className="bg-green-500 text-white hover:bg-green-500/90">
                      Available
                    </Badge>
                  ) : (
                    <span className="text-sm text-muted-foreground">
                      &mdash; Not available
                    </span>
                  )}
                </TableCell>
              </TableRow>
            ))}
      </TableBody>
    </Table>
  );
};

// Case-insensitive filter via toLowerCase() handles inconsistent key casing from Google Sheets JSONB
const META_KEYS = new Set(['id', 'created_at', 'updated_at', 'synced_at']);

function summarizeRawData(rawData: Record<string, unknown>): string {
  const entries = Object.entries(rawData)
    .filter(([key]) => !META_KEYS.has(key.toLowerCase()))
    .sort(([a], [b]) => a.localeCompare(b));
  const summary = entries
    .slice(0, 3)
    .map(([key, value]) => `${key}: ${String(value ?? '')}`)
    .join(' | ');
  return summary || 'No data';
}
