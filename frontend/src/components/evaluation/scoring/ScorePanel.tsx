import type { ScoringResult } from '../../../hooks/useScoring';

const CATEGORY_LABELS = [
  'Operational',
  'Business',
  'Content',
  'Visitors',
  'Promo Tools',
  'Products/Status',
  'Ads',
  'Campaign',
  'Competition',
  'Stock',
  'Discount',
];

interface ScorePanelProps {
  scoringResult: ScoringResult | null;
}

export const ScorePanel = ({ scoringResult }: ScorePanelProps) => {
  return (
    <div className="sticky top-6 rounded-lg border bg-card p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase text-muted-foreground">
        Score Summary
      </h3>

      <div className="mb-3 text-center">
        <div className="text-3xl font-bold tabular-nums">
          {scoringResult ? Math.round(scoringResult.total_score) : '\u2014'}
        </div>
        <div className="text-xs text-muted-foreground">Total Score</div>
      </div>

      <div className="space-y-1 text-sm text-muted-foreground">
        {CATEGORY_LABELS.map((label) => {
          const cat = scoringResult?.category_scores.find(
            (c) => c.category.toLowerCase() === label.toLowerCase(),
          );
          return (
            <div key={label} className="flex justify-between">
              <span>{label}</span>
              <span className="tabular-nums">
                {cat ? Math.round(cat.score) : '\u2014'}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
