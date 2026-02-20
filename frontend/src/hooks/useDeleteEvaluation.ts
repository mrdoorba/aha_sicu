import { useMutation, useQueryClient } from '@tanstack/react-query';
import client from '../services/apiClient';

export function useDeleteEvaluation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (evaluationId: number) => {
      const { error } = await client.DELETE(
        '/api/v1/evaluations/{evaluation_id}',
        {
          params: {
            path: { evaluation_id: evaluationId },
          },
        },
      );
      if (error) throw new Error('Failed to delete evaluation');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evaluations-grouped'] });
      queryClient.invalidateQueries({ queryKey: ['brand-evaluations'] });
      queryClient.invalidateQueries({ queryKey: ['evaluations'] });
    },
  });
}
