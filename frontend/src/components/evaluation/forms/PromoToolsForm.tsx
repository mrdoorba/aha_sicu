import { Card, CardContent } from '../../ui/card';
import { CurrencyField } from './CurrencyField';
import type { PromoToolsData } from './formConfig';
import { PROMO_TOOLS_FIELDS } from './formConfig';

interface PromoToolsFormProps {
  data: PromoToolsData;
  onChange: (category: 'promoTools', key: string, value: number | null) => void;
  onBlur: () => void;
}

export function PromoToolsForm({ data, onChange, onBlur }: PromoToolsFormProps) {
  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 text-sm font-semibold">Promo Tools</p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {PROMO_TOOLS_FIELDS.map((field) => (
            <CurrencyField
              key={field.key}
              name={`promoTools.${field.key}`}
              label={field.label}
              benchmark={field.benchmark}
              value={data[field.key as keyof PromoToolsData] as number | null}
              onChange={(v) => onChange('promoTools', field.key, v)}
              onBlur={onBlur}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
