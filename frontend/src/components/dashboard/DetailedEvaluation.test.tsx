import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { DetailedEvaluation } from './DetailedEvaluation';

const makeRow = (metric: string, verdict = '✔️') => ({
  metric,
  value: 100,
  benchmark: '>= 50',
  verdict,
  message: '',
  score: 10,
});

const scoreBreakdown = [
  {
    category: 'Data Iklan',
    score: 30,
    max_score: 40,
    rows: [
      makeRow('Penjualan'),
      makeRow('Biaya'),
      makeRow('ROI'),
      makeRow('Iklan check up', '❌'),
    ],
  },
];

describe('DetailedEvaluation', () => {
  it('filters out Iklan check up from metric cards', () => {
    render(<DetailedEvaluation scoreBreakdown={scoreBreakdown} />);
    expect(screen.getByText('Penjualan')).toBeInTheDocument();
    expect(screen.getByText('Biaya')).toBeInTheDocument();
    expect(screen.getByText('ROI')).toBeInTheDocument();
    expect(screen.queryByText('Iklan check up')).not.toBeInTheDocument();
  });

  it('shows fallback when all rows are filtered out', () => {
    const onlyIklan = [
      {
        category: 'Data Iklan',
        score: 0,
        max_score: 10,
        rows: [makeRow('Iklan check up')],
      },
    ];
    render(<DetailedEvaluation scoreBreakdown={onlyIklan} />);
    // Should show the "no metrics" fallback
    expect(screen.queryByText('Iklan check up')).not.toBeInTheDocument();
  });

  it('returns null when scoreBreakdown is empty', () => {
    const { container } = render(<DetailedEvaluation scoreBreakdown={[]} />);
    expect(container.innerHTML).toBe('');
  });
});
