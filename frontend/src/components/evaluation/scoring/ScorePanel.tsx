import { useTranslation } from 'react-i18next';
import type { ScoringResult } from '../../../hooks/useScoring';
import { CATEGORY_MAP } from '../../../lib/categoryMap';

interface ScorePanelProps {
  scoringResult: ScoringResult | null;
}

export const ScorePanel = ({ scoringResult }: ScorePanelProps) => {
  const { t } = useTranslation();

  return (
    <div className="sticky top-6 rounded-lg border bg-card p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase text-muted-foreground">
        {t('scorePanel.scoreSummary')}
      </h3>

      <div className="mb-3 text-center">
        <div className="text-3xl font-bold tabular-nums">
          {scoringResult ? Math.round(scoringResult.total_score) : '\u2014'}
        </div>
        <div className="text-xs text-muted-foreground">{t('scorePanel.totalScore')}</div>
      </div>

      <div className="space-y-1 text-sm text-muted-foreground">
        {CATEGORY_MAP.map(({ backend, labelKey }) => {
          const cat = scoringResult?.category_scores.find(
            (c) => c.category === backend,
          );
          return (
            <div key={backend} className="flex justify-between">
              <span>{t(labelKey)}</span>
              <span className="tabular-nums">
                {cat
                  ? cat.available
                    ? Math.round(cat.score)
                    : t('scorePanel.notAvailable')
                  : '\u2014'}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
