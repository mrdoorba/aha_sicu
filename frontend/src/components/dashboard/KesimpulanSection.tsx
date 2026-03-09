import { Card, CardContent } from '../ui/card';
import { useTranslation } from 'react-i18next';

interface KesimpulanSectionProps {
  calculatorResults: Record<string, unknown>;
}

function parseBulletPoints(text: string): string[] {
  return text
    .split('\n')
    .map((line) => line.replace(/^[-•]\s*/, '').trim())
    .filter(Boolean);
}

export const KesimpulanSection = ({ calculatorResults }: KesimpulanSectionProps) => {
  const { t } = useTranslation();
  const summary = calculatorResults.scoring_summary as
    | { conclusion?: string; marketing_estimation?: string; marketing_budget?: string }
    | undefined;

  return (
    <Card className="border-none shadow-xl bg-card overflow-hidden">
      <CardContent className="p-8">
        <div className="flex items-center gap-2 mb-6">
          <span className="text-xs font-black text-primary/40 tracking-widest">05</span>
          <h2 className="text-lg font-bold tracking-tight text-foreground">
            {t('presentation.section.kesimpulan')}
          </h2>
        </div>

        {!summary ? (
          <p className="text-sm text-muted-foreground py-6 text-center">{t('common.noData')}</p>
        ) : (
          <div className="space-y-6">
            {summary.conclusion && (
              <ul className="space-y-2">
                {parseBulletPoints(summary.conclusion).map((point, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-foreground">
                    <span className="mt-1.5 size-1.5 rounded-full bg-primary shrink-0" />
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {summary.marketing_estimation && (
                <div className="rounded-xl border border-border/50 bg-muted/30 p-5">
                  <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2">
                    {t('presentation.kesimpulan.marketingEstimation')}
                  </p>
                  <p className="text-lg font-bold text-primary">{summary.marketing_estimation}</p>
                </div>
              )}

              {summary.marketing_budget && (
                <div className="rounded-xl border border-border/50 bg-muted/30 p-5">
                  <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2">
                    {t('presentation.kesimpulan.marketingBudget')}
                  </p>
                  <p className="text-lg font-bold text-primary">{summary.marketing_budget}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
