import { useState } from 'react';
import { Card, CardContent } from '../ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/tabs';
import { CategoryMetricCard } from './CategoryMetricCard';
import { useTranslation } from 'react-i18next';
import { CATEGORY_MAP } from '../../lib/categoryMap';

interface RowScore {
  metric: string;
  value: unknown;
  benchmark: string;
  verdict: string;
  message: string;
  score: number;
  metric_i18n?: { key: string; vars: Record<string, string> } | null;
  message_i18n?: { key: string; vars: Record<string, string> } | null;
  benchmark_i18n?: { key: string; vars: Record<string, string> } | null;
}

interface CategoryBreakdown {
  category: string;
  score: number;
  max_score: number;
  rows?: RowScore[];
}

interface DetailedEvaluationProps {
  scoreBreakdown: CategoryBreakdown[];
}

export const DetailedEvaluation = ({ scoreBreakdown }: DetailedEvaluationProps) => {
  const { t } = useTranslation();
  const [visitedTabs, setVisitedTabs] = useState<Set<string>>(new Set([scoreBreakdown[0]?.category ?? '']));

  const handleTabChange = (value: string) => {
    setVisitedTabs((prev) => new Set(prev).add(value));
  };

  if (scoreBreakdown.length === 0) return null;

  return (
    <Card className="border-none shadow-xl bg-card overflow-hidden">
      <CardContent className="p-8">
        <div className="flex items-center gap-2 mb-6">
          <span className="text-xs font-black text-primary/40 tracking-widest">02</span>
          <h2 className="text-lg font-bold tracking-tight text-foreground">{t('presentation.section.detailedEvaluation')}</h2>
        </div>

        <Tabs defaultValue={scoreBreakdown[0]?.category} onValueChange={handleTabChange}>
          <TabsList variant="line" className="w-full flex-wrap justify-start mb-6">
            {scoreBreakdown.map((cat) => {
              const mapped = CATEGORY_MAP.find((m) => m.backend === cat.category);
              const label = mapped ? t(mapped.labelKey) : cat.category;
              return (
                <TabsTrigger key={cat.category} value={cat.category} className="text-xs">
                  {label}
                </TabsTrigger>
              );
            })}
          </TabsList>

          {scoreBreakdown.map((cat) => (
            <TabsContent key={cat.category} value={cat.category}>
              {visitedTabs.has(cat.category) && (
                <>
                  {cat.rows && cat.rows.length > 0 ? (
                    <div className="grid gap-3 sm:grid-cols-2">
                      {cat.rows.flatMap((row, idx) => {
                        const card = (
                          <div key={idx}>
                            <CategoryMetricCard
                              metric={row.metric}
                              value={row.value}
                              verdict={row.verdict}
                              score={row.score}
                              benchmark={row.benchmark}
                              message={row.message}
                              metric_i18n={row.metric_i18n}
                              message_i18n={row.message_i18n}
                              benchmark_i18n={row.benchmark_i18n}
                            />
                          </div>
                        );
                        if (row.metric.startsWith('Rata² Penjualan') || row.metric === 'Program Afiliasi' || row.metric === 'ROI') {
                          return [
                            card,
                            <div key={`spacer-${idx}`} className="hidden sm:block" />,
                            <div key={`separator-${idx}`} className="col-span-2 border-t border-primary/30" />,
                          ];
                        }
                        return [card];
                      })}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground py-8 text-center">
                      {t('presentation.detailedEvaluation.noMetrics')}
                    </p>
                  )}
                </>
              )}
            </TabsContent>
          ))}
        </Tabs>
      </CardContent>
    </Card>
  );
};
