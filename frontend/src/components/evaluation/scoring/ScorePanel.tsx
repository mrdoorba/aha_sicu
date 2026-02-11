import type { ScoringResult } from '../../../hooks/useScoring';

// Map backend Indonesian category names → English display labels
const CATEGORY_MAP: Array<{ backend: string; label: string }> = [
  { backend: 'Kesehatan Operasional Toko', label: 'Operational' },
  { backend: 'Bisnis Analisis', label: 'Business' },
  { backend: 'Skor Kesehatan Konten', label: 'Content' },
  { backend: 'Tinjauan Pengunjung', label: 'Visitors' },
  { backend: 'Promo Toko', label: 'Promo Tools' },
  { backend: 'Jumlah Produk & Status Toko', label: 'Products/Status' },
  { backend: 'Data Iklan', label: 'Ads' },
  { backend: 'Partisipasi Campaign', label: 'Campaign' },
  { backend: 'Kompetisi TOP Produk', label: 'Competition' },
  { backend: 'Stok', label: 'Stock' },
  { backend: 'Discount', label: 'Discount' },
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
        {CATEGORY_MAP.map(({ backend, label }) => {
          const cat = scoringResult?.category_scores.find(
            (c) => c.category === backend,
          );
          return (
            <div key={backend} className="flex justify-between">
              <span>{label}</span>
              <span className="tabular-nums">
                {cat
                  ? cat.available
                    ? Math.round(cat.score)
                    : 'N/A'
                  : '\u2014'}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
