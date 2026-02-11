import { Card, CardContent } from '../../ui/card';
import { CurrencyField } from './CurrencyField';
import { NumberField } from './NumberField';
import type { BusinessData } from './formConfig';
import { BUSINESS_FIELDS } from './formConfig';

interface BusinessFormProps {
  data: BusinessData;
  categoryType: string | null;
  onChange: (category: 'business', key: string, value: number | null) => void;
  onBlur: () => void;
}

export function BusinessForm({ data, categoryType, onChange, onBlur }: BusinessFormProps) {
  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 text-sm font-semibold">Business</p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {BUSINESS_FIELDS.map((field) => {
            const benchmark =
              field.benchmarkFashion && categoryType === 'fashion'
                ? field.benchmarkFashion
                : field.benchmark;

            if (field.inputType === 'currency') {
              return (
                <CurrencyField
                  key={field.key}
                  name={`business.${field.key}`}
                  label={field.label}
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
                label={field.label}
                unit={field.unit}
                benchmark={benchmark}
                value={data[field.key as keyof BusinessData] as number | null}
                onChange={(v) => onChange('business', field.key, v)}
                onBlur={onBlur}
              />
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
