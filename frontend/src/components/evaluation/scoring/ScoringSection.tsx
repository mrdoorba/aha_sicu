import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '../../ui/card';
import { Button } from '../../ui/button';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { FinalScoreDisplay } from './FinalScoreDisplay';
import { ScoreBreakdown } from './ScoreBreakdown';
import { EmailOutput } from './EmailOutput';
import { WhatsAppLink } from './WhatsAppLink';
import { VerdictSelector } from './VerdictSelector';
import type { ScoringResult } from '../../../hooks/useScoring';

interface ScoringSectionProps {
  onGenerate: (request: {
    template: 'fashion' | 'non_fashion';
    verdict: string;
    store_name: string;
    period: string;
    brand_name: string;
  }) => void;
  scoringResult: ScoringResult | null;
  isGenerating: boolean;
  isStale: boolean;
  error: Error | null;
  categoryType: string | null;
  storeName: string;
  brandName: string;
}

export const ScoringSection = ({
  onGenerate,
  scoringResult,
  isGenerating,
  isStale,
  error,
  categoryType,
  storeName,
  brandName,
}: ScoringSectionProps) => {
  const { t } = useTranslation();
  const [verdict, setVerdict] = useState('✔️');
  const [period, setPeriod] = useState('');

  const canGenerate = !!categoryType;
  const canSave = !!verdict && !!period;

  const handleGenerate = () => {
    if (!canGenerate) return;
    onGenerate({
      template: categoryType as 'fashion' | 'non_fashion',
      verdict,
      store_name: storeName,
      period,
      brand_name: brandName,
    });
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="pt-4">
          <p className="mb-4 font-semibold">{t('scoring.finalScore')}</p>

          <div className="flex flex-wrap items-end gap-4">
            <Button
              onClick={handleGenerate}
              disabled={!canGenerate || isGenerating}
            >
              {isGenerating ? (
                <RefreshCw className="mr-1 size-4 animate-spin" aria-hidden="true" />
              ) : null}
              {scoringResult && !isStale ? t('scoring.recalculate') : t('scoring.calculate')}
            </Button>
          </div>

          {!categoryType && (
            <p className="mt-2 text-sm text-muted-foreground">
              {t('scoring.selectCategory')}
            </p>
          )}

          {isStale && scoringResult && (
            <div className="mt-3 flex items-center gap-2 rounded-md bg-yellow-50 p-2 text-sm text-yellow-800">
              <AlertTriangle className="size-4 shrink-0" aria-hidden="true" />
              {t('scoring.staleWarning')}
            </div>
          )}

          {error && (
            <p className="mt-2 text-sm text-destructive">
              {t('scoring.errorPrefix')} {error.message}
            </p>
          )}

          {scoringResult && (
            <div className="mt-4 flex flex-wrap items-end gap-4 border-t pt-4">
              <VerdictSelector value={verdict} onChange={setVerdict} />

              <div className="space-y-1">
                <label className="text-sm font-medium" htmlFor="scoring-period">
                  {t('scoring.period')}
                </label>
                <input
                  id="scoring-period"
                  type="text"
                  value={period}
                  onChange={(e) => setPeriod(e.target.value)}
                  placeholder={t('scoring.periodPlaceholder')}
                  className="h-9 w-40 rounded-md border border-input bg-background px-3 text-sm"
                />
              </div>

              {canSave && (
                <Button
                  variant="outline"
                  onClick={handleGenerate}
                  disabled={isGenerating}
                >
                  {isGenerating ? (
                    <RefreshCw className="mr-1 size-4 animate-spin" aria-hidden="true" />
                  ) : null}
                  {t('scoring.recalculateWithVerdict')}
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {scoringResult && (
        <>
          <Card>
            <CardContent className="pt-4">
              <FinalScoreDisplay
                totalScore={scoringResult.total_score}
                verdict={scoringResult.verdict}
                template={scoringResult.template}
              />
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-4">
              <p className="mb-2 text-sm font-semibold">{t('scoring.perCategoryBreakdown')}</p>
              <ScoreBreakdown categoryScores={scoringResult.category_scores} />
            </CardContent>
          </Card>

          <EmailOutput
            subject={scoringResult.email_subject}
            body={scoringResult.email_body}
          />

          <div className="flex items-center gap-3">
            <WhatsAppLink link={scoringResult.whatsapp_link} />
          </div>
        </>
      )}
    </div>
  );
};
