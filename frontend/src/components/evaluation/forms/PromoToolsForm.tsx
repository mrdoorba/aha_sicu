import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '../../ui/card';
import { CurrencyField } from './CurrencyField';
import { ExternalLink } from 'lucide-react';
import type { PromoToolsData } from './formConfig';
import { PROMO_TOOLS_FIELDS, getSectionLinks, localizeSellerLink } from './formConfig';

interface PromoToolsFormProps {
  data: PromoToolsData;
  salesMonth0: number;
  currency?: string;
  marketplace?: string;
  onChange: (category: 'promoTools', key: string, value: number | null) => void;
  onBlur: () => void;
}

export function PromoToolsForm({ data, salesMonth0, currency = 'IDR', marketplace = 'ID', onChange, onBlur }: PromoToolsFormProps) {
  const { t } = useTranslation();
  const links = getSectionLinks(marketplace);
  const metricFields = PROMO_TOOLS_FIELDS.filter((field) => field.key !== 'komisiProgramAfiliasi');

  // % Penggunaan: count of metric-bearing tools with value > 0
  const usageCount = metricFields.filter((f) => {
    const val = data[f.key as keyof PromoToolsData];
    return val != null && val > 0;
  }).length;
  const usagePct = Math.round((usageCount / metricFields.length) * 100);

  // % Efektifitas: count of metric-bearing tools exceeding threshold
  // Mirrors backend _promo_verdict(): D=0→❌, promoToko at D/D13≥50%→❌ (too dependent),
  // then benchmark check
  const effectivenessResult = (() => {
    if (!salesMonth0) return null; // 0 or null → show "—"
    const passingCount = metricFields.filter((f) => {
      const val = data[f.key as keyof PromoToolsData] ?? 0;
      if (f.threshold == null) return false;
      if (val === 0) return false;
      // gratisOngkir is absolute threshold (>0), not percentage-based
      if (f.key === 'gratisOngkir') return val > f.threshold;
      // Too dependent: promoToko ≥ 50% of total sales → fail. Only promoToko —
      // the source sheet puts this branch on row 31 alone, and applying it to
      // every tool made voucher (68% benchmark) impossible to pass here while
      // the backend passed it.
      if (f.key === 'promoToko' && val / salesMonth0 >= 0.5) return false;
      return val >= salesMonth0 * f.threshold;
    }).length;
    return Math.round((passingCount / metricFields.length) * 100);
  })();

  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 flex items-center gap-2 text-sm font-semibold">
          {t('forms.promoTools.title')}
          <a href={links.promoTools} target="_blank" rel="noopener noreferrer" aria-label={t('common.aria.openSellerCenter')}>
            <ExternalLink className="size-4 text-muted-foreground" aria-hidden="true" />
          </a>
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {PROMO_TOOLS_FIELDS.map((field) => (
            <div key={field.key}>
              <div className="flex items-center gap-1">
                <CurrencyField
                  name={`promoTools.${field.key}`}
                  label={t(field.labelKey!)}
                  benchmark={field.benchmarkKey ? t(field.benchmarkKey) : field.benchmark}
                  currency={currency}
                  value={data[field.key as keyof PromoToolsData] as number | null}
                  onChange={(v) => onChange('promoTools', field.key, v)}
                  onBlur={onBlur}
                />
                {field.link && (
                  <a href={localizeSellerLink(field.link, marketplace)} target="_blank" rel="noopener noreferrer" aria-label={t('common.aria.openShopeeRef')} className="mt-5 shrink-0">
                    <ExternalLink className="size-3.5 text-muted-foreground" aria-hidden="true" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Computed fields */}
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <p className="mb-1 text-sm font-medium">{t('forms.promoTools.usagePct')}</p>
            <div className="rounded-md bg-muted p-2 text-sm" role="status" aria-live="polite">
              {usagePct}%
            </div>
          </div>
          <div>
            <p className="mb-1 text-sm font-medium">{t('forms.promoTools.effectivenessPct')}</p>
            <div className="rounded-md bg-muted p-2 text-sm" role="status" aria-live="polite">
              {effectivenessResult == null ? '—' : `${effectivenessResult}%`}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
