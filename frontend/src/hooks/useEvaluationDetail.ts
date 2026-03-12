import { useQuery } from '@tanstack/react-query';
import client from '../services/apiClient';
import { isApiErrorWithCode } from '../lib/typeGuards';

export interface BrandRawData {
  email: string | null;
  pic_name: string | null;
  store_link: string | null;
  kategori: string | null;
}

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
  period: string;
  brand_raw_data: BrandRawData;
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
        if (isApiErrorWithCode(error)) {
          throw new ApiError(error.detail, error.code);
        }
        throw new ApiError('Failed to fetch evaluation detail');
      }
      return data as EvaluationDetail;
    },
    enabled: id > 0,
  });

  const isNotFound =
    query.isError &&
    query.error instanceof ApiError &&
    query.error.code === 'EVAL_NOT_FOUND';

  return {
    evaluation: query.data ?? null,
    isLoading: query.isLoading,
    isError: query.isError,
    isNotFound,
    error: query.error,
    refetch: query.refetch,
  };
}
