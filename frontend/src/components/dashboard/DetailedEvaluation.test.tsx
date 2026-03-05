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
  it('renders all provided metric cards', () => {
    render(<DetailedEvaluation scoreBreakdown={scoreBreakdown} />);
    expect(screen.getByText('Penjualan')).toBeInTheDocument();
    expect(screen.getByText('Biaya')).toBeInTheDocument();
    expect(screen.getByText('ROI')).toBeInTheDocument();
    expect(screen.getByText('Iklan check up')).toBeInTheDocument();
  });

  it('shows fallback when there are no rows', () => {
    const emptyRows = [
      {
        category: 'Data Iklan',
        score: 0,
        max_score: 10,
        rows: [],
      },
    ];
    render(<DetailedEvaluation scoreBreakdown={emptyRows} />);
    // Should render without errors
    expect(screen.getByRole('tabpanel')).toBeInTheDocument();
  });

  it('returns null when scoreBreakdown is empty', () => {
    const { container } = render(<DetailedEvaluation scoreBreakdown={[]} />);
    expect(container.innerHTML).toBe('');
  });
});
