import { useQuery } from '@tanstack/react-query';
import client from '../services/apiClient';

/** A brand's VP score read against the bar its package sets. */
export interface PackageFit {
  package: string | null;
  vp: number | null;
  bar: number | null;
  /** 0, or -10 when VP falls short of the bar. */
  adjustment: number;
  /** null when there was nothing to judge. */
  met: boolean | null;
}

export interface BrandDetail {
  id: number;
  brand_name: string;
  raw_data: Record<string, unknown>;
  updated_at: string;
  marketplace: string;
  meeting_raw_data: Record<string, unknown> | null;
  package_fit: PackageFit;
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
