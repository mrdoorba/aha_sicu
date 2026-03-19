import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '../../ui/card';
import { CurrencyField } from './CurrencyField';
import { NumberField } from './NumberField';
import { ExternalLink } from 'lucide-react';
import type { BusinessData } from './formConfig';
import { BUSINESS_FIELDS, getSectionLinks, generateMonthLabels, formatCurrency } from './formConfig';
import type { ScoringRules } from '../../../hooks/useRules';
import { getBenchmarkFromRules, FORM_TO_RULES_MAP } from './benchmarkUtils';
import { getIntlLocale } from '../../../lib/localeMap';

interface BusinessFormProps {
  data: BusinessData;
  rules?: ScoringRules;
  currency?: string;
  marketplace?: string;
  onChange: (category: 'business', key: string, value: number | string | null) => void;
  onBlur: () => void;
}

export function BusinessForm({ data, rules, currency = 'IDR', marketplace = 'ID', onChange, onBlur }: BusinessFormProps) {
  const { t, i18n } = useTranslation();
  const links = getSectionLinks(marketplace);
  const monthLabels = useMemo(() => generateMonthLabels(data.salesStartMonth), [data.salesStartMonth]);

  // Generate month options for the selector (last 12 months from now)
  const monthOptions = useMemo(() => {
    const options: Array<{ value: string; label: string }> = [];
    const now = new Date();
    for (let i = 0; i < 12; i++) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const val = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
      const label = d.toLocaleDateString(getIntlLocale(i18n.language), { month: 'short', year: 'numeric' });
      options.push({ value: val, label });
    }
    return options;
  }, [i18n.language]);

  // Dynamic label overrides for sales months and conversion rate
  const getFieldLabel = (field: typeof BUSINESS_FIELDS[number], index: number): string => {
    if (field.key === 'conversionRate') {
      return t('forms.business.conversionRate', { month: t(monthLabels[0]) });
    }
    if (field.key.startsWith('salesMonth')) {
      return t('forms.business.salesMonth', { month: t(monthLabels[index]) });
    }
    return t(field.labelKey!);
  };

  // Computed average of 6 months
  const salesMonths = [data.salesMonth0, data.salesMonth1, data.salesMonth2, data.salesMonth3, data.salesMonth4, data.salesMonth5];
  const allNull = salesMonths.every((v) => v == null);
  const average = allNull ? null : salesMonths.reduce<number>((sum, v) => sum + (v ?? 0), 0) / 6;

  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 flex items-center gap-2 text-sm font-semibold">
          {t('forms.business.title')}
          <a href={links.business} target="_blank" rel="noopener noreferrer" aria-label={t('common.aria.openSellerCenter')}>
            <ExternalLink className="size-4 text-muted-foreground" aria-hidden="true" />
          </a>
        </p>

        {/* Month selector */}
        <div className="mb-4">
          <label htmlFor="salesStartMonth" className="mb-1 block text-sm font-medium">
            {t('forms.business.startMonth')}
          </label>
          <select
            id="salesStartMonth"
            className="rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={data.salesStartMonth ?? ''}
            onChange={(e) => {
              onChange('business', 'salesStartMonth', e.target.value || null);
            }}
            onBlur={onBlur}
          >
            <option value="">{t('forms.business.selectMonth')}</option>
            {monthOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {BUSINESS_FIELDS.map((field, index) => {
            const label = getFieldLabel(field, index);
            const mapping = FORM_TO_RULES_MAP[field.key];
            const benchmark = mapping
              ? getBenchmarkFromRules(rules, mapping.category, mapping.key, field.unit, field.benchmark)
              : field.benchmark;

            if (field.inputType === 'currency') {
              return (
                <CurrencyField
                  key={field.key}
                  name={`business.${field.key}`}
                  label={label}
                  benchmark={benchmark}
                  currency={currency}
                  value={data[field.key as keyof BusinessData] as number | null}
                  onChange={(v) => onChange('business', field.key, v)}
                  onBlur={onBlur}
                />
              );
            }

            return (
              <NumberField
                key={field.key}
                name={`business.${field.key}`}
                label={label}
                unit={field.unit}
                benchmark={benchmark}
                value={data[field.key as keyof BusinessData] as number | null}
                onChange={(v) => onChange('business', field.key, v)}
                onBlur={onBlur}
              />
            );
          })}
        </div>

        {/* Computed: Average sales */}
        <div className="mt-4">
          <p className="mb-1 text-sm font-medium">{t('forms.business.averageSales')}</p>
          <div className="rounded-md bg-muted p-2 text-sm" role="status" aria-live="polite">
            {average == null ? '—' : `${currency} ${formatCurrency(average)}`}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
