import { useQuery } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface BrandEvaluationItem {
  id: number;
  final_score: number;
  verdict: string;
  template: string;
  evaluator_email: string;
  created_at: string;
}

export interface BrandEvaluationListResponse {
  items: BrandEvaluationItem[];
  total: number;
}

export function useBrandEvaluations(
  brandId: number,
  limit?: number,
  dateFrom?: string,
  dateTo?: string,
  enabled = false,
) {
  const query = useQuery({
    queryKey: ['brand-evaluations', brandId, limit, dateFrom, dateTo],
    queryFn: async () => {
      const { data, error } = await client.GET(
        '/api/v1/evaluations/grouped/{brand_id}',
        {
          params: {
            path: { brand_id: brandId },
            query: {
              ...(limit ? { limit } : {}),
              ...(dateFrom ? { date_from: dateFrom } : {}),
              ...(dateTo ? { date_to: dateTo } : {}),
            },
          },
        },
      );
      if (error) throw new Error('Failed to fetch brand evaluations');
      return data;
    },
    enabled,
  });

  return {
    evaluations: query.data?.items ?? [],
    total: query.data?.total ?? 0,
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch,
  };
}
