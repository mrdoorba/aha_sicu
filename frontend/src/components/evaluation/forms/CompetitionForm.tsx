import { Card, CardContent } from '../../ui/card';
import { Input } from '../../ui/input';
import { Label } from '../../ui/label';
import { CurrencyField } from './CurrencyField';
import type { CompetitionData, CompetitionProduct } from './formConfig';

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

function formatPrice(value: number): string {
  return new Intl.NumberFormat('id-ID').format(value);
}

function CompetitivenessResult({ product }: { product: CompetitionProduct }) {
  const { productName, sellingPrice, keyword, marketPrice } = product;

  if (sellingPrice == null || marketPrice == null) return null;

  const displayName = productName || '—';
  const isNotCompetitive = sellingPrice > marketPrice * 1.1;

  return (
    <div className={`mt-2 rounded-md bg-muted p-2 text-sm ${isNotCompetitive ? 'text-red-600' : 'text-green-600'}`}>
      <p>
        {isNotCompetitive
          ? `• ${displayName} (Rp. ${formatPrice(sellingPrice)}) = ❌tidak kompetitif (harga kisaran pasaran: Rp. ${formatPrice(marketPrice)})`
          : `• ${displayName} (Rp. ${formatPrice(sellingPrice)}) = ✅kompetitif`}
      </p>
      {keyword && <p className="text-muted-foreground">↪{keyword}</p>}
    </div>
  );
}

export function CompetitionForm({ data, onChange, onBlur }: CompetitionFormProps) {
  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 text-sm font-semibold">Kompetisi TOP Produk</p>
        <div className="space-y-4">
          {PRODUCTS.map((product) => {
            const productData = data[product.key];
            return (
              <div key={product.key} className="rounded-lg border p-4">
                <p className="mb-3 text-sm font-medium">{product.label}</p>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {/* Nama Produk */}
                  <div className="space-y-1">
                    <Label htmlFor={`competition.${product.key}.productName`}>
                      Nama Produk
                    </Label>
                    <Input
                      id={`competition.${product.key}.productName`}
                      name={`competition.${product.key}.productName`}
                      type="text"
                      value={productData?.productName ?? ''}
                      onChange={(e) =>
                        onChange('competition', `${product.key}.productName`, e.target.value || null)
                      }
                      onBlur={onBlur}
                      placeholder="—"
                    />
                  </div>

                  {/* Harga Jual */}
                  <CurrencyField
                    name={`competition.${product.key}.sellingPrice`}
                    label="Harga Jual"
                    value={productData?.sellingPrice ?? null}
                    onChange={(v) => onChange('competition', `${product.key}.sellingPrice`, v)}
                    onBlur={onBlur}
                  />

                  {/* Kata kunci pencarian */}
                  <div className="space-y-1">
                    <Label htmlFor={`competition.${product.key}.keyword`}>
                      Kata kunci pencarian
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

                  {/* LINK */}
                  <div className="space-y-1">
                    <Label htmlFor={`competition.${product.key}.link`}>
                      LINK
                    </Label>
                    <Input
                      id={`competition.${product.key}.link`}
                      name={`competition.${product.key}.link`}
                      type="text"
                      value={productData?.link ?? ''}
                      onChange={(e) =>
                        onChange('competition', `${product.key}.link`, e.target.value || null)
                      }
                      onBlur={onBlur}
                      placeholder="—"
                    />
                  </div>

                  {/* Harga rata-rata pasaran */}
                  <CurrencyField
                    name={`competition.${product.key}.marketPrice`}
                    label="Harga rata-rata pasaran"
                    value={productData?.marketPrice ?? null}
                    onChange={(v) => onChange('competition', `${product.key}.marketPrice`, v)}
                    onBlur={onBlur}
                  />
                </div>

                {/* Computed competitiveness result */}
                <CompetitivenessResult product={productData} />
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
