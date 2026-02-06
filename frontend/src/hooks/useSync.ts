import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCurrentUserToken } from '../firebase/auth';

const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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
      const token = await getCurrentUserToken();
      const res = await fetch(`${baseUrl}/api/v1/sync/status`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to fetch sync status');
      return res.json();
    },
    refetchInterval: 10_000,
  });
}

export function useTriggerSync() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const token = await getCurrentUserToken();
      const res = await fetch(`${baseUrl}/api/v1/sync`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.status === 409) throw new Error('Sync already in progress');
      if (!res.ok) throw new Error('Failed to trigger sync');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['syncStatus'] });
      queryClient.invalidateQueries({ queryKey: ['brands'] });
    },
  });
}
