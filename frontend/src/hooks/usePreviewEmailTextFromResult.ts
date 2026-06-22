import { useQuery } from '@tanstack/react-query';
import client from '../services/apiClient';
import type { ScoringResult } from './useScoring';
import type { components } from '../types/api.generated';

type PreviewEmailRequest = components['schemas']['PreviewEmailRequest'];

/**
 * Render the plain-text email body for an in-memory, not-yet-saved scoring
 * result by POSTing it to `/email/preview?format=text&language=`.
 *
 * The pre-save scoring screen has no saved evaluation id to hit the GET preview
 * endpoint, so it posts the just-computed result. Reuses the single backend
 * `render_email`; no client-side assembly. Disabled until a result exists.
 */
export function usePreviewEmailTextFromResult(
  scoringResult: ScoringResult | null | undefined,
  language: string,
  calculatorResults?: Record<string, unknown>,
) {
  return useQuery({
    queryKey: ['emailPreviewFromResult', scoringResult, language],
    enabled: !!scoringResult,
    queryFn: async (): Promise<string> => {
      const r = scoringResult!;
      const requestBody: PreviewEmailRequest = {
        category_scores: r.category_scores as unknown as PreviewEmailRequest['category_scores'],
        conclusion: r.conclusion,
        conclusion_i18n:
          r.conclusion_i18n as unknown as PreviewEmailRequest['conclusion_i18n'],
        marketing_estimation: r.marketing_estimation,
        marketing_budget: r.marketing_budget,
        marketing_budget_i18n:
          r.marketing_budget_i18n as unknown as PreviewEmailRequest['marketing_budget_i18n'],
        closing_message: r.closing_message,
        closing_message_i18n:
          r.closing_message_i18n as unknown as PreviewEmailRequest['closing_message_i18n'],
        calculator_results: calculatorResults ?? {},
        // brand_name/period only affect the HTML chrome, not the text body.
        brand_name: '',
        period: '',
      };
      const { data, error } = await client.POST('/api/v1/email/preview', {
        params: { query: { language, format: 'text' } },
        body: requestBody,
        parseAs: 'text',
      });
      if (error) throw new Error('Failed to render email preview');
      return data as string;
    },
  });
}
