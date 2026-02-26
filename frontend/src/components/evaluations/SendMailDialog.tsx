import { useState, useMemo } from 'react';
import { Mail } from 'lucide-react';
import { useTranslation } from 'react-i18next';
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
import type { BrandRawData } from '../../hooks/useEvaluationDetail';
import { buildSubject, buildBody } from './sendMailUtils';

interface SendMailDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  brandName: string;
  createdAt: string;
  emailOutput: string;
  brandRawData: BrandRawData;
}

export function SendMailDialog({
  open,
  onOpenChange,
  brandName,
  createdAt,
  emailOutput,
  brandRawData,
}: SendMailDialogProps) {
  const { t } = useTranslation();
  const [to, setTo] = useState('bot@ahacommerce.net');
  const [picEmail, setPicEmail] = useState(brandRawData.email ?? '');

  const subject = useMemo(() => buildSubject(brandName, createdAt), [brandName, createdAt]);

  const body = useMemo(
    () =>
      buildBody(
        picEmail,
        brandName,
        brandRawData.pic_name ?? '',
        brandRawData.store_link ?? '',
        brandRawData.kategori ?? '',
        emailOutput,
      ),
    [picEmail, brandName, brandRawData, emailOutput],
  );

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      setTo('bot@ahacommerce.net');
      setPicEmail(brandRawData.email ?? '');
    }
    onOpenChange(nextOpen);
  };

  const handleSend = () => {
    const mailtoUrl = `mailto:${encodeURIComponent(to)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    const opened = window.open(mailtoUrl, '_blank');
    if (!opened) {
      window.location.href = mailtoUrl;
    }
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-5xl">
        <DialogHeader>
          <DialogTitle>{t('sendMail.title')}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
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
          <Button onClick={handleSend}>
            <Mail className="mr-1.5 size-4" />
            {t('sendMail.send')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

