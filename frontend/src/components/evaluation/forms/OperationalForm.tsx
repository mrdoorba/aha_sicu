import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '../../ui/card';
import { NumberField } from './NumberField';
import { ExternalLink } from 'lucide-react';
import type { OperationalData } from './formConfig';
import { OPERATIONAL_FIELDS, SECTION_LINKS } from './formConfig';

interface OperationalFormProps {
  data: OperationalData;
  onChange: (category: 'operational', key: string, value: number | null) => void;
  onBlur: () => void;
}

export function OperationalForm({ data, onChange, onBlur }: OperationalFormProps) {
  const { t } = useTranslation();

  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 flex items-center gap-2 text-sm font-semibold">
          {t('forms.operational.title')}
          <a href={SECTION_LINKS.operational} target="_blank" rel="noopener noreferrer" aria-label={t('common.aria.openSellerCenter')}>
            <ExternalLink className="size-4 text-muted-foreground" aria-hidden="true" />
          </a>
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {OPERATIONAL_FIELDS.map((field) => (
            <NumberField
              key={field.key}
              name={`operational.${field.key}`}
              label={field.label}
              unit={field.unit}
              benchmark={field.benchmark}
              value={data[field.key as keyof OperationalData] as number | null}
              onChange={(v) => onChange('operational', field.key, v)}
              onBlur={onBlur}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
