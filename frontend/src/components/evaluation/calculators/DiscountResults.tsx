import { AlertTriangle } from 'lucide-react';
import { Badge } from '../../ui/badge';
import type { CalculatorResult, DiscountDetails } from '../../../hooks/useCalculator';

interface DiscountResultsProps {
  result: CalculatorResult;
}

export function DiscountResults({ result }: DiscountResultsProps) {
  const details = result.details as DiscountDetails;

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-sm font-semibold">Discount Check Calculator</h4>
        <time className="text-xs text-muted-foreground">
          {new Date(result.calculated_at).toLocaleString('id-ID')}
        </time>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-muted-foreground">% Diskon TOP SKU</span>
          <span className="font-medium">{details.discount_pct}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Range</span>
          <span className="font-medium">{details.range_min} ~ {details.range_max}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Voucher</span>
          <span className="font-medium">{details.voucher_pct}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Paket Diskon</span>
          <span className="font-medium">{details.paket_pct}</span>
        </div>
        {details.fake_discount_flag && (
          <Badge variant="destructive" className="mt-1 gap-1">
            <AlertTriangle className="size-3" />
            Fake Discount Detected
          </Badge>
        )}
      </div>
    </div>
  );
}
