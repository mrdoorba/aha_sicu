import { useState, useMemo } from 'react';
import { Mail } from 'lucide-react';
import { useTranslation } from 'react-i18next';
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
import {
  buildI18nEmailBody,
  type ScoringConclusionData,
} from '../../utils/buildI18nEmailBody';
import i18n from '../../i18n';
import type { CategoryScore } from '../../hooks/useScoring';
import type { BrandRawData } from '../../hooks/useEvaluationDetail';
import {
  buildSubject,
  buildBody,
  buildMailtoUrl,
  openMailto,
} from './sendMailUtils';
import { isRecord } from '../../lib/typeGuards';

interface SendMailDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  brandName: string;
  period: string;
  emailOutput: string;
  brandRawData: BrandRawData;
  scoreBreakdown?: Array<Record<string, unknown>>;
  calculatorResults?: Record<string, unknown>;
}

/**
 * Type guard to check whether calculator_results.scoring_summary has
 * the shape needed for ScoringConclusionData.
 */
function isScoringSummary(value: unknown): value is ScoringConclusionData {
  if (!isRecord(value)) return false;
  return (
    typeof value.conclusion === 'string' ||
    Array.isArray(value.conclusion_i18n) ||
    typeof value.marketing_budget === 'string' ||
    typeof value.closing_message === 'string'
  );
}

export function SendMailDialog({
  open,
  onOpenChange,
  brandName,
  period,
  emailOutput,
  brandRawData,
  scoreBreakdown,
  calculatorResults,
}: SendMailDialogProps) {
  const { t } = useTranslation();
  const [to, setTo] = useState('bot@ahacommerce.net');
  const [picEmail, setPicEmail] = useState(brandRawData.email ?? '');
  const [emailLanguage, setEmailLanguage] = useState<string>(i18n.language);

  // Determine whether we have i18n-capable score data
  const hasI18nData = useMemo(() => {
    if (!scoreBreakdown || scoreBreakdown.length === 0) return false;
    // Check if any row in any category has message_i18n
    return scoreBreakdown.some((cat) => {
      const rows = cat.rows;
      if (!Array.isArray(rows)) return false;
      return rows.some(
        (r: Record<string, unknown>) =>
          r.message_i18n != null && typeof r.message_i18n === 'object',
      );
    });
  }, [scoreBreakdown]);

  // Build i18n email body when score breakdown with i18n data is available
  const i18nBody = useMemo(() => {
    if (!hasI18nData || !scoreBreakdown) return null;
    const fixedT = i18n.getFixedT(emailLanguage);
    const castScores = scoreBreakdown as unknown as CategoryScore[];

    let scoringSummary: ScoringConclusionData | null = null;
    if (calculatorResults && isRecord(calculatorResults.scoring_summary)) {
      const raw = calculatorResults.scoring_summary;
      if (isScoringSummary(raw)) {
        scoringSummary = raw;
      }
    }

    return buildI18nEmailBody(castScores, scoringSummary, fixedT, calculatorResults);
  }, [hasI18nData, scoreBreakdown, calculatorResults, emailLanguage]);

  const fixedT = useMemo(() => {
    if (!hasI18nData) return undefined;
    return i18n.getFixedT(emailLanguage);
  }, [hasI18nData, emailLanguage]);

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
        i18nBody ?? undefined,
      ),
    [picEmail, brandName, brandRawData, emailOutput, fixedT, i18nBody],
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
    const mailtoUrl = buildMailtoUrl(to, subject, body);
    openMailto(mailtoUrl);
    onOpenChange(false);
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
          <Button onClick={handleSend}>
            <Mail className="mr-1.5 size-4" />
            {t('sendMail.send')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
