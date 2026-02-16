import { Card, CardContent } from '../../ui/card';
import { CurrencyField } from './CurrencyField';
import { ExternalLink } from 'lucide-react';
import type { PromoToolsData } from './formConfig';
import { PROMO_TOOLS_FIELDS, SECTION_LINKS } from './formConfig';

interface PromoToolsFormProps {
  data: PromoToolsData;
  salesMonth0: number;
  onChange: (category: 'promoTools', key: string, value: number | null) => void;
  onBlur: () => void;
}

export function PromoToolsForm({ data, salesMonth0, onChange, onBlur }: PromoToolsFormProps) {
  // % Penggunaan: count of tools with value > 0 / 11
  const usageCount = PROMO_TOOLS_FIELDS.filter((f) => {
    const val = data[f.key as keyof PromoToolsData];
    return val != null && val > 0;
  }).length;
  const usagePct = (usageCount / PROMO_TOOLS_FIELDS.length) * 100;

  // % Efektifitas: count of tools exceeding threshold / 11
  const effectivenessResult = (() => {
    if (!salesMonth0) return null; // 0 or null → show "—"
    const passingCount = PROMO_TOOLS_FIELDS.filter((f) => {
      const val = data[f.key as keyof PromoToolsData] ?? 0;
      if (f.threshold == null) return false;
      // gratisOngkir is absolute threshold (>0), not percentage-based
      if (f.key === 'gratisOngkir') return val > f.threshold;
      return val > salesMonth0 * f.threshold;
    }).length;
    return (passingCount / PROMO_TOOLS_FIELDS.length) * 100;
  })();

  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 flex items-center gap-2 text-sm font-semibold">
          Alat Promosi
          <a href={SECTION_LINKS.promoTools} target="_blank" rel="noopener noreferrer">
            <ExternalLink className="size-4 text-muted-foreground" />
          </a>
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {PROMO_TOOLS_FIELDS.map((field) => (
            <div key={field.key}>
              <div className="flex items-center gap-1">
                <CurrencyField
                  name={`promoTools.${field.key}`}
                  label={field.label}
                  benchmark={field.benchmark}
                  value={data[field.key as keyof PromoToolsData] as number | null}
                  onChange={(v) => onChange('promoTools', field.key, v)}
                  onBlur={onBlur}
                />
                {field.link && (
                  <a href={field.link} target="_blank" rel="noopener noreferrer" className="mt-5 shrink-0">
                    <ExternalLink className="size-3.5 text-muted-foreground" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Computed fields */}
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <p className="mb-1 text-sm font-medium">% Penggunaan alat promosi</p>
            <div className="rounded-md bg-muted p-2 text-sm">
              {usagePct.toFixed(1)}%
            </div>
          </div>
          <div>
            <p className="mb-1 text-sm font-medium">% Efektifitas alat promosi</p>
            <div className="rounded-md bg-muted p-2 text-sm">
              {effectivenessResult == null ? '—' : `${effectivenessResult.toFixed(1)}%`}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
