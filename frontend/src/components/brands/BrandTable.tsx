import { useNavigate } from 'react-router-dom';
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
import type { BrandListItem } from '../../hooks/useBrands';

interface BrandTableProps {
  brands: BrandListItem[];
  isLoading: boolean;
}

export const BrandTable = ({ brands, isLoading }: BrandTableProps) => {
  const navigate = useNavigate();

  return (
    <Table aria-label="Brand list" aria-busy={isLoading}>
      <TableHeader>
        <TableRow>
          <TableHead className="text-xs uppercase">Brand Name</TableHead>
          <TableHead className="text-xs uppercase">Key Info</TableHead>
          <TableHead className="text-xs uppercase">Meeting Data</TableHead>
          <TableHead className="text-xs uppercase">Action</TableHead>
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
                <TableCell>
                  <div className="h-8 w-20 animate-pulse rounded bg-muted" />
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
                <TableCell>
                  <Button
                    size="sm"
                    onClick={() => navigate(`/evaluation/${brand.id}`)}
                  >
                    Evaluate
                  </Button>
                </TableCell>
              </TableRow>
            ))}
      </TableBody>
    </Table>
  );
};

// Priority fields to display from VP raw_data (in order of importance)
const PRIORITY_KEYS = [
  'Kategori',
  'Score\nVP',
  'Signed up',
  'Shopee Mall',
  'No OPEX Issue',
  'Approach',
];

function summarizeRawData(rawData: Record<string, unknown>): string {
  const parts: string[] = [];
  for (const key of PRIORITY_KEYS) {
    if (key in rawData && rawData[key] !== '' && rawData[key] != null) {
      parts.push(`${key.replace('\n', ' ')}: ${String(rawData[key])}`);
    }
    if (parts.length >= 3) break;
  }
  return parts.join(' | ') || 'No data';
}
