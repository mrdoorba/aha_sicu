import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '../../ui/card';
import { NumberField } from './NumberField';
import { ExternalLink } from 'lucide-react';
import type { VisitorsData } from './formConfig';
import { VISITORS_FIELDS, getSectionLinks } from './formConfig';
import type { ScoringRules } from '../../../hooks/useRules';
import { getBenchmarkFromRules, FORM_TO_RULES_MAP } from './benchmarkUtils';

interface VisitorsFormProps {
  data: VisitorsData;
  storeLink: string | null;
  rules?: ScoringRules;
  marketplace?: string;
  onChange: (category: 'visitors', key: string, value: number | null) => void;
  onBlur: () => void;
}

export function VisitorsForm({ data, storeLink, rules, marketplace = 'ID', onChange, onBlur }: VisitorsFormProps) {
  const { t } = useTranslation();
  const links = getSectionLinks(marketplace);
  const totalVisitors = data.totalVisitors ?? 0;
  const returningVisitors = data.returningVisitors ?? 0;
  const rawPct = totalVisitors > 0 ? (returningVisitors / totalVisitors) * 100 : null;
  const returningPct = rawPct != null ? Math.min(rawPct, 100) : null;

  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 flex items-center gap-2 text-sm font-semibold">
          {t('forms.visitors.title')}
          <a href={links.visitors} target="_blank" rel="noopener noreferrer" aria-label={t('common.aria.openSellerCenter')}>
            <ExternalLink className="size-4 text-muted-foreground" aria-hidden="true" />
          </a>
        </p>
        <div className="grid gap-4 sm:grid-cols-3">
          {VISITORS_FIELDS.map((field) => {
            const mapping = FORM_TO_RULES_MAP[field.key];
            const benchmark = mapping
              ? getBenchmarkFromRules(rules, mapping.category, mapping.key, field.unit, field.benchmark)
              : field.benchmark;

            return (
            <div key={field.key} className="relative">
              <NumberField
                name={`visitors.${field.key}`}
                label={t(field.labelKey!)}
                unit={field.unit}
                benchmark={benchmark}
                value={data[field.key as keyof VisitorsData] as number | null}
                onChange={(v) => onChange('visitors', field.key, v)}
                onBlur={onBlur}
              />
              {field.key === 'totalFollowers' && storeLink && (
                <a
                  href={storeLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={t('common.aria.openStore')}
                  className="absolute right-0 top-0"
                >
                  <ExternalLink className="size-3.5 text-muted-foreground" aria-hidden="true" />
                </a>
              )}
            </div>
            );
          })}
        </div>

        {/* Computed: % Pengunjung Lama */}
        <div className="mt-4">
          <p className="mb-1 text-sm font-medium">{t('forms.visitors.returningPct')}</p>
          <div className="rounded-md bg-muted p-2 text-sm" role="status" aria-live="polite">
            {data.totalVisitors == null || data.totalVisitors === 0
              ? '—'
              : `${returningPct!.toFixed(1)}%`}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
