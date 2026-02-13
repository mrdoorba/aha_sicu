import { useMutation, useQueryClient } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface UpdateRuleParams {
  template: 'fashion' | 'non_fashion' | 'default';
  rules: Record<string, unknown>;
}

export function useUpdateRule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ template, rules }: UpdateRuleParams) => {
      const { data, error } = await client.PUT('/api/v1/rules/{template}', {
        params: { path: { template } },
        body: { rules },
      });
      if (error) {
        const detail = (error as Record<string, unknown>)?.detail;
        throw new Error(typeof detail === 'string' ? detail : 'Failed to update scoring rules');
      }
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] });
    },
  });
}
