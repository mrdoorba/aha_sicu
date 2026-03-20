import { useQuery, keepPreviousData } from '@tanstack/react-query';
import client from '../services/apiClient';

export function useEmailHistory(
  page = 1,
  limit = 20,
  search?: string,
  dateFrom?: string,
  dateTo?: string,
  status?: string,
) {
  const query = useQuery({
    queryKey: ['email-history', page, limit, search, dateFrom, dateTo, status],
    queryFn: async () => {
      const { data, error } = await client.GET('/api/v1/email/history', {
        params: {
          query: {
            page,
            limit,
            ...(search ? { search } : {}),
            ...(dateFrom ? { date_from: dateFrom } : {}),
            ...(dateTo ? { date_to: dateTo } : {}),
            ...(status ? { status } : {}),
          },
        },
      });
      if (error) throw new Error('Failed to fetch email history');
      return data;
    },
    placeholderData: keepPreviousData,
  });

  return {
    items: query.data?.items ?? [],
    total: query.data?.total ?? 0,
    page: query.data?.page ?? page,
    pages: query.data?.pages ?? 0,
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch,
    isPlaceholderData: query.isPlaceholderData,
  };
}
