import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import client from '../services/apiClient';

export type CategoryType = 'fashion' | 'non_fashion';

export interface EvaluationState {
  brand_id: number;
  category_type: CategoryType | null;
  manual_data: Record<string, unknown> | null;
  updated_at: string | null;
}

export interface EvaluationInputsUpdate {
  category_type?: CategoryType | null;
  manual_data?: Record<string, unknown> | null;
}

export function useEvaluationState(brandId: number) {
  return useQuery({
    queryKey: ['evaluation', brandId],
    queryFn: async () => {
      const { data, error } = await client.GET(
        '/api/v1/evaluations/brands/{brand_id}',
        { params: { path: { brand_id: brandId } } },
      );
      if (error) throw new Error('Failed to fetch evaluation state');
      return data;
    },
    enabled: brandId > 0,
  });
}

export function useSaveEvaluationInputs(brandId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: EvaluationInputsUpdate) => {
      const { data, error } = await client.PUT(
        '/api/v1/evaluations/brands/{brand_id}',
        {
          params: { path: { brand_id: brandId } },
          body,
        },
      );
      if (error) throw new Error('Failed to save evaluation inputs');
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evaluation', brandId] });
    },
  });
}
