import { Card, CardContent } from '../../ui/card';
import { CurrencyField } from './CurrencyField';
import { ExternalLink } from 'lucide-react';
import type { AdsData } from './formConfig';
import { ADS_FIELDS, SECTION_LINKS } from './formConfig';

interface AdsFormProps {
  data: AdsData;
  salesMonth0: number;
  onChange: (category: 'ads', key: string, value: number | null) => void;
  onBlur: () => void;
}

export function AdsForm({ data, salesMonth0, onChange, onBlur }: AdsFormProps) {
  const adSales = data.adSales ?? 0;
  const adCost = data.adCost ?? 0;

  const roi = adCost > 0 ? adSales / adCost : null;
  const gmvAdsPct = salesMonth0 > 0 ? (adSales / salesMonth0) * 100 : null;
  const costAdsPct = salesMonth0 > 0 ? (adCost / salesMonth0) * 100 : null;

  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 flex items-center gap-2 text-sm font-semibold">
          Data Iklan
          <a href={SECTION_LINKS.ads} target="_blank" rel="noopener noreferrer" aria-label="Buka Shopee Seller Center (tab baru)">
            <ExternalLink className="size-4 text-muted-foreground" aria-hidden="true" />
          </a>
        </p>
        <div className="grid gap-4 sm:grid-cols-2">
          {ADS_FIELDS.map((field) => (
            <CurrencyField
              key={field.key}
              name={`ads.${field.key}`}
              label={field.label}
              benchmark={field.benchmark}
              value={data[field.key as keyof AdsData] as number | null}
              onChange={(v) => onChange('ads', field.key, v)}
              onBlur={onBlur}
            />
          ))}
        </div>

        {/* Computed fields */}
        <div className="mt-4 grid gap-4 sm:grid-cols-3">
          <div>
            <p className="mb-1 text-sm font-medium">ROAS</p>
            <div className="rounded-md bg-muted p-2 text-sm" role="status" aria-live="polite">
              {roi == null ? '—' : roi.toFixed(2)}
            </div>
          </div>
          <div>
            <p className="mb-1 text-sm font-medium">% GMV Iklan / GMV Toko</p>
            <div className="rounded-md bg-muted p-2 text-sm" role="status" aria-live="polite">
              {gmvAdsPct == null ? '—' : `${gmvAdsPct.toFixed(1)}%`}
            </div>
          </div>
          <div>
            <p className="mb-1 text-sm font-medium">% Biaya Iklan / GMV Toko</p>
            <div className="rounded-md bg-muted p-2 text-sm" role="status" aria-live="polite">
              {costAdsPct == null ? '—' : `${costAdsPct.toFixed(1)}%`}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
