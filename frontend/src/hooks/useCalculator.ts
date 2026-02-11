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

export interface CalculatorResult {
  calculator_type: string;
  output_text: string;
  details: AdsKeywordDetails;
  calculated_at: string;
}

export function useRunCalculator(brandId: number, calculatorType: 'ads_keyword') {
  const queryClient = useQueryClient();

  return useMutation<CalculatorResult>({
    mutationFn: async () => {
      const { data, error } = await client.POST(
        '/api/v1/evaluations/brands/{brand_id}/calculators/ads_keyword',
        { params: { path: { brand_id: brandId } } },
      );
      if (error) throw error;
      return data as CalculatorResult;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calculatorResults', brandId] });
    },
  });
}
