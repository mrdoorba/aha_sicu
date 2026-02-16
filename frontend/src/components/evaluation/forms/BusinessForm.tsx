import { useMemo } from 'react';
import { Card, CardContent } from '../../ui/card';
import { CurrencyField } from './CurrencyField';
import { NumberField } from './NumberField';
import { ExternalLink } from 'lucide-react';
import type { BusinessData } from './formConfig';
import { BUSINESS_FIELDS, SECTION_LINKS, generateMonthLabels } from './formConfig';

interface BusinessFormProps {
  data: BusinessData;
  categoryType: string | null;
  onChange: (category: 'business', key: string, value: number | string | null) => void;
  onBlur: () => void;
}

function formatCurrencyDisplay(value: number): string {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value);
}

export function BusinessForm({ data, categoryType, onChange, onBlur }: BusinessFormProps) {
  const monthLabels = useMemo(() => generateMonthLabels(data.salesStartMonth), [data.salesStartMonth]);

  // Generate month options for the selector (last 12 months from now)
  const monthOptions = useMemo(() => {
    const options: Array<{ value: string; label: string }> = [];
    const now = new Date();
    for (let i = 0; i < 12; i++) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const val = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
      const label = d.toLocaleDateString('id-ID', { month: 'short', year: 'numeric' });
      options.push({ value: val, label });
    }
    return options;
  }, []);

  // Dynamic label overrides for sales months and conversion rate
  const getFieldLabel = (field: typeof BUSINESS_FIELDS[number], index: number): string => {
    if (field.key === 'conversionRate') {
      return `Tingkat Konversi ${monthLabels[0]}`;
    }
    if (field.key.startsWith('salesMonth')) {
      return `Penjualan Bulan ${monthLabels[index]}`;
    }
    return field.label;
  };

  // Computed average of 6 months
  const salesMonths = [data.salesMonth0, data.salesMonth1, data.salesMonth2, data.salesMonth3, data.salesMonth4, data.salesMonth5];
  const allNull = salesMonths.every((v) => v == null);
  const average = allNull ? null : salesMonths.reduce<number>((sum, v) => sum + (v ?? 0), 0) / 6;

  // Conversion rate benchmark depends on category type
  const conversionBenchmark = categoryType === 'fashion' ? '>2%' : '>3%';

  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 flex items-center gap-2 text-sm font-semibold">
          Bisnis Analisis
          <a href={SECTION_LINKS.business} target="_blank" rel="noopener noreferrer" aria-label="Buka Shopee Seller Center (tab baru)">
            <ExternalLink className="size-4 text-muted-foreground" aria-hidden="true" />
          </a>
        </p>

        {/* Month selector */}
        <div className="mb-4">
          <label htmlFor="salesStartMonth" className="mb-1 block text-sm font-medium">
            Bulan Awal Penjualan
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
            <option value="">-- Pilih Bulan --</option>
            {monthOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {BUSINESS_FIELDS.map((field, index) => {
            const label = getFieldLabel(field, index);
            const benchmark = field.key === 'conversionRate' ? conversionBenchmark : field.benchmark;

            if (field.inputType === 'currency') {
              return (
                <CurrencyField
                  key={field.key}
                  name={`business.${field.key}`}
                  label={label}
                  benchmark={benchmark}
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
          <p className="mb-1 text-sm font-medium">Rata-rata Penjualan 6 Bulan Terakhir</p>
          <div className="rounded-md bg-muted p-2 text-sm" role="status" aria-live="polite">
            {average == null ? '—' : formatCurrencyDisplay(average)}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
