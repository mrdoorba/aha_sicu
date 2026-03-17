import { useMutation } from '@tanstack/react-query';
import { useCallback, useState } from 'react';
import client from '../services/apiClient';

export interface SaveEvaluationRequest {
  template: 'fashion' | 'non_fashion';
  final_score: number;
  verdict: string;
  score_breakdown: Array<Record<string, unknown>>;
  calculator_results: Record<string, unknown>;
  manual_inputs: Record<string, unknown>;
  rule_version?: number;
  email_output?: string | null;
  marketplace?: string;
  period?: string;
}

export interface SaveEvaluationResponse {
  id: number;
  brand_id: number;
  final_score: number;
  verdict: string;
  template: string;
  created_at: string;
}

export function useSaveEvaluation(brandId: number) {
  const [isSaved, setIsSaved] = useState(false);

  const mutation = useMutation<SaveEvaluationResponse, Error, SaveEvaluationRequest>({
    mutationFn: async (request) => {
      const { data, error } = await client.POST(
        '/api/v1/evaluations/brands/{brand_id}/save',
        {
          params: { path: { brand_id: brandId } },
          body: request,
        },
      );
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      setIsSaved(true);
    },
  });

  const resetMutation = mutation.reset;
  const reset = useCallback(() => {
    setIsSaved(false);
    resetMutation();
  }, [resetMutation]);

  return {
    saveEvaluation: mutation.mutate,
    isSaving: mutation.isPending,
    isSaved,
    error: mutation.error,
    reset,
  };
}
