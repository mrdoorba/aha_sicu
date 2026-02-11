import { Card, CardContent } from '../../ui/card';
import { NumberField } from './NumberField';
import type { VisitorsData } from './formConfig';
import { VISITORS_FIELDS } from './formConfig';

interface VisitorsFormProps {
  data: VisitorsData;
  onChange: (category: 'visitors', key: string, value: number | null) => void;
  onBlur: () => void;
}

export function VisitorsForm({ data, onChange, onBlur }: VisitorsFormProps) {
  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 text-sm font-semibold">Visitors</p>
        <div className="grid gap-4 sm:grid-cols-3">
          {VISITORS_FIELDS.map((field) => (
            <NumberField
              key={field.key}
              name={`visitors.${field.key}`}
              label={field.label}
              unit={field.unit}
              benchmark={field.benchmark}
              value={data[field.key as keyof VisitorsData] as number | null}
              onChange={(v) => onChange('visitors', field.key, v)}
              onBlur={onBlur}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
