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

interface CategoryBreakdown {
  category: string;
  score: number;
  max_score: number;
}

interface ScoreBreakdownChartProps {
  scoreBreakdown: CategoryBreakdown[];
}

export const ScoreBreakdownChart = ({ scoreBreakdown }: ScoreBreakdownChartProps) => {
  const { t } = useTranslation();

  const EXCLUDED_CATEGORIES = ['Kompetisi TOP Produk'];

  const filteredBreakdown = scoreBreakdown.filter(
    (cat) => !EXCLUDED_CATEGORIES.includes(cat.category)
  );

  const radarData = filteredBreakdown.map((cat) => {
    const mapped = CATEGORY_MAP.find((m) => m.backend === cat.category);
    const label = mapped ? t(mapped.labelKey) : cat.category;
    const percent = cat.max_score > 0 ? (cat.score / cat.max_score) * 100 : 0;
    return { category: label, value: Math.round(percent), fullMark: 100 };
  });

  return (
    <Card className="border-none shadow-xl bg-card overflow-hidden">
      <CardContent className="p-8">
        <div className="flex items-center gap-2 mb-6">
          <span className="text-xs font-black text-primary/40 tracking-widest">02</span>
          <h2 className="text-lg font-bold tracking-tight text-foreground">{t('presentation.section.scoreBreakdown')}</h2>
        </div>

        <div className="grid gap-8 lg:grid-cols-2 items-center">
          {/* Left: Radar Chart */}
          <div className="w-full h-96">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData} outerRadius="70%">
                <PolarGrid gridType="polygon" stroke="hsl(var(--muted-foreground) / 0.4)" />
                <PolarAngleAxis
                  dataKey="category"
                  tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))', fontWeight: 500 }}
                  tickLine={false}
                />
                <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                  name="Score"
                  dataKey="value"
                  stroke="hsl(var(--primary))"
                  fill="hsl(var(--primary))"
                  fillOpacity={0.4}
                  strokeWidth={2}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Right: Horizontal Category Bars */}
          <div className="space-y-4">
            {filteredBreakdown.map((cat, idx) => {
              const mapped = CATEGORY_MAP.find((m) => m.backend === cat.category);
              const label = mapped ? t(mapped.labelKey) : cat.category;
              const percent = cat.max_score > 0 ? (cat.score / cat.max_score) * 100 : 0;

              return (
                <div key={idx} className="space-y-1.5">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-semibold text-foreground">{label}</span>
                    <span className="font-bold tabular-nums text-muted-foreground">
                      {cat.score.toFixed(1)}<span className="text-muted-foreground/50"> / {cat.max_score.toFixed(0)}</span>
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
};
