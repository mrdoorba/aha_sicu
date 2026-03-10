import { useQuery } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface FeatureFlags {
  email_enabled: boolean;
}

export function useFeatureFlags() {
  return useQuery<FeatureFlags>({
    queryKey: ['featureFlags'],
    queryFn: async () => {
      const { data, error } = await client.GET('/api/v1/config/features');
      if (error) throw new Error('Failed to fetch feature flags');
      return data as FeatureFlags;
    },
    staleTime: Infinity,
  });
}
