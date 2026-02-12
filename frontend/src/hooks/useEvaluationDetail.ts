import { useQuery } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface EvaluationDetail {
  id: number;
  brand_id: number;
  brand_name: string;
  final_score: number;
  verdict: string;
  template: string;
  score_breakdown: Array<Record<string, unknown>>;
  calculator_results: Record<string, unknown>;
  manual_inputs: Record<string, unknown>;
  email_output: string | null;
  evaluator_email: string;
  created_at: string;
  rule_version: number;
}

class ApiError extends Error {
  code?: string;
  constructor(message: string, code?: string) {
    super(message);
    this.code = code;
  }
}

export function useEvaluationDetail(id: number) {
  const query = useQuery<EvaluationDetail>({
    queryKey: ['evaluation-detail', id],
    queryFn: async () => {
      const { data, error } = await client.GET(
        '/api/v1/evaluations/{evaluation_id}',
        {
          params: { path: { evaluation_id: id } },
        },
      );
      if (error) {
        const apiError = error as Record<string, unknown>;
        throw new ApiError(
          typeof apiError.detail === 'string'
            ? apiError.detail
            : 'Failed to fetch evaluation detail',
          typeof apiError.code === 'string' ? apiError.code : undefined,
        );
      }
      return data as EvaluationDetail;
    },
    enabled: id > 0,
  });

  const isNotFound =
    query.isError && (query.error as ApiError)?.code === 'EVAL_NOT_FOUND';

  return {
    evaluation: query.data ?? null,
    isLoading: query.isLoading,
    isError: query.isError,
    isNotFound,
    error: query.error,
    refetch: query.refetch,
  };
}
