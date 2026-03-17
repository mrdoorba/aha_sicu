import { useMutation, useQueryClient } from '@tanstack/react-query';
import client from '../services/apiClient';
import { isApiErrorWithDetail } from '../lib/typeGuards';

export interface UpdateRuleParams {
  template: 'fashion' | 'non_fashion' | 'default';
  rules: Record<string, unknown>;
  marketplace?: string;
}

export function useUpdateRule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ template, rules, marketplace }: UpdateRuleParams) => {
      const { data, error } = await client.PUT('/api/v1/rules/{template}', {
        params: { path: { template }, query: { marketplace } },
        body: { rules },
      });
      if (error) {
        const err: unknown = error;
        throw new Error(
          isApiErrorWithDetail(err) ? err.detail : 'Failed to update scoring rules',
        );
      }
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] });
    },
  });
}
