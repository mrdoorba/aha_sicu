import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from 'recharts';
import { CheckCircle2, XCircle, TrendingUp } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { useTranslation } from 'react-i18next';
import { computeVerdictCounts, type VerdictCounts } from '../../lib/verdictCounts';

interface RowData {
  verdict: string;
}

interface CategoryBreakdown {
  category: string;
  score: number;
  max_score: number;
  rows?: RowData[];
}

interface ScoreOverviewProps {
  score: number;
  verdict: string;
  template: string;
  scoreBreakdown?: CategoryBreakdown[];
}

export const ScoreOverview = ({ score, scoreBreakdown }: ScoreOverviewProps) => {
  const { t } = useTranslation();

  // Compute partner score from ✔️/❌ verdicts
  const counts: VerdictCounts = scoreBreakdown
    ? computeVerdictCounts(scoreBreakdown)
    : { checks: 0, xs: 0, total: 0, score: Math.round(score) };

  const partnerScore = counts.score;

  const chartData = [{ name: 'score', value: partnerScore, fill: 'var(--primary)' }];

  return (
    <Card className="border-none shadow-2xl bg-gradient-to-br from-card to-muted/30 overflow-hidden relative">
      <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full -mr-48 -mt-48 blur-3xl opacity-60 pointer-events-none" />
      <CardContent className="p-8 relative z-10">
        <div className="flex items-center gap-2 mb-6">
          <span className="text-xs font-black text-primary/40 tracking-widest">01</span>
          <h2 className="text-lg font-bold tracking-tight text-foreground">{t('presentation.section.scoreOverview')}</h2>
        </div>

        <div className="grid gap-8 md:grid-cols-2 items-center">
          {/* Left: Score + Verdict + Counts */}
          <div className="flex flex-col items-center md:items-start gap-6">
            <div className="flex items-baseline gap-2">
              <span className="text-7xl font-black tabular-nums tracking-tighter">{partnerScore}</span>
              <span className="text-2xl text-muted-foreground font-medium">/100</span>
            </div>

            {/* ✔️/❌ counts */}
            {counts.total > 0 && (
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="size-5 text-green-600" />
                  <span className="text-lg font-bold text-green-600 tabular-nums">{counts.checks}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <XCircle className="size-5 text-orange-500" />
                  <span className="text-lg font-bold text-orange-500 tabular-nums">{counts.xs}</span>
                </div>
              </div>
            )}

            <div className="flex flex-wrap items-center justify-center gap-3 md:justify-start">
              <div className="inline-flex items-baseline gap-2 rounded-full border border-primary/15 bg-primary/[0.07] px-4 py-2">
                <span className="text-xs font-bold text-foreground">{t('scoreOverview.compatibility')}</span>
                <span className="text-lg font-black tabular-nums leading-none text-primary">
                  {Math.round(score)}
                  <span className="text-xs font-semibold text-muted-foreground">/100</span>
                </span>
              </div>

              <Badge
                className="flex items-center gap-2 px-5 py-2 text-sm font-bold tracking-wide border bg-primary/10 text-primary border-primary/20"
                variant="outline"
              >
                <TrendingUp className="size-4" />
                {t('scoreOverview.verdict')}
              </Badge>
            </div>

          </div>

          {/* Right: Radial Ring Chart */}
          <div className="flex justify-center">
            <div className="relative w-56 h-56">
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart
                  cx="50%"
                  cy="50%"
                  innerRadius="75%"
                  outerRadius="100%"
                  barSize={16}
                  data={chartData}
                  startAngle={90}
                  endAngle={-270}
                >
                  <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
                  <RadialBar
                    background={{ fill: 'hsl(var(--muted-foreground) / 0.15)' }}
                    dataKey="value"
                    angleAxisId={0}
                    cornerRadius={10}
                  />
                </RadialBarChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-5xl font-bold tabular-nums tracking-tight">{partnerScore}</span>
                <span className="text-xs font-semibold tracking-widest text-muted-foreground uppercase">{t('scoreOverview.scoreLabel')}</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
