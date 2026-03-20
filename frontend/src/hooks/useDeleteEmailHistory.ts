import { useMutation, useQueryClient } from '@tanstack/react-query';
import { getCurrentUserToken } from '../firebase/auth';
import { API_BASE_URL } from '../config';

export function useDeleteEmailHistory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (ids: number[]) => {
      const token = await getCurrentUserToken();
      const res = await fetch(`${API_BASE_URL}/api/v1/email/history`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ ids }),
      });
      if (!res.ok) throw new Error('Failed to delete email history');
      return res.json() as Promise<{ deleted: number }>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['email-history'] });
    },
  });
}
