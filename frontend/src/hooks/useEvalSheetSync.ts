import { useMutation } from '@tanstack/react-query';
import client from '../services/apiClient';

export function useEvalSheetSync() {
  const mutation = useMutation({
    mutationFn: async () => {
      const { data, error } = await client.POST('/api/v1/sync/eval-sheet');
      if (error) throw new Error('Failed to sync eval sheet');
      return data;
    },
  });

  return {
    syncEvalSheet: mutation.mutate,
    isLoading: mutation.isPending,
    data: mutation.data,
    error: mutation.error,
  };
}
