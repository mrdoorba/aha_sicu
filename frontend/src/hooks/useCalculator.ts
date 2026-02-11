import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
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

export interface TopSkuDetails {
  output_1: Array<{
    kode_variasi: string;
    product_name: string;
    total_omzet: number;
    rata2_harga_jual: number;
  }>;
  output_2: Array<{
    kode_variasi: string;
    nama_produk: string;
    varian: string;
    stok: number;
  }>;
  average_stock: number;
  product_count: number;
  total_unique_products: number;
}

export type CalculatorDetails = AdsKeywordDetails | DiscountDetails | TopSkuDetails;

export interface CalculatorResult {
  calculator_type: string;
  output_text: string;
  details: CalculatorDetails;
  calculated_at: string;
}

export interface CalculatorResultsListResponse {
  brand_id: number;
  results: CalculatorResult[];
}

type CalculatorType = 'ads_keyword' | 'discount' | 'top_sku';

const CALCULATOR_PATHS = {
  ads_keyword: '/api/v1/evaluations/brands/{brand_id}/calculators/ads_keyword',
  discount: '/api/v1/evaluations/brands/{brand_id}/calculators/discount',
  top_sku: '/api/v1/evaluations/brands/{brand_id}/calculators/top_sku',
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
      queryClient.invalidateQueries({ queryKey: ['calculatorStatus', brandId] });
    },
  });
}

// ---------------------------------------------------------------------------
// Fetch stored calculator results hook
// ---------------------------------------------------------------------------

export function useCalculatorResults(brandId: number) {
  return useQuery<CalculatorResultsListResponse>({
    queryKey: ['calculatorResults', brandId],
    queryFn: async () => {
      const { data, error } = await client.GET(
        '/api/v1/evaluations/brands/{brand_id}/calculators/results',
        { params: { path: { brand_id: brandId } } },
      );
      if (error) throw error;
      return data as CalculatorResultsListResponse;
    },
    enabled: brandId > 0,
  });
}

// ---------------------------------------------------------------------------
// Calculator status types and hook
// ---------------------------------------------------------------------------

export interface SingleCalculatorStatus {
  status: 'ready' | 'pending';
  has_result: boolean;
  required_files: string[];
  required_manual: string[];
  available_files: string[];
  missing_files: string[];
  missing_manual: string[];
  calculated_at: string | null;
}

export interface CalculatorStatusResponse {
  brand_id: number;
  calculators: Record<string, SingleCalculatorStatus>;
}

export function useCalculatorStatus(brandId: number) {
  return useQuery<CalculatorStatusResponse>({
    queryKey: ['calculatorStatus', brandId],
    queryFn: async () => {
      const { data, error } = await client.GET(
        '/api/v1/evaluations/brands/{brand_id}/calculators/status',
        { params: { path: { brand_id: brandId } } },
      );
      if (error) throw error;
      return data as CalculatorStatusResponse;
    },
    enabled: brandId > 0,
  });
}

// ---------------------------------------------------------------------------
// Run-all calculators types and hook
// ---------------------------------------------------------------------------

export interface RunCalculatorItem {
  calculator_type: string;
  status: 'success' | 'skipped' | 'error';
  result?: CalculatorResult;
  reason?: string;
}

export interface RunAllResponse {
  results: RunCalculatorItem[];
}

export function useRunAllCalculators(brandId: number) {
  const queryClient = useQueryClient();

  return useMutation<RunAllResponse>({
    mutationFn: async () => {
      const { data, error } = await client.POST(
        '/api/v1/evaluations/brands/{brand_id}/calculators/run-all',
        { params: { path: { brand_id: brandId } } },
      );
      if (error) throw error;
      return data as RunAllResponse;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calculatorResults', brandId] });
      queryClient.invalidateQueries({ queryKey: ['calculatorStatus', brandId] });
    },
  });
}
