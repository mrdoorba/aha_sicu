import { useTranslation } from 'react-i18next';
import type { ScoringResult } from '../../../hooks/useScoring';
import type { PackageFit } from '../../../hooks/useBrandDetail';
import { CATEGORY_MAP } from '../../../lib/categoryMap';

interface ScorePanelProps {
  scoringResult: ScoringResult | null;
  packageFit?: PackageFit | null;
}

export const ScorePanel = ({ scoringResult, packageFit }: ScorePanelProps) => {
  const { t } = useTranslation();
  const adjustment = scoringResult?.vp_adjustment ?? 0;

  return (
    <div className="sticky top-6 rounded-lg border bg-card p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase text-muted-foreground">
        {t('scorePanel.scoreSummary')}
      </h3>

      <div className="mb-3 text-center">
        <div className="text-3xl font-bold tabular-nums">
          {scoringResult ? Math.round(scoringResult.total_score) : '—'}
        </div>
        <div className="text-xs text-muted-foreground">{t('scorePanel.totalScore')}</div>
      </div>

      {/* The VP adjustment sits between the category rows and the total, so the
          rows below still add up to a number the reader can see. */}
      {scoringResult ? (
        <div className="mb-3 space-y-1 border-b pb-3 text-xs">
          <div className="flex justify-between text-muted-foreground">
            <span>{t('scorePanel.categoryTotal')}</span>
            <span className="tabular-nums">{Math.round(scoringResult.category_total)}</span>
          </div>
          <div
            className={`flex justify-between ${
              adjustment < 0 ? 'font-semibold text-destructive' : 'text-muted-foreground'
            }`}
          >
            <span>{t('scorePanel.vpAdjustment')}</span>
            <span className="tabular-nums">
              {adjustment < 0 ? `−${Math.abs(adjustment)}` : 0}
            </span>
          </div>
          {packageFit ? (
            <p className="text-[11px] leading-snug text-muted-foreground">
              {packageFit.vp !== null && packageFit.bar !== null
                ? t(packageFit.met ? 'scorePanel.vpMet' : 'scorePanel.vpShortfall', {
                    vp: Math.round(packageFit.vp),
                    bar: Math.round(packageFit.bar),
                    package: packageFit.package ?? '',
                  })
                : t('scorePanel.vpUnjudged')}
            </p>
          ) : null}
        </div>
      ) : null}

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
                  : '—'}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
