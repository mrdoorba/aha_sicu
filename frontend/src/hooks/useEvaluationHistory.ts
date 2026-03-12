import { useQuery, keepPreviousData } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface EvaluationListItem {
  id: number;
  brand_name: string;
  final_score: number;
  verdict: string;
  template: string;
  evaluator_email: string;
  created_at: string;
}

export interface EvaluationListResponse {
  items: EvaluationListItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export type SortBy = 'created_at' | 'final_score';
export type SortOrder = 'asc' | 'desc';

export function useEvaluationHistory(
  page = 1,
  limit = 20,
  sortBy: SortBy = 'created_at',
  sortOrder: SortOrder = 'desc',
  search?: string,
  dateFrom?: string,
  dateTo?: string,
) {
  const query = useQuery({
    queryKey: ['evaluations', page, limit, sortBy, sortOrder, search, dateFrom, dateTo],
    queryFn: async () => {
      const { data, error } = await client.GET('/api/v1/evaluations', {
        params: {
          query: {
            page,
            limit,
            sort_by: sortBy,
            sort_order: sortOrder,
            ...(search ? { search } : {}),
            ...(dateFrom ? { date_from: dateFrom } : {}),
            ...(dateTo ? { date_to: dateTo } : {}),
          },
        },
      });
      if (error) throw new Error('Failed to fetch evaluation history');
      return data;
    },
    placeholderData: keepPreviousData,
    refetchInterval: 30_000,
  });

  return {
    evaluations: query.data?.items ?? [],
    total: query.data?.total ?? 0,
    page: query.data?.page ?? page,
    pages: query.data?.pages ?? 0,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
    isPlaceholderData: query.isPlaceholderData,
  };
}
