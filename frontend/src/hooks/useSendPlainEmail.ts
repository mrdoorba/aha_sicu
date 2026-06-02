import { useMutation } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface SendPlainEmailParams {
  evaluationId: number;
  recipients: string[];
  subject: string;
  body: string;
  cc?: string[];
  bcc?: string[];
}

export function useSendPlainEmail() {
  return useMutation({
    mutationFn: async ({
      evaluationId,
      recipients,
      subject,
      body,
      cc,
      bcc,
    }: SendPlainEmailParams) => {
      const { data, error } = await client.POST('/api/v1/email/send-plain', {
        body: {
          evaluation_id: evaluationId,
          recipients,
          subject,
          body,
          ...(cc && cc.length > 0 ? { cc } : {}),
          ...(bcc && bcc.length > 0 ? { bcc } : {}),
        },
      });
      if (error) throw new Error('Failed to send email');
      return data;
    },
  });
}
