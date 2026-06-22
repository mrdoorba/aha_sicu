import { useQuery } from '@tanstack/react-query';
import { getCurrentUserToken } from '../firebase/auth';
import { API_BASE_URL } from '../config';

/**
 * Fetch the plain-text email body rendered server-side by the unified email
 * renderer (`GET /email/preview/{id}?format=text&language=`).
 *
 * The backend is the single source of truth for the email layout; the frontend
 * no longer assembles the body locally. Disabled until a valid evaluation id is
 * available (the body is DB-backed, so it only exists for saved evaluations).
 */
export function usePreviewEmailText(
  evaluationId: number | undefined,
  language: string,
  enabled = true,
) {
  return useQuery({
    queryKey: ['emailPreviewText', evaluationId, language],
    enabled: enabled && !!evaluationId && evaluationId > 0,
    queryFn: async (): Promise<string> => {
      const params = new URLSearchParams();
      params.set('format', 'text');
      params.set('language', language);
      const token = await getCurrentUserToken();
      const res = await fetch(
        `${API_BASE_URL}/api/v1/email/preview/${evaluationId}?${params.toString()}`,
        { headers: token ? { Authorization: `Bearer ${token}` } : {} },
      );
      if (!res.ok) throw new Error('Failed to load email preview');
      return res.text();
    },
  });
}
