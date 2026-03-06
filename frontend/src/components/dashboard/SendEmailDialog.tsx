import { useState } from 'react';
import { Mail, Loader2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { toPng } from 'html-to-image';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card, CardContent } from '../ui/card';
import { useSendEmail } from '../../hooks/useSendEmail';
import type { BrandRawData } from '../../hooks/useEvaluationDetail';

interface SendEmailDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  evaluationId: number;
  brandName: string;
  period: string;
  score: number;
  brandRawData: BrandRawData;
  chartRef: React.RefObject<HTMLDivElement | null>;
  onSuccess?: () => void;
}

const isValidEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

export function SendEmailDialog({
  open,
  onOpenChange,
  evaluationId,
  brandName,
  period,
  score,
  brandRawData,
  chartRef,
  onSuccess,
}: SendEmailDialogProps) {
  const { t } = useTranslation();
  const { mutate, isPending, isError, reset } = useSendEmail();

  const [recipient, setRecipient] = useState(brandRawData.email ?? '');
  const [captureError, setCaptureError] = useState(false);

  const handleClose = (nextOpen: boolean) => {
    if (!nextOpen) {
      reset();
      setCaptureError(false);
      setRecipient(brandRawData.email ?? '');
    }
    onOpenChange(nextOpen);
  };

  const handleSend = async () => {
    setCaptureError(false);

    let dataUrl: string;
    try {
      dataUrl = await toPng(chartRef.current!, { cacheBust: true, backgroundColor: '#ffffff', pixelRatio: 2 });
    } catch {
      setCaptureError(true);
      return;
    }

    const chartImage = dataUrl.replace(/^data:image\/png;base64,/, '');

    mutate(
      { evaluationId, recipient, chartImage },
      {
        onSuccess: () => {
          toast.success(t('sendEmail.success', { recipient }));
          onOpenChange(false);
          onSuccess?.();
        },
      },
    );
  };

  const sendDisabled = !isValidEmail(recipient) || isPending;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t('sendEmail.title')}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Brand Summary Card */}
          <Card>
            <CardContent className="p-4">
              <p className="font-semibold">{brandName}</p>
              <p className="text-sm text-muted-foreground">{period}</p>
              <p className="text-lg font-bold">{Math.round(score)}</p>
            </CardContent>
          </Card>

          {/* Recipient Input */}
          <div className="space-y-1.5">
            <Label htmlFor="send-email-recipient">{t('sendEmail.recipient')}</Label>
            <Input
              id="send-email-recipient"
              type="email"
              placeholder={t('sendEmail.recipientPlaceholder')}
              value={recipient}
              onChange={(e) => setRecipient(e.target.value)}
              disabled={isPending}
            />
          </div>

          {/* Error Messages */}
          {captureError && (
            <p className="text-sm text-destructive">{t('sendEmail.captureError')}</p>
          )}
          {isError && (
            <p className="text-sm text-destructive">{t('sendEmail.error')}</p>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => handleClose(false)} disabled={isPending}>
            {t('sendEmail.cancel')}
          </Button>
          <Button onClick={handleSend} disabled={sendDisabled}>
            {isPending ? (
              <>
                <Loader2 className="mr-2 size-4 animate-spin" />
                {t('sendEmail.sending')}
              </>
            ) : isError ? (
              t('sendEmail.retry')
            ) : (
              <>
                <Mail className="mr-2 size-4" />
                {t('sendEmail.send')}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
