import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '../../ui/button';
import { Card, CardContent } from '../../ui/card';
import { Copy, Check } from 'lucide-react';
import { EmailLanguageSelector } from '../../shared/EmailLanguageSelector';
import i18n from '../../../i18n';
import { usePreviewEmailTextFromResult } from '../../../hooks/usePreviewEmailTextFromResult';
import type { ScoringResult } from '../../../hooks/useScoring';

interface EmailOutputProps {
  subject: string;
  body: string;
  scoringResult?: ScoringResult | null;
  calculatorResults?: Record<string, unknown>;
}

export const EmailOutput = ({
  subject,
  body,
  scoringResult,
  calculatorResults,
}: EmailOutputProps) => {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);
  const [emailLanguage, setEmailLanguage] = useState(i18n.language);

  // The pre-save scoring screen has no saved evaluation, so it re-renders the
  // in-memory result via the stateless POST /email/preview endpoint (the one
  // unified renderer). The score response's email_body (Indonesian) is the
  // initial/fallback render so there is no flash while the preview loads.
  const { data: previewBody } = usePreviewEmailTextFromResult(
    scoringResult,
    emailLanguage,
    calculatorResults,
  );

  const displaySubject = scoringResult?.email_subject ?? subject;
  const displayBody = previewBody ?? scoringResult?.email_body ?? body;

  const handleCopy = async () => {
    const fullText = `Subject: ${displaySubject}\n\n${displayBody}`;
    await navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card>
      <CardContent className="pt-4">
        <div className="mb-2 flex items-center justify-between">
          <p className="text-sm font-semibold">{t('emailOutput.title')}</p>
          <div className="flex items-center gap-2">
            {scoringResult && (
              <EmailLanguageSelector
                value={emailLanguage}
                onChange={setEmailLanguage}
              />
            )}
            <Button variant="outline" size="sm" onClick={handleCopy}>
              {copied ? (
                <Check className="mr-1 size-3.5" aria-hidden="true" />
              ) : (
                <Copy className="mr-1 size-3.5" aria-hidden="true" />
              )}
              {copied ? t('emailOutput.copied') : t('emailOutput.copy')}
            </Button>
          </div>
        </div>
        <p className="mb-2 text-xs text-muted-foreground">{displaySubject}</p>
        <pre className="max-h-64 overflow-auto whitespace-pre-wrap rounded-md bg-muted p-3 text-xs">
          {displayBody}
        </pre>
      </CardContent>
    </Card>
  );
};
