import { useMutation, useQueryClient } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface UpdateRuleParams {
  template: 'fashion' | 'non_fashion';
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
      if (error) throw new Error('Failed to update scoring rules');
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] });
    },
  });
}
