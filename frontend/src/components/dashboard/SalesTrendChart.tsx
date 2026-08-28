import { useTranslation } from 'react-i18next';
import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  ReferenceLine,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export interface SalesTrendPoint {
  /** Month label as rendered on the cards, e.g. "Mar 2026". */
  month: string;
  value: number;
  /** True for the latest evaluated month — the emphasised bar. */
  isLatest: boolean;
}

interface SalesTrendChartProps {
  data: SalesTrendPoint[];
  /** 6-month average; drawn as the baseline the latest month is scored against. */
  average: number;
}

/** 27,972,564 → "28.0M" for axis ticks and the reference-line label. */
function compact(value: number): string {
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(1)}B`;
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(0)}K`;
  return String(value);
}

/**
 * The business category's trend card. Call it for that category only — it always
 * renders, because the Real Benchmark note it carries has to reach the prospect
 * even for a brand with too little history to plot (that is when mistaking
 * Seller Center omset for the benchmark costs most). The chart itself appears
 * only when there is a series.
 */
export const SalesTrendChart = ({ data, average }: SalesTrendChartProps) => {
  const { t } = useTranslation();

  const hasTrend = data.length > 0;

  return (
    <div className="mt-6 rounded-lg border border-border/80 bg-card p-4">
      {hasTrend && (
      <>
      <div className="mb-4 flex items-baseline justify-between gap-4">
        <p className="text-sm font-semibold text-foreground">{t('presentation.salesTrend.title')}</p>
        <p className="text-xs text-muted-foreground">
          {t('scoring.avgSales6mo')}
          <span className="ml-1.5 font-bold tabular-nums text-foreground">
            {average.toLocaleString('en-US')}
          </span>
        </p>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }} barCategoryGap="28%">
            <CartesianGrid stroke="var(--chart-grid)" strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="month"
              tick={{ fontSize: 12, fill: 'var(--muted-foreground)', fontWeight: 500 }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              width={52}
              tickFormatter={compact}
              tick={{ fontSize: 11, fill: 'var(--muted-foreground)' }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              cursor={{ fill: 'var(--chart-grid)', fillOpacity: 0.25 }}
              contentStyle={{
                background: 'var(--card)',
                border: '1px solid var(--border)',
                borderRadius: '0.5rem',
                fontSize: '0.8125rem',
              }}
              labelStyle={{ color: 'var(--muted-foreground)', fontWeight: 600 }}
              itemStyle={{ color: 'var(--foreground)', fontWeight: 700 }}
              formatter={(value?: number) => [
                typeof value === 'number' ? value.toLocaleString('en-US') : '-',
                t('presentation.salesTrend.tooltip'),
              ]}
            />
            {average > 0 && (
              <ReferenceLine
                y={average}
                stroke="var(--muted-foreground)"
                strokeDasharray="5 4"
                strokeWidth={2}
                label={{
                  value: compact(average),
                  position: 'right',
                  fontSize: 11,
                  fill: 'var(--muted-foreground)',
                }}
              />
            )}
            <Bar dataKey="value" radius={[4, 4, 0, 0]} isAnimationActive={false}>
              {data.map((point) => (
                <Cell
                  key={point.month}
                  // ponytail: emphasis form — latest month in the accent hue, the
                  // five context months recede. Single series, so no legend.
                  fill={point.isLatest ? 'var(--chart-1)' : 'var(--muted-foreground)'}
                  fillOpacity={point.isLatest ? 1 : 0.28}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      </>
      )}

      {/* The benchmark the prospect actually gets is not the one drawn above:
          Seller Center omset only picks the scheme. Same copy, same keys, as
          the email's Bisnis section — see layout.py's SectionNote. */}
      <div className={hasTrend ? 'mt-4 border-t border-border/80 pt-4' : ''}>
        <div className="rounded-md border-l-[3px] border-primary bg-primary/10 px-3 py-2.5">
          <p className="mb-1 text-[11px] font-bold uppercase tracking-wider text-primary">
            {t('presentation.salesTrend.realBenchmark.label')}
          </p>
          <p className="text-xs leading-relaxed text-foreground">
            {t('presentation.salesTrend.realBenchmark.note')}
          </p>
        </div>
      </div>
    </div>
  );
};
