import { Card, CardContent } from '../../ui/card';
import { CurrencyField } from './CurrencyField';
import { NumberField } from './NumberField';
import type { BusinessData } from './formConfig';
import { BUSINESS_FIELDS } from './formConfig';

interface BusinessFormProps {
  data: BusinessData;
  onChange: (category: 'business', key: string, value: number | null) => void;
  onBlur: () => void;
}

export function BusinessForm({ data, onChange, onBlur }: BusinessFormProps) {
  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 text-sm font-semibold">Business</p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {BUSINESS_FIELDS.map((field) => {
            if (field.inputType === 'currency') {
              return (
                <CurrencyField
                  key={field.key}
                  name={`business.${field.key}`}
                  label={field.label}
                  benchmark={field.benchmark}
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
                benchmark={field.benchmark}
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
