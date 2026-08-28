import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DetailedEvaluation } from './DetailedEvaluation';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

// ResponsiveContainer measures its parent, which is 0×0 in jsdom — pin a size so
// recharts actually renders its children.
vi.mock('recharts', async () => {
  const actual = await vi.importActual<typeof import('recharts')>('recharts');
  return {
    ...actual,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <actual.ResponsiveContainer width={640} height={256}>{children}</actual.ResponsiveContainer>
    ),
  };
});

const MONTHS = ['Mar 2026', 'Feb 2026', 'Jan 2026', 'Dec 2025', 'Nov 2025', 'Oct 2025'];
const VALUES = [27_972_564, 36_670_965, 51_747_830, 43_587_016, 44_661_863, 50_879_010];

const businessBreakdown = [
  {
    category: 'Bisnis Analisis',
    score: 10,
    max_score: 25,
    rows: [
      {
        metric: `Penjualan Bulan ${MONTHS[0]}`,
        value: VALUES[0],
        benchmark: '>42,586,541',
        verdict: '❌',
        message: '',
        score: 0,
        metric_i18n: { key: 'scoring.monthlySales', vars: { month: MONTHS[0] } },
      },
      ...MONTHS.slice(1).map((month, i) => ({
        metric: `Penjualan Bulan ${month}`,
        value: VALUES[i + 1],
        benchmark: '-',
        verdict: '-',
        message: '',
        score: 0,
        metric_i18n: { key: 'scoring.pastMonthlySales', vars: { month } },
      })),
      {
        metric: 'Rata² Penjualan 6 bulan terakhir',
        value: 42_586_541,
        benchmark: '-',
        verdict: '-',
        message: '',
        score: 10,
        metric_i18n: { key: 'scoring.avgSales6mo', vars: {} },
      },
    ],
  },
];

describe('Business sales trend', () => {
  it('keeps the benchmarked latest month as a card and drops the five past-month cards', () => {
    render(<DetailedEvaluation scoreBreakdown={businessBreakdown} />);

    expect(screen.getByText('scoring.monthlySales')).toBeInTheDocument();
    expect(screen.queryByText('scoring.pastMonthlySales')).not.toBeInTheDocument();
    // The average survives as a card and as the chart's reference value.
    expect(screen.getAllByText('42,586,541').length).toBeGreaterThan(0);
  });

  it('plots all six months oldest-first', () => {
    const { container } = render(<DetailedEvaluation scoreBreakdown={businessBreakdown} />);

    const ticks = [...container.querySelectorAll('.recharts-cartesian-axis-tick-value')]
      .map((node) => node.textContent)
      .filter((label): label is string => MONTHS.includes(label ?? ''));

    expect(ticks).toEqual([...MONTHS].reverse());
  });

  it('emphasises only the latest month bar', () => {
    const { container } = render(<DetailedEvaluation scoreBreakdown={businessBreakdown} />);

    const bars = [...container.querySelectorAll('.recharts-bar-rectangle path')];
    expect(bars).toHaveLength(6);
    // Oldest-first, so the emphasised bar is last.
    expect(bars.at(-1)?.getAttribute('fill')).toBe('var(--chart-1)');
    expect(bars.at(0)?.getAttribute('fill')).toBe('var(--muted-foreground)');
  });

  it('closes the trend card with the Real Benchmark note', () => {
    render(<DetailedEvaluation scoreBreakdown={businessBreakdown} />);

    expect(screen.getByText('presentation.salesTrend.realBenchmark.label')).toBeInTheDocument();
    expect(screen.getByText('presentation.salesTrend.realBenchmark.note')).toBeInTheDocument();
  });

  it('keeps the note when there is too little history to plot', () => {
    // One month is a card, not a trend — but the prospect still has to be told
    // which benchmark counts, and a thin history is when that matters most.
    const [latest, ...pastMonths] = businessBreakdown[0].rows;
    const { container } = render(
      <DetailedEvaluation
        scoreBreakdown={[{
          ...businessBreakdown[0],
          rows: [latest, pastMonths.at(-1)!],
        }]}
      />,
    );

    expect(container.querySelector('.recharts-wrapper')).toBeNull();
    expect(screen.getByText('presentation.salesTrend.realBenchmark.note')).toBeInTheDocument();
  });

  it('renders no chart and no note for categories without sales rows', () => {
    const { container } = render(
      <DetailedEvaluation
        scoreBreakdown={[
          {
            category: 'Kesehatan Operasional Toko',
            score: 10,
            max_score: 10,
            rows: [
              {
                metric: 'Tingkat Konversi',
                value: 4,
                benchmark: '>3%',
                verdict: '✔️',
                message: '',
                score: 10,
              },
            ],
          },
        ]}
      />,
    );

    expect(container.querySelector('.recharts-wrapper')).toBeNull();
    expect(
      screen.queryByText('presentation.salesTrend.realBenchmark.note'),
    ).not.toBeInTheDocument();
  });
});
