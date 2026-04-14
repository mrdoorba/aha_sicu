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
  value_i18n?: { key: string; vars: Record<string, string> } | null;
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
  marketplace?: string;
  manualInputs?: Record<string, unknown>;
  calculatorResults?: Record<string, unknown>;
}

export const DetailedEvaluation = ({
  scoreBreakdown,
  marketplace,
  manualInputs,
  calculatorResults,
}: DetailedEvaluationProps) => {
  const { t } = useTranslation();
  const [visitedTabs, setVisitedTabs] = useState<Set<string>>(new Set([scoreBreakdown[0]?.category ?? '']));

  const affiliateCommission = (() => {
    const promoTools = manualInputs?.promoTools;
    if (!promoTools || typeof promoTools !== 'object') return null;
    const value = (promoTools as Record<string, unknown>).komisiProgramAfiliasi;
    return typeof value === 'number' ? value : null;
  })();

  const discountAffiliateCommission = (() => {
    const discount = calculatorResults?.discount;
    if (!discount || typeof discount !== 'object') return null;
    const details = (discount as Record<string, unknown>).details;
    if (!details || typeof details !== 'object') return null;

    const i18n = (details as Record<string, unknown>).i18n;
    const affiliateCommissionI18n = i18n && typeof i18n === 'object'
      ? (i18n as Record<string, unknown>).affiliateCommission
      : null;

    if (affiliateCommissionI18n && typeof affiliateCommissionI18n === 'object') {
      const vars = (affiliateCommissionI18n as { vars?: Record<string, unknown> }).vars;
      const value = vars?.value;
      if (typeof value === 'string' && value.trim()) return value;
    }

    const value = (details as Record<string, unknown>).affiliate_commission_pct;
    return typeof value === 'string' && value.trim() ? value : null;
  })();

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
                  {(() => {
                    const cards = cat.rows?.flatMap((row, idx) => {
                      const discountAffiliateCommissionLine = (
                        cat.category === 'Discount'
                        && idx === 0
                        && discountAffiliateCommission !== null
                        && !row.message.includes(discountAffiliateCommission)
                      )
                        ? [t('discount.output.affiliateCommission', { value: discountAffiliateCommission })]
                        : [];

                      const rowCards = [
                        <div key={idx}>
                          <CategoryMetricCard
                            metric={row.metric}
                            value={row.value}
                            verdict={row.verdict}
                            score={row.score}
                            benchmark={(row.metric_i18n?.key === 'scoring.adCost' || row.metric === 'Biaya (iklan)') ? '-' : row.benchmark}
                            message={row.message}
                            metric_i18n={row.metric_i18n}
                            value_i18n={row.value_i18n}
                            message_i18n={row.message_i18n}
                            benchmark_i18n={row.benchmark_i18n}
                            extraDetails={discountAffiliateCommissionLine}
                            marketplace={marketplace}
                          />
                        </div>,
                      ];
                      const shouldShowAffiliateCommission = (
                        affiliateCommission !== null
                        && (row.metric_i18n?.key === 'scoring.promo.programAfiliasi' || row.metric === 'Program Afiliasi')
                      );
                      if (shouldShowAffiliateCommission) {
                        rowCards.push(
                          <div key={`affiliate-commission-${idx}`}>
                            <CategoryMetricCard
                              metric={t('fields.promoTools.komisiProgramAfiliasi')}
                              value={affiliateCommission}
                              verdict="-"
                              score={0}
                              benchmark=""
                              message=""
                              marketplace={marketplace}
                            />
                          </div>,
                        );
                      }
                      if (row.metric_i18n?.key === 'scoring.avgSales6mo' || row.metric.startsWith('Rata² Penjualan') || row.metric_i18n?.key === 'scoring.promo.programAfiliasi' || row.metric === 'Program Afiliasi' || row.metric === 'ROI') {
                        return [
                          ...rowCards,
                          ...(rowCards.length === 1
                            ? [<div key={`spacer-${idx}`} className="hidden sm:block" />]
                            : []),
                          <div key={`separator-${idx}`} className="col-span-2 border-t border-primary/30" />,
                        ];
                      }
                      return rowCards;
                    }) ?? [];

                    return cards.length > 0 ? (
                    <div className="grid gap-3 sm:grid-cols-2">
                      {cards}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground py-8 text-center">
                      {t('presentation.detailedEvaluation.noMetrics')}
                    </p>
                    );
                  })()}
                </>
              )}
            </TabsContent>
          ))}
        </Tabs>
      </CardContent>
    </Card>
  );
};
