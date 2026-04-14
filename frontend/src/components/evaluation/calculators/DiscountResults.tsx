import { useTranslation } from 'react-i18next';
import { AlertTriangle } from 'lucide-react';
import { Badge } from '../../ui/badge';
import type { CalculatorResult } from '../../../hooks/useCalculator';
import { isDiscountDetails } from '../../../lib/calculatorGuards';
import { getIntlLocale } from '../../../lib/languages';

interface DiscountResultsProps {
  result: CalculatorResult;
}

export function DiscountResults({ result }: DiscountResultsProps) {
  const { t, i18n } = useTranslation();

  if (!isDiscountDetails(result.details)) {
    return <p className="text-sm text-muted-foreground">{t('discount.invalidData')}</p>;
  }
  const details = result.details;

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-sm font-semibold">{t('discount.title')}</h4>
        <time className="text-xs text-muted-foreground">
          {new Date(result.calculated_at).toLocaleString(getIntlLocale(i18n.language))}
        </time>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-muted-foreground">{t('discount.topSkuDiscount')}</span>
          <span className="font-medium">{details.discount_pct}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">{t('discount.range')}</span>
          <span className="font-medium">{details.range_min} ~ {details.range_max}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">{t('discount.voucher')}</span>
          <span className="font-medium">{details.voucher_pct}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">{t('discount.packageDiscount')}</span>
          <span className="font-medium">{details.paket_pct}</span>
        </div>
        {details.affiliate_commission_pct && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">{t('discount.affiliateCommission')}</span>
            <span className="font-medium">{details.affiliate_commission_pct}</span>
          </div>
        )}
        {details.fake_discount_flag && (
          <Badge variant="destructive" className="mt-1 gap-1">
            <AlertTriangle className="size-3" />
            {t('discount.fakeDiscountDetected')}
          </Badge>
        )}
      </div>
    </div>
  );
}
