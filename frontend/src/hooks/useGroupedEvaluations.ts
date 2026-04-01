import { useQuery, keepPreviousData } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface GroupedEvaluationItem {
  brand_id: number;
  brand_name: string;
  marketplace: 'ID' | 'TH';
  evaluation_count: number;
  top_score: number;
  top_verdict: string;
  latest_date: string;
}

export interface GroupedEvaluationListResponse {
  items: GroupedEvaluationItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export function useGroupedEvaluations(
  page = 1,
  limit = 20,
  search?: string,
  dateFrom?: string,
  dateTo?: string,
) {
  const query = useQuery({
    queryKey: ['evaluations-grouped', page, limit, search, dateFrom, dateTo],
    queryFn: async () => {
      const { data, error } = await client.GET('/api/v1/evaluations/grouped', {
        params: {
          query: {
            page,
            limit,
            ...(search ? { search } : {}),
            ...(dateFrom ? { date_from: dateFrom } : {}),
            ...(dateTo ? { date_to: dateTo } : {}),
          },
        },
      });
      if (error) throw new Error('Failed to fetch grouped evaluations');
      return data;
    },
    placeholderData: keepPreviousData,
  });

  return {
    brands: query.data?.items ?? [],
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
