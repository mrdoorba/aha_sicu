import { useMutation, useQueryClient } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface AdsKeywordDetails {
  ak2: string;
  ak3: string;
  ak4: string;
  al2: string;
  al3: string;
  al5: string;
  al6: string;
  al7: string;
  al8: string;
  al9: string;
  thresholds: {
    am6: number;
    am7: number;
    am9: number;
    am10: number;
  };
}

export interface DiscountDetails {
  discount_pct: string;
  range_min: string;
  range_max: string;
  voucher_pct: string;
  paket_pct: string;
  fake_discount_flag: boolean;
  product_summary: Array<{
    product_name: string;
    qty: number;
    avg_discount_pct: number;
  }>;
  top_sku: Array<{
    product_name: string;
    qty: number;
    avg_discount_pct: number;
  }>;
  totals: {
    sum_n: number;
    sum_p: number;
    sum_voucher: number;
    sum_paket: number;
    sum_harga_setelah_diskon: number;
  };
}

export type CalculatorDetails = AdsKeywordDetails | DiscountDetails;

export interface CalculatorResult {
  calculator_type: string;
  output_text: string;
  details: CalculatorDetails;
  calculated_at: string;
}

type CalculatorType = 'ads_keyword' | 'discount';

const CALCULATOR_PATHS = {
  ads_keyword: '/api/v1/evaluations/brands/{brand_id}/calculators/ads_keyword',
  discount: '/api/v1/evaluations/brands/{brand_id}/calculators/discount',
} as const;

export function useRunCalculator(brandId: number, calculatorType: CalculatorType) {
  const queryClient = useQueryClient();

  return useMutation<CalculatorResult>({
    mutationFn: async () => {
      const path = CALCULATOR_PATHS[calculatorType];
      const { data, error } = await client.POST(path, {
        params: { path: { brand_id: brandId } },
      });
      if (error) throw error;
      return data as CalculatorResult;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calculatorResults', brandId] });
    },
  });
}
