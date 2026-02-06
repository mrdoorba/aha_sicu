import { useQuery } from '@tanstack/react-query';
import { getCurrentUserToken } from '../firebase/auth';

const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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
  return useQuery<BrandListResponse>({
    queryKey: ['brands', page, limit, search],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: String(page),
        limit: String(limit),
      });
      if (search) params.set('search', search);
      const token = await getCurrentUserToken();
      const res = await fetch(`${baseUrl}/api/v1/brands?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to fetch brands');
      return res.json();
    },
  });
}
