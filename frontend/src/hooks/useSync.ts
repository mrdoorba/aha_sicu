import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import client from '../services/apiClient';

// Keep in sync with apiClient.ts paths['/api/v1/sync/status'] response type
export interface SyncStatusData {
  id: number;
  last_sync: string;
  status: 'success' | 'failed' | 'in_progress';
  started_at: string;
  completed_at: string | null;
  brands_synced: number;
  error_message: string | null;
  sync_details: Record<string, {
    rows_synced: number;
    rows_skipped: number;
    status: string;
  }> | null;
}

export function useSyncStatus() {
  return useQuery<SyncStatusData | null>({
    queryKey: ['syncStatus'],
    queryFn: async () => {
      const { data, error } = await client.GET('/api/v1/sync/status');
      if (error) throw new Error('Failed to fetch sync status');
      return (data as SyncStatusData) ?? null;
    },
    refetchInterval: 10_000,
  });
}

export function useTriggerSync() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { data, error, response } = await client.POST('/api/v1/sync');
      if (error) {
        if (response.status === 409) throw new Error('Sync already in progress');
        throw new Error('Failed to trigger sync');
      }
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['syncStatus'] });
    },
  });
}
