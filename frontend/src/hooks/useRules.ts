import { useQuery } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface RuleThreshold {
  threshold?: number;
  threshold_pct?: number;
  points?: number;
  opportunity_points?: number;
  comparison?: string;
  info_only?: boolean;
  min?: number;
  max?: number;
  points_no_flag?: number;
  points_flag?: number;
  mall?: number;
  star_plus?: number;
  star?: number;
  regular?: number;
  value?: number;
  // Message templates (Story 5.5)
  message_pass?: string;
  message_fail?: string;
  message_fail_severe?: string;
  message_no_ads?: string;
  message_too_minimal?: string;
  message_no_data?: string;
  // Promo individual messages (nested object)
  message_zero?: string;
  message_dependent?: string;
  message_pass_afiliasi?: string;
}

export interface InterpretationRange {
  min: number | null;
  max: number | null;
  label: string;
  verdict: string;
}

export interface ScoringRules {
  operational: Record<string, RuleThreshold>;
  business: Record<string, RuleThreshold>;
  content: Record<string, RuleThreshold>;
  visitors: Record<string, RuleThreshold>;
  promo_tools: Record<string, RuleThreshold>;
  products_status: Record<string, RuleThreshold>;
  ads: Record<string, RuleThreshold>;
  campaign: Record<string, RuleThreshold>;
  stock: Record<string, RuleThreshold>;
  discount: Record<string, RuleThreshold>;
  marketing: Record<string, RuleThreshold>;
  competition?: { message_pass?: string; message_fail?: string };
  interpretation: {
    ranges: InterpretationRange[];
    closing_messages?: Record<string, string>;
  };
}

export interface ScoringRule {
  id: number;
  template: string;
  rules: ScoringRules;
  version: number;
  updated_by: number | null;
  updated_at: string;
}

export function useRules() {
  const query = useQuery<ScoringRule[]>({
    queryKey: ['rules'],
    queryFn: async () => {
      const { data, error } = await client.GET('/api/v1/rules');
      if (error) throw new Error('Failed to fetch scoring rules');
      return data as ScoringRule[];
    },
  });

  return {
    rules: query.data ?? [],
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}
