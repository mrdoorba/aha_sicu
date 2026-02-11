import { Card, CardContent } from '../../ui/card';
import { Input } from '../../ui/input';
import { Label } from '../../ui/label';
import { CurrencyField } from './CurrencyField';
import type { CompetitionData } from './formConfig';

interface CompetitionFormProps {
  data: CompetitionData;
  onChange: (category: 'competition', key: string, value: string | number | null) => void;
  onBlur: () => void;
}

const PRODUCTS = [
  { key: 'product1', label: 'Produk Kompetitor 1' },
  { key: 'product2', label: 'Produk Kompetitor 2' },
  { key: 'product3', label: 'Produk Kompetitor 3' },
] as const;

export function CompetitionForm({ data, onChange, onBlur }: CompetitionFormProps) {
  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 text-sm font-semibold">Competition</p>
        <div className="space-y-4">
          {PRODUCTS.map((product) => {
            const productData = data[product.key];
            return (
              <div key={product.key} className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-1">
                  <Label htmlFor={`competition.${product.key}.keyword`}>
                    {product.label} — Keyword
                  </Label>
                  <Input
                    id={`competition.${product.key}.keyword`}
                    name={`competition.${product.key}.keyword`}
                    type="text"
                    value={productData?.keyword ?? ''}
                    onChange={(e) =>
                      onChange('competition', `${product.key}.keyword`, e.target.value || null)
                    }
                    onBlur={onBlur}
                    placeholder="—"
                  />
                </div>
                <CurrencyField
                  name={`competition.${product.key}.marketPrice`}
                  label={`${product.label} — Harga Pasar`}
                  value={productData?.marketPrice ?? null}
                  onChange={(v) => onChange('competition', `${product.key}.marketPrice`, v)}
                  onBlur={onBlur}
                />
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
