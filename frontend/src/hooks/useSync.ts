import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import client from '../services/apiClient';
import type { components } from '../types/api.generated';

export type ColumnChangeDetail = components['schemas']['ColumnChangeDetail'];
export type SyncDetailData = components['schemas']['SyncDetailResponse'];

// Keep in sync with generated OpenAPI schema for /api/v1/sync and /api/v1/sync/status.
export type SyncStatusData = components['schemas']['SyncStatusResponse'];

export function useSyncStatus() {
  return useQuery({
    queryKey: ['syncStatus'],
    queryFn: async () => {
      const { data, error } = await client.GET('/api/v1/sync/status');
      if (error) throw new Error('Failed to fetch sync status');
      return (data as SyncStatusData) ?? null;
    },
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'in_progress' ? 3_000 : 30_000;
    },
  });
}

export function useTriggerSync() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { data, response } = await client.POST('/api/v1/sync');
      if (!response.ok) {
        if (response.status === 409) throw new Error('Sync already in progress');
        throw new Error('Failed to trigger sync');
      }
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['syncStatus'] });
      queryClient.invalidateQueries({ queryKey: ['brands'] });
    },
  });
}
