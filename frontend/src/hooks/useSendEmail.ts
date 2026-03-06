import { useMutation } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface SendEmailParams {
  evaluationId: number;
  recipient: string;
  chartImage: string;
}

export function useSendEmail() {
  return useMutation({
    mutationFn: async ({ evaluationId, recipient, chartImage }: SendEmailParams) => {
      const { data, error } = await client.POST('/api/v1/email/send', {
        body: {
          evaluation_id: evaluationId,
          recipient,
          chart_image: chartImage,
        },
      });
      if (error) throw new Error('Failed to send email');
      return data;
    },
  });
}
