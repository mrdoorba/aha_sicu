import { useMutation } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface SendEmailParams {
  evaluationId: number;
  recipients: string[];
  chartImage: string;
  cc?: string[];
  bcc?: string[];
  note?: string;
  language?: string;
}

export function useSendEmail() {
  return useMutation({
    mutationFn: async ({ evaluationId, recipients, chartImage, cc, bcc, note, language }: SendEmailParams) => {
      const { data, error } = await client.POST('/api/v1/email/send', {
        body: {
          evaluation_id: evaluationId,
          recipients,
          chart_image: chartImage,
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
