import { useState, useCallback, useEffect, useRef } from 'react';
import { Mail, Loader2, ChevronDown, RefreshCw } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { EmailLanguageSelector } from '../shared/EmailLanguageSelector';
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
import { Label } from '../ui/label';
import { Card, CardContent } from '../ui/card';
import { useSendEmail } from '../../hooks/useSendEmail';
import { EmailChipInput } from './EmailChipInput';
import { getCurrentUserToken } from '../../firebase/auth';
import { API_BASE_URL } from '../../config';
import type { BrandRawData } from '../../hooks/useEvaluationDetail';
import i18nInstance from '../../i18n';

function buildDefaultNote(
  brandName: string,
  brandRawData: BrandRawData,
  language: string,
): string {
  const fixedT = i18nInstance.getFixedT(language);
  const salutation = fixedT('sendMailUtils.salutation', {
    brandName,
    picName: brandRawData.pic_name ?? '',
  });
  // Append the category clause only when present, else "dengan kategori" dangles.
  const kategori = brandRawData.kategori ?? '';
  const intro =
    fixedT('sendMailUtils.intro', { brandName, storeLink: brandRawData.store_link ?? '' }) +
    (kategori ? fixedT('sendMailUtils.introCategory', { kategori }) : '');
  return `${salutation}\n\n${intro}`;
}

interface SendEmailDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  evaluationId: number;
  brandName: string;
  period: string;
  score: number;
  brandRawData: BrandRawData;
  /** Brand marketplace ('ID' | 'TH'); picks the default email language. */
  marketplace?: string;
  onSuccess?: () => void;
}

export function SendEmailDialog({
  open,
  onOpenChange,
  evaluationId,
  brandName,
  period,
  score,
  brandRawData,
  marketplace,
  onSuccess,
}: SendEmailDialogProps) {
  const { t, i18n } = useTranslation();
  const { mutate, isPending, isError, reset } = useSendEmail();

  // Default the email to the brand's country: TH brand → 'th', ID → 'id',
  // falling back to the dashboard UI language when the marketplace is unknown.
  const defaultLanguage =
    marketplace === 'TH' ? 'th' : marketplace === 'ID' ? 'id' : i18n.language;

  const initialRecipients = [brandRawData.email].filter(Boolean) as string[];
  const [emailLanguage, setEmailLanguage] = useState(defaultLanguage);

  const DEFAULT_CC: Record<string, string[]> = {
    id: ['tbd@ahacommerce.net', 'main@ahacommerce.net'],
    th: ['th.bd@ahacommerce.net', 'th@ahacommerce.net'],
  };
  const initialCc = DEFAULT_CC[defaultLanguage] ?? DEFAULT_CC['id'] ?? [];
  // BCC the ops mailbox on every language.
  const initialBcc = ['stp@ahacommerce.net'];

  const [recipients, setRecipients] = useState<string[]>(initialRecipients);
  const [cc, setCc] = useState<string[]>(initialCc);
  const [bcc, setBcc] = useState<string[]>(initialBcc);
  const [showCc, setShowCc] = useState(initialCc.length > 0);
  const [showBcc, setShowBcc] = useState(initialBcc.length > 0);
  const [note, setNote] = useState(() => buildDefaultNote(brandName, brandRawData, defaultLanguage));
  const [showPreview, setShowPreview] = useState(false);
  const [previewHtml, setPreviewHtml] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const previousEmailLanguage = useRef(emailLanguage);

  const totalRecipients = recipients.length + cc.length + bcc.length;
  const sendDisabled = recipients.length === 0 || isPending;

  const fetchPreview = useCallback(async () => {
    setPreviewLoading(true);
    try {
      const params = new URLSearchParams();
      if (note) params.set('note', note);
      params.set('language', emailLanguage);
      const qs = params.toString();
      const token = await getCurrentUserToken();
      const res = await fetch(
        `${API_BASE_URL}/api/v1/email/preview/${evaluationId}${qs ? `?${qs}` : ''}`,
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        },
      );
      const html = await res.text();
      setPreviewHtml(html);
    } catch {
      setPreviewHtml(null);
    } finally {
      setPreviewLoading(false);
    }
  }, [evaluationId, note, emailLanguage]);

  const togglePreview = () => {
    const next = !showPreview;
    setShowPreview(next);
    if (next && previewHtml === null) {
      fetchPreview();
    }
  };

  const handleRefreshPreview = () => {
    setPreviewHtml(null);
    fetchPreview();
  };

  useEffect(() => {
    if (previousEmailLanguage.current === emailLanguage) return;
    previousEmailLanguage.current = emailLanguage;

    setPreviewHtml(null);
    if (showPreview) {
      fetchPreview();
    }
  }, [emailLanguage, fetchPreview, showPreview]);

  const handleClose = (nextOpen: boolean) => {
    if (!nextOpen) {
      reset();
      setRecipients(initialRecipients);
      setCc(initialCc);
      setBcc(initialBcc);
      setShowCc(initialCc.length > 0);
      setShowBcc(initialBcc.length > 0);
      setNote(buildDefaultNote(brandName, brandRawData, defaultLanguage));
      setEmailLanguage(defaultLanguage);
      setShowPreview(false);
      setPreviewHtml(null);
    }
    onOpenChange(nextOpen);
  };

  const handleSend = () => {
    mutate(
      {
        evaluationId,
        recipients,
        cc: cc.length > 0 ? cc : undefined,
        bcc: bcc.length > 0 ? bcc : undefined,
        note: note || undefined,
        language: emailLanguage,
      },
      {
        onSuccess: () => {
          toast.success(t('sendEmail.success', { count: recipients.length }));
          onOpenChange(false);
          onSuccess?.();
        },
      },
    );
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>{t('sendEmail.title')}</DialogTitle>
          <DialogDescription className="sr-only">
            {t('sendEmail.description')}
          </DialogDescription>
        </DialogHeader>

        <div className="max-h-[65vh] overflow-y-auto space-y-4 pr-1">
          {/* Recipient Section */}
          <div className="space-y-3">
            {/* To Field */}
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <Label htmlFor="send-email-to">{t('sendEmail.recipient')}</Label>
                {!showCc && (
                  <button
                    type="button"
                    className="text-xs text-muted-foreground hover:text-foreground"
                    onClick={() => setShowCc(true)}
                  >
                    CC
                  </button>
                )}
                {!showBcc && (
                  <button
                    type="button"
                    className="text-xs text-muted-foreground hover:text-foreground"
                    onClick={() => setShowBcc(true)}
                  >
                    BCC
                  </button>
                )}
              </div>
              <EmailChipInput
                id="send-email-to"
                emails={recipients}
                onChange={setRecipients}
                disabled={isPending}
                placeholder={t('sendEmail.recipientPlaceholder')}
                maxTotal={10}
                currentTotal={totalRecipients}
              />
            </div>

            {/* CC Field */}
            {showCc && (
              <div className="space-y-1.5">
                <Label htmlFor="send-email-cc">{t('sendEmail.cc')}</Label>
                <EmailChipInput
                  id="send-email-cc"
                  emails={cc}
                  onChange={setCc}
                  disabled={isPending}
                  placeholder="CC"
                  maxTotal={10}
                  currentTotal={totalRecipients}
                />
              </div>
            )}

            {/* BCC Field */}
            {showBcc && (
              <div className="space-y-1.5">
                <Label htmlFor="send-email-bcc">{t('sendEmail.bcc')}</Label>
                <EmailChipInput
                  id="send-email-bcc"
                  emails={bcc}
                  onChange={setBcc}
                  disabled={isPending}
                  placeholder="BCC"
                  maxTotal={10}
                  currentTotal={totalRecipients}
                />
              </div>
            )}
          </div>

          {/* Email Language Selector */}
          <EmailLanguageSelector value={emailLanguage} onChange={(lang) => {
            setEmailLanguage(lang);
            const newCc = DEFAULT_CC[lang] ?? DEFAULT_CC['id'] ?? [];
            setCc(newCc);
            setShowCc(newCc.length > 0);
            setNote(buildDefaultNote(brandName, brandRawData, lang));
          }} />

          {/* Note Section */}
          <div className="space-y-1.5">
            <Label htmlFor="send-email-note">{t('sendEmail.noteLabel')}</Label>
            <textarea
              id="send-email-note"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              maxLength={500}
              disabled={isPending}
              placeholder={t('sendEmail.notePlaceholder')}
              rows={3}
              className="w-full rounded-md border bg-transparent px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <p className="text-xs text-muted-foreground text-right">{note.length}/500</p>
          </div>

          {/* Brand Summary Card */}
          <Card>
            <CardContent className="p-4">
              <p className="font-semibold">{brandName}</p>
              <p className="text-sm text-muted-foreground">{period}</p>
              <p className="text-lg font-bold">{Math.round(score)}</p>
            </CardContent>
          </Card>

          {/* Preview Section */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={togglePreview}
                className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
              >
                <ChevronDown
                  className={`size-4 transition-transform ${showPreview ? 'rotate-180' : ''}`}
                />
                {t('sendEmail.previewToggle')}
              </button>
              {showPreview && (
                <button
                  type="button"
                  onClick={handleRefreshPreview}
                  className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                >
                  <RefreshCw className="size-3" />
                  {t('sendEmail.previewRefresh')}
                </button>
              )}
            </div>

            {showPreview && (
              <div>
                {previewLoading ? (
                  <div className="flex items-center justify-center h-[300px] border rounded">
                    <Loader2 className="size-6 animate-spin text-muted-foreground" />
                    <span className="ml-2 text-sm text-muted-foreground">
                      {t('sendEmail.previewLoading')}
                    </span>
                  </div>
                ) : previewHtml ? (
                  <iframe
                    srcDoc={previewHtml}
                    className="w-full h-[300px] border rounded"
                    sandbox="allow-same-origin"
                    title="Email Preview"
                  />
                ) : null}
              </div>
            )}
          </div>

          {/* Error Messages */}
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
