import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useCallback, useEffect } from 'react';
import client from '../services/apiClient';

export interface RowScore {
  row: number;
  metric: string;
  value: unknown;
  benchmark: string;
  verdict: string;
  message: string;
  score: number;
}

export interface CategoryScore {
  category: string;
  score: number;
  max_score: number;
  rows: RowScore[];
  available: boolean;
}

export interface ScoringResult {
  total_score: number;
  category_scores: CategoryScore[];
  verdict: string;
  conclusion: string;
  marketing_estimation: string;
  marketing_percentage: string;
  marketing_budget: string;
  closing_message: string;
  email_subject: string;
  email_body: string;
  whatsapp_link: string;
  template: string;
  rule_version: number;
}

interface ScoringRequest {
  template: 'fashion' | 'non_fashion';
  verdict: string;
  store_name: string;
  period: string;
  brand_name: string;
  email?: string | null;
}

export function useScoring(brandId: number) {
  const queryClient = useQueryClient();
  const [scoringResult, setScoringResult] = useState<ScoringResult | null>(null);
  const [isStale, setIsStale] = useState(false);

  const mutation = useMutation<ScoringResult, Error, ScoringRequest>({
    mutationFn: async (request) => {
      const { data, error } = await client.POST(
        '/api/v1/evaluations/brands/{brand_id}/score',
        {
          params: { path: { brand_id: brandId } },
          body: request,
        },
      );
      if (error) throw error;
      return data as ScoringResult;
    },
    onSuccess: (data) => {
      setScoringResult(data);
      setIsStale(false);
      queryClient.setQueryData(['scoring', brandId], data);
    },
  });

  const markStale = useCallback(() => {
    if (scoringResult) {
      setIsStale(true);
    }
  }, [scoringResult]);

  // Mark stale when manual data or calculator results change
  useEffect(() => {
    const unsub = queryClient.getQueryCache().subscribe((event) => {
      if (
        event.type === 'updated' &&
        scoringResult &&
        (event.query.queryKey[0] === 'evaluationState' ||
          event.query.queryKey[0] === 'calculatorResults')
      ) {
        setIsStale(true);
      }
    });
    return () => unsub();
  }, [queryClient, scoringResult]);

  return {
    generateScore: mutation.mutate,
    scoringResult,
    isStale,
    markStale,
    isGenerating: mutation.isPending,
    error: mutation.error,
  };
}
