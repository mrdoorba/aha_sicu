import { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '../../ui/button';
import { Card, CardContent } from '../../ui/card';
import { Copy, Check } from 'lucide-react';
import { EmailLanguageSelector } from '../../shared/EmailLanguageSelector';
import {
  buildI18nEmailBody,
  type ScoringConclusionData,
} from '../../../utils/buildI18nEmailBody';
import i18n from '../../../i18n';
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
  const fixedT = useMemo(() => i18n.getFixedT(emailLanguage), [emailLanguage]);

  const displaySubject = useMemo(() => {
    const subjectI18n = scoringResult?.email_subject_i18n;
    if (subjectI18n) {
      return fixedT(subjectI18n.key, subjectI18n.vars);
    }
    return subject;
  }, [fixedT, scoringResult?.email_subject_i18n, subject]);

  const displayBody = useMemo(() => {
    if (scoringResult) {
      const summary: ScoringConclusionData = {
        conclusion: scoringResult.conclusion,
        conclusion_i18n: scoringResult.conclusion_i18n,
        marketing_budget: scoringResult.marketing_budget,
        marketing_budget_i18n: scoringResult.marketing_budget_i18n,
        closing_message: scoringResult.closing_message,
        closing_message_i18n: scoringResult.closing_message_i18n,
        marketing_estimation: scoringResult.marketing_estimation,
      };
      return buildI18nEmailBody(
        scoringResult.category_scores,
        summary,
        fixedT,
        calculatorResults,
      );
    }
    return body;
  }, [scoringResult, fixedT, body, calculatorResults]);

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
