import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
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
  const { t } = useTranslation();

  return (
    <Table aria-label="Brand list" aria-busy={isLoading}>
      <TableHeader>
        <TableRow>
          <TableHead className="text-xs uppercase">{t('brandTable.header.brandName')}</TableHead>
          <TableHead className="text-xs uppercase">{t('brandTable.header.keyInfo')}</TableHead>
          <TableHead className="text-xs uppercase">{t('brandTable.header.meetingData')}</TableHead>
          <TableHead className="text-xs uppercase">{t('brandTable.header.action')}</TableHead>
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
                  {summarizeRawData(brand.raw_data) || t('brandTable.fallback.noData')}
                </TableCell>
                <TableCell>
                  {brand.meeting_raw_data ? (
                    <Badge className="bg-green-500 text-white hover:bg-green-500/90">
                      {t('brandTable.badge.available')}
                    </Badge>
                  ) : (
                    <span className="text-sm text-muted-foreground">
                      &mdash; {t('brandTable.badge.notAvailable')}
                    </span>
                  )}
                </TableCell>
                <TableCell>
                  <Button
                    size="sm"
                    onClick={() => navigate(`/evaluation/${brand.id}`)}
                  >
                    {t('brandTable.button.evaluate')}
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
  'Nama PIC/ Jabatan*',
  'Kategori',
  'No WA*',
];

const PRIORITY_LABELS: Record<string, string> = {
  'Nama PIC/ Jabatan*': 'Nama PIC',
  'No WA*': 'No WA',
};

function summarizeRawData(rawData: Record<string, unknown>): string {
  const parts: string[] = [];
  for (const key of PRIORITY_KEYS) {
    if (key in rawData && rawData[key] !== '' && rawData[key] != null) {
      const label = PRIORITY_LABELS[key] ?? key;
      parts.push(`${label}: ${String(rawData[key])}`);
    }
    if (parts.length >= 3) break;
  }
  return parts.join(' | ');
}
