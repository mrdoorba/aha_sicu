import { useMutation } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface SendPlainEmailParams {
  evaluationId: number;
  recipients: string[];
  subject: string;
  /**
   * Display body shown in the dialog. Ignored by the backend, which renders the
   * sent body server-side from evaluationId + language; sent for backward
   * compatibility / auditing only.
   */
  body: string;
  /** PIC address(es) for the body's `[EMAIL TO: ...]` line; rendered server-side. */
  picEmail?: string;
  language: string;
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
      picEmail,
      language,
      cc,
      bcc,
    }: SendPlainEmailParams) => {
      const { data, error } = await client.POST('/api/v1/email/send-plain', {
        body: {
          evaluation_id: evaluationId,
          recipients,
          subject,
          body,
          language,
          ...(picEmail ? { pic_email: picEmail } : {}),
          ...(cc && cc.length > 0 ? { cc } : {}),
          ...(bcc && bcc.length > 0 ? { bcc } : {}),
        },
      });
      if (error) throw new Error('Failed to send email');
      return data;
    },
  });
}
