import { useQuery } from '@tanstack/react-query';
import client from '../services/apiClient';

// Keep in sync with apiClient.ts paths['/api/v1/brands'] response type
export interface BrandListItem {
  id: number;
  brand_name: string;
  raw_data: Record<string, unknown>;
  updated_at: string;
  meeting_raw_data: Record<string, unknown> | null;
}

export interface BrandListResponse {
  items: BrandListItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export function useBrands(page = 1, limit = 20, search = '') {
  return useQuery({
    queryKey: ['brands', page, limit, search],
    queryFn: async () => {
      const { data, error } = await client.GET('/api/v1/brands', {
        params: {
          query: { page, limit, ...(search ? { search } : {}) },
        },
      });
      if (error) throw new Error('Failed to fetch brands');
      return data as BrandListResponse;
    },
  });
}
