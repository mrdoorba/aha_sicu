import { Card, CardContent } from '../../ui/card';
import { NumberField } from './NumberField';
import { SelectField } from './SelectField';
import type { ProductsData } from './formConfig';
import { PRODUCTS_FIELDS, STORE_STATUS_OPTIONS } from './formConfig';

interface ProductsStatusFormProps {
  data: ProductsData;
  onChange: (category: 'products', key: string, value: number | string | null) => void;
  onBlur: () => void;
}

export function ProductsStatusForm({ data, onChange, onBlur }: ProductsStatusFormProps) {
  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 text-sm font-semibold">Products / Status</p>
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
