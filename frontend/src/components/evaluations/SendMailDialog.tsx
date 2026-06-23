import { useState, useMemo } from 'react';
import { Mail } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { EmailLanguageSelector } from '../shared/EmailLanguageSelector';
import i18n from '../../i18n';
import type { BrandRawData } from '../../hooks/useEvaluationDetail';
import { buildSubject, buildBody } from './sendMailUtils';
import { useSendPlainEmail } from '../../hooks/useSendPlainEmail';
import { usePreviewEmailText } from '../../hooks/usePreviewEmailText';

interface SendMailDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  evaluationId: number;
  brandName: string;
  period: string;
  emailOutput: string;
  brandRawData: BrandRawData;
}

export function SendMailDialog({
  open,
  onOpenChange,
  evaluationId,
  brandName,
  period,
  emailOutput,
  brandRawData,
}: SendMailDialogProps) {
  const { t } = useTranslation();
  const [to, setTo] = useState('bot@ahacommerce.net');
  const [picEmail, setPicEmail] = useState(brandRawData.email ?? '');
  const [emailLanguage, setEmailLanguage] = useState<string>(i18n.language);
  const sendMutation = useSendPlainEmail();

  const fixedT = useMemo(
    () => i18n.getFixedT(emailLanguage),
    [emailLanguage],
  );

  // The section body is rendered server-side by the unified renderer; fall back
  // to the stored (Indonesian) email output while the preview text loads.
  const { data: previewBody } = usePreviewEmailText(evaluationId, emailLanguage, open);

  const subject = useMemo(
    () => buildSubject(brandName, period, fixedT),
    [brandName, period, fixedT],
  );

  const body = useMemo(
    () =>
      buildBody(
        picEmail,
        brandName,
        brandRawData.pic_name ?? '',
        brandRawData.store_link ?? '',
        brandRawData.kategori ?? '',
        emailOutput,
        fixedT,
        previewBody ?? undefined,
      ),
    [picEmail, brandName, brandRawData, emailOutput, fixedT, previewBody],
  );

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      setTo('bot@ahacommerce.net');
      setPicEmail(brandRawData.email ?? '');
      setEmailLanguage(i18n.language);
    }
    onOpenChange(nextOpen);
  };

  const handleSend = () => {
    sendMutation.mutate(
      { evaluationId, recipients: [to], subject, body, picEmail, language: emailLanguage },
      {
        onSuccess: () => {
          toast.success(t('sendMail.sendSuccess', { defaultValue: 'Email sent.' }));
          onOpenChange(false);
        },
        onError: (err) => {
          toast.error(
            t('sendMail.sendError', {
              defaultValue: 'Failed to send email.',
            }) +
              (err instanceof Error && err.message ? ` (${err.message})` : ''),
          );
        },
      },
    );
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-h-[calc(100dvh-2rem)] overflow-y-auto sm:max-w-5xl">
        <DialogHeader>
          <DialogTitle>{t('sendMail.title')}</DialogTitle>
          <DialogDescription className="sr-only">
            {t('sendMail.description')}
          </DialogDescription>
        </DialogHeader>

        <div className="min-w-0 space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="send-mail-to">{t('sendMail.to')}</Label>
            <Input
              id="send-mail-to"
              type="email"
              value={to}
              onChange={(e) => setTo(e.target.value)}
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="send-mail-pic-email">{t('sendMail.picEmail')}</Label>
            <Input
              id="send-mail-pic-email"
              type="email"
              value={picEmail}
              onChange={(e) => setPicEmail(e.target.value)}
            />
          </div>

          {/* Email Language Selector */}
          <EmailLanguageSelector value={emailLanguage} onChange={setEmailLanguage} />

          <div className="space-y-1.5">
            <Label>{t('sendMail.subject')}</Label>
            <div className="rounded border bg-muted px-3 py-2 text-sm" data-testid="mail-subject">
              {subject}
            </div>
          </div>

          <div className="space-y-1.5">
            <Label>{t('sendMail.body')}</Label>
            <pre
              className="max-h-64 overflow-y-auto whitespace-pre-wrap rounded border bg-muted p-3 text-sm"
              data-testid="mail-body"
            >
              {body}
            </pre>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => handleOpenChange(false)}>
            {t('sendMail.cancel')}
          </Button>
          <Button onClick={handleSend} disabled={sendMutation.isPending}>
            <Mail className="mr-1.5 size-4" />
            {sendMutation.isPending
              ? t('sendMail.sending', { defaultValue: 'Sending…' })
              : t('sendMail.send')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
