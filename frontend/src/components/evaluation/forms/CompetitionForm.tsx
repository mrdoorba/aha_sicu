import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '../../ui/card';
import { Input } from '../../ui/input';
import { Label } from '../../ui/label';
import { buildShopeeSearchUrl } from './competitionUtils';
import { CurrencyField } from './CurrencyField';
import type { CompetitionData, CompetitionProduct } from './formConfig';

interface CompetitionFormProps {
  data: CompetitionData;
  onChange: (category: 'competition', key: string, value: string | number | null) => void;
  onBlur: () => void;
}

const PRODUCTS = [
  { key: 'product1', labelKey: 'forms.competition.product1' },
  { key: 'product2', labelKey: 'forms.competition.product2' },
  { key: 'product3', labelKey: 'forms.competition.product3' },
] as const;

function formatPrice(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}

function CompetitivenessResult({ product }: { product: CompetitionProduct }) {
  const { t } = useTranslation();
  const { productName, sellingPrice, keyword, marketPrice } = product;

  if (sellingPrice == null || marketPrice == null || marketPrice === 0) return null;

  const displayName = productName || '—';
  const isNotCompetitive = sellingPrice > marketPrice * 1.1;

  return (
    <div className={`mt-2 rounded-md bg-muted p-2 text-sm ${isNotCompetitive ? 'text-red-600' : 'text-green-600'}`} role="status" aria-live="polite">
      <p>
        {isNotCompetitive
          ? t('forms.competition.notCompetitive', { name: displayName, price: formatPrice(sellingPrice), marketPrice: formatPrice(marketPrice) })
          : t('forms.competition.competitive', { name: displayName, price: formatPrice(sellingPrice) })}
      </p>
      {keyword && <p className="text-muted-foreground">↪{keyword}</p>}
    </div>
  );
}

export function CompetitionForm({ data, onChange, onBlur }: CompetitionFormProps) {
  const { t } = useTranslation();

  return (
    <Card className="mb-4">
      <CardContent className="pt-4">
        <p className="mb-3 text-sm font-semibold">{t('forms.competition.title')}</p>
        <div className="space-y-4">
          {PRODUCTS.map((product) => {
            const productData = data[product.key];
            return (
              <div key={product.key} className="rounded-lg border p-4">
                <p className="mb-3 text-sm font-medium">{t(product.labelKey)}</p>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {/* Nama Produk */}
                  <div className="space-y-1">
                    <Label htmlFor={`competition.${product.key}.productName`}>
                      {t('forms.competition.productName')}
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
                    label={t('forms.competition.sellingPrice')}
                    value={productData?.sellingPrice ?? null}
                    onChange={(v) => {
                      onChange('competition', `${product.key}.sellingPrice`, v);
                      onChange('competition', `${product.key}.link`, buildShopeeSearchUrl(v, productData?.keyword ?? null));
                    }}
                    onBlur={onBlur}
                  />

                  {/* Kata kunci pencarian */}
                  <div className="space-y-1">
                    <Label htmlFor={`competition.${product.key}.keyword`}>
                      {t('forms.competition.keyword')}
                    </Label>
                    <Input
                      id={`competition.${product.key}.keyword`}
                      name={`competition.${product.key}.keyword`}
                      type="text"
                      value={productData?.keyword ?? ''}
                      onChange={(e) => {
                        const kw = e.target.value || null;
                        onChange('competition', `${product.key}.keyword`, kw);
                        onChange('competition', `${product.key}.link`, buildShopeeSearchUrl(productData?.sellingPrice ?? null, kw));
                      }}
                      onBlur={onBlur}
                      placeholder="—"
                    />
                  </div>

                  {/* LINK */}
                  <div className="space-y-1">
                    <Label>{t('forms.competition.link')}</Label>
                    {productData?.link ? (
                      <a
                        href={productData.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block truncate text-sm text-blue-600 underline"
                      >
                        {t('forms.competition.linkText')}
                      </a>
                    ) : (
                      <p className="text-sm text-muted-foreground">{t('forms.competition.linkPlaceholder')}</p>
                    )}
                  </div>

                  {/* Harga rata-rata pasaran */}
                  <CurrencyField
                    name={`competition.${product.key}.marketPrice`}
                    label={t('forms.competition.marketPrice')}
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
