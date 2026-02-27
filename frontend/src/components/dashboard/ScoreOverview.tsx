import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from 'recharts';
import { CheckCircle2, XCircle } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';
import { useTranslation } from 'react-i18next';

interface ScoreOverviewProps {
  score: number;
  verdict: string;
  template: string;
}

export const ScoreOverview = ({ score, verdict, template }: ScoreOverviewProps) => {
  const { t } = useTranslation();

  const isApproved = verdict === '✔️';
  const isRejected = verdict.startsWith('❌');

  const chartData = [{ name: 'score', value: score, fill: isApproved ? 'var(--success)' : isRejected ? 'var(--destructive)' : 'var(--muted)' }];

  return (
    <Card className="border-none shadow-2xl bg-gradient-to-br from-card to-muted/30 overflow-hidden relative">
      <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full -mr-48 -mt-48 blur-3xl opacity-60 pointer-events-none" />
      <CardContent className="p-8 relative z-10">
        <div className="flex items-center gap-2 mb-6">
          <span className="text-xs font-black text-primary/40 tracking-widest">01</span>
          <h2 className="text-lg font-bold tracking-tight text-foreground">{t('presentation.section.scoreOverview')}</h2>
        </div>

        <div className="grid gap-8 md:grid-cols-2 items-center">
          {/* Left: Score + Verdict + Conclusion */}
          <div className="flex flex-col items-center md:items-start gap-6">
            <div className="flex items-baseline gap-2">
              <span className="text-7xl font-black tabular-nums tracking-tighter">{score}</span>
              <span className="text-2xl text-muted-foreground font-medium">/100</span>
            </div>

            <Badge
              className={cn(
                'flex items-center gap-2 px-6 py-2 text-base font-black uppercase tracking-widest border',
                isApproved ? 'bg-success text-white border-success' :
                isRejected ? 'bg-destructive text-white border-destructive' :
                'bg-muted text-muted-foreground border-border'
              )}
            >
              {isApproved ? <CheckCircle2 className="size-5" /> : isRejected ? <XCircle className="size-5" /> : null}
              {isApproved ? t('presentation.verdict.approved') : isRejected ? t('presentation.verdict.rejected') : t('presentation.verdict.pending')}
            </Badge>

            <div className="text-xs text-muted-foreground/60">
              <span>{template === 'fashion' ? t('evaluationSections.fashion') : t('evaluationSections.nonFashion')}</span>
            </div>
          </div>

          {/* Right: Radial Ring Chart with Score Inside */}
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
                <span className="text-5xl font-bold tabular-nums tracking-tight">{score}</span>
                <span className="text-xs font-semibold tracking-widest text-muted-foreground uppercase">Score</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
