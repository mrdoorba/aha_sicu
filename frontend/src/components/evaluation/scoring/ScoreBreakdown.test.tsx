import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ScoreBreakdown } from './ScoreBreakdown';
import type { CategoryScore } from '../../../hooks/useScoring';

const SAMPLE_SCORES: CategoryScore[] = [
  {
    category: 'Operational',
    score: 5,
    max_score: 5,
    rows: [],
  },
  {
    category: 'Business',
    score: -3,
    max_score: 10,
    rows: [],
  },
];

describe('ScoreBreakdown', () => {
  it('renders category names', () => {
    render(<ScoreBreakdown categoryScores={SAMPLE_SCORES} />);
    expect(screen.getByText('Operational')).toBeInTheDocument();
    expect(screen.getByText('Business')).toBeInTheDocument();
  });

  it('renders score and max columns', () => {
    render(<ScoreBreakdown categoryScores={SAMPLE_SCORES} />);
    // Operational has score=5 and max=5, so "5" appears twice
    expect(screen.getAllByText('5')).toHaveLength(2);
    expect(screen.getByText('-3')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
  });

  it('renders table headers', () => {
    render(<ScoreBreakdown categoryScores={SAMPLE_SCORES} />);
    expect(screen.getByText('Category')).toBeInTheDocument();
    expect(screen.getByText('Score')).toBeInTheDocument();
    expect(screen.getByText('Max')).toBeInTheDocument();
  });

  it('filters out zero-score categories', () => {
    const scores: CategoryScore[] = [
      { category: 'Active', score: 5, max_score: 10, rows: [] },
      { category: 'Empty', score: 0, max_score: 0, rows: [] },
    ];
    render(<ScoreBreakdown categoryScores={scores} />);
    expect(screen.getByText('Active')).toBeInTheDocument();
    expect(screen.queryByText('Empty')).not.toBeInTheDocument();
  });
});
