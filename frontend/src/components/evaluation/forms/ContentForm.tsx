import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '../../ui/card';
import { NumberField } from './NumberField';
import type { ContentData } from './formConfig';
import { CONTENT_FIELDS } from './formConfig';

interface ContentFormProps {
  data: ContentData;
  onChange: (category: 'content', key: string, value: number | null) => void;
  onBlur: () => void;
}

export function ContentForm({ data, onChange, onBlur }: ContentFormProps) {
  const { t } = useTranslation();
  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 text-sm font-semibold">{t('forms.content.title')}</p>
        <div className="grid gap-4 sm:grid-cols-2">
          {CONTENT_FIELDS.map((field) => (
            <NumberField
              key={field.key}
              name={`content.${field.key}`}
              label={field.label}
              unit={field.unit}
              benchmark={field.benchmark}
              value={data[field.key as keyof ContentData] as number | null}
              onChange={(v) => onChange('content', field.key, v)}
              onBlur={onBlur}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
