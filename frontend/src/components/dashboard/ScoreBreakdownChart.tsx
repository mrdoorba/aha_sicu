import { forwardRef } from 'react';
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts';
import { Card, CardContent } from '../ui/card';
import { cn } from '../../lib/utils';
import { useTranslation } from 'react-i18next';
import { CATEGORY_MAP } from '../../lib/categoryMap';
import { computeCategoryVerdictCounts } from '../../lib/verdictCounts';

interface RowData {
  verdict: string;
}

interface CategoryBreakdown {
  category: string;
  score: number;
  max_score: number;
  rows?: RowData[];
}

interface ScoreBreakdownChartProps {
  scoreBreakdown: CategoryBreakdown[];
}

export const ScoreBreakdownChart = forwardRef<HTMLDivElement, ScoreBreakdownChartProps>(({ scoreBreakdown }, ref) => {
  const { t } = useTranslation();

  const radarData = scoreBreakdown.map((cat) => {
    const mapped = CATEGORY_MAP.find((m) => m.backend === cat.category);
    const label = mapped ? t(mapped.labelKey) : cat.category;
    const counts = computeCategoryVerdictCounts(cat.rows || []);
    const percent = counts.total > 0 ? counts.score : 0;
    return { category: label, value: percent, fullMark: 100 };
  });

  return (
    <Card className="border-none shadow-xl bg-card overflow-hidden">
      <CardContent className="p-8">
        <div className="flex items-center gap-2 mb-6">
          <span className="text-xs font-black text-primary/40 tracking-widest">04</span>
          <h2 className="text-lg font-bold tracking-tight text-foreground">{t('presentation.section.scoreBreakdown')}</h2>
        </div>

        <div className="grid gap-8 lg:grid-cols-2 items-center">
          {/* Left: Radar Chart */}
          <div ref={ref} className="w-full h-96 bg-card rounded-lg">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData} outerRadius="70%">
                <PolarGrid gridType="polygon" stroke="var(--chart-grid)" />
                <PolarAngleAxis
                  dataKey="category"
                  tick={{ fontSize: 12, fill: 'var(--muted-foreground)', fontWeight: 500 }}
                  tickLine={false}
                />
                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                  name="Score"
                  dataKey="value"
                  stroke="var(--chart-radar-stroke)"
                  fill="var(--chart-radar-fill)"
                  fillOpacity={0.3}
                  strokeWidth={2.5}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Right: Category Bars with ✔️/❌ counts */}
          <div className="space-y-4">
            {scoreBreakdown.map((cat, idx) => {
              const mapped = CATEGORY_MAP.find((m) => m.backend === cat.category);
              const label = mapped ? t(mapped.labelKey) : cat.category;
              const counts = computeCategoryVerdictCounts(cat.rows || []);
              const percent = counts.total > 0 ? counts.score : 0;

              return (
                <div key={idx} className="space-y-1.5">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-semibold text-foreground">{label}</span>
                    <span className="font-bold tabular-nums text-muted-foreground">
                      <span className="text-green-600">✔️ {counts.checks}</span>
                      <span className="text-muted-foreground/50 mx-1">/</span>
                      <span className="text-orange-500">❌ {counts.xs}</span>
                    </span>
                  </div>
                  <div className="h-2.5 w-full overflow-hidden rounded-full bg-muted-foreground/20">
                    <div
                      className={cn(
                        'h-full rounded-full transition-all duration-1000 ease-out',
                        percent >= 80
                          ? 'bg-success'
                          : percent >= 50
                            ? 'bg-primary'
                            : 'bg-orange-500'
                      )}
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

ScoreBreakdownChart.displayName = 'ScoreBreakdownChart';
