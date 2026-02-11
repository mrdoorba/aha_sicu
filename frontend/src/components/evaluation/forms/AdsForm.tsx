import { Card, CardContent } from '../../ui/card';
import { CurrencyField } from './CurrencyField';
import type { AdsData } from './formConfig';
import { ADS_FIELDS } from './formConfig';

interface AdsFormProps {
  data: AdsData;
  onChange: (category: 'ads', key: string, value: number | null) => void;
  onBlur: () => void;
}

export function AdsForm({ data, onChange, onBlur }: AdsFormProps) {
  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 text-sm font-semibold">Ads</p>
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
      </CardContent>
    </Card>
  );
}
