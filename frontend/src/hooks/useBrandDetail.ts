import { useQuery } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface BrandDetail {
  id: number;
  brand_name: string;
  raw_data: Record<string, unknown>;
  updated_at: string;
  meeting_raw_data: Record<string, unknown> | null;
}

export function useBrandDetail(brandId: number) {
  return useQuery({
    queryKey: ['brand', brandId],
    queryFn: async () => {
      const { data, error } = await client.GET('/api/v1/brands/{brand_id}', {
        params: { path: { brand_id: brandId } },
      });
      if (error) throw new Error('Failed to fetch brand detail');
      return data as BrandDetail;
    },
    enabled: brandId > 0,
  });
}
