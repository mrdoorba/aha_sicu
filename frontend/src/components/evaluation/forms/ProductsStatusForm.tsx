import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '../../ui/card';
import { NumberField } from './NumberField';
import { SelectField } from './SelectField';
import { ExternalLink } from 'lucide-react';
import type { ProductsData } from './formConfig';
import { PRODUCTS_FIELDS, STORE_STATUS_OPTIONS } from './formConfig';

interface ProductsStatusFormProps {
  data: ProductsData;
  storeLink: string | null;
  onChange: (category: 'products', key: string, value: number | string | null) => void;
  onBlur: () => void;
}

export function ProductsStatusForm({ data, storeLink, onChange, onBlur }: ProductsStatusFormProps) {
  const { t } = useTranslation();

  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 flex items-center gap-2 text-sm font-semibold">
          {t('forms.products.title')}
          {storeLink && (
            <a href={storeLink} target="_blank" rel="noopener noreferrer" aria-label={t('common.aria.openStore')}>
              <ExternalLink className="size-4 text-muted-foreground" aria-hidden="true" />
            </a>
          )}
        </p>
        <div className="grid gap-4 sm:grid-cols-2">
          {PRODUCTS_FIELDS.map((field) => {
            if (field.inputType === 'select') {
              return (
                <SelectField
                  key={field.key}
                  name={`products.${field.key}`}
                  label={field.label}
                  options={STORE_STATUS_OPTIONS}
                  benchmark={field.benchmark}
                  value={data.storeStatus}
                  onChange={(v) => {
                    onChange('products', field.key, v);
                    onBlur(); // Trigger auto-save — dropdown selection IS the commit action
                  }}
                />
              );
            }

            return (
              <NumberField
                key={field.key}
                name={`products.${field.key}`}
                label={field.label}
                unit={field.unit}
                benchmark={field.benchmark}
                value={data[field.key as keyof ProductsData] as number | null}
                onChange={(v) => onChange('products', field.key, v)}
                onBlur={onBlur}
              />
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
