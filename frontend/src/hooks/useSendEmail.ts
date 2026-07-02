import { useMutation } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface SendEmailParams {
  evaluationId: number;
  recipients: string[];
  cc?: string[];
  bcc?: string[];
  note?: string;
  language?: string;
}

export function useSendEmail() {
  return useMutation({
    mutationFn: async ({ evaluationId, recipients, cc, bcc, note, language }: SendEmailParams) => {
      const { data, error } = await client.POST('/api/v1/email/send', {
        body: {
          evaluation_id: evaluationId,
          recipients,
          ...(cc && cc.length > 0 ? { cc } : {}),
          ...(bcc && bcc.length > 0 ? { bcc } : {}),
          ...(note ? { note } : {}),
          ...(language ? { language } : {}),
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } as any,
      });
      if (error) throw new Error('Failed to send email');
      return data;
    },
  });
}
