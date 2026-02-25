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
    available: true,
  },
  {
    category: 'Business',
    score: -3,
    max_score: 10,
    rows: [],
    available: true,
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
    expect(screen.getByText('Kategori')).toBeInTheDocument();
    expect(screen.getByText('Skor')).toBeInTheDocument();
    expect(screen.getByText('Maks')).toBeInTheDocument();
  });

  it('filters out zero-score categories', () => {
    const scores: CategoryScore[] = [
      { category: 'Active', score: 5, max_score: 10, rows: [], available: true },
      { category: 'Empty', score: 0, max_score: 0, rows: [], available: true },
    ];
    render(<ScoreBreakdown categoryScores={scores} />);
    expect(screen.getByText('Active')).toBeInTheDocument();
    expect(screen.queryByText('Empty')).not.toBeInTheDocument();
  });

  it('applies destructive styling to negative scores', () => {
    render(<ScoreBreakdown categoryScores={SAMPLE_SCORES} />);
    const negativeCell = screen.getByText('-3');
    expect(negativeCell).toHaveClass('text-destructive');
    expect(negativeCell).toHaveClass('font-semibold');
  });

  it('does not apply destructive styling to positive scores', () => {
    render(<ScoreBreakdown categoryScores={SAMPLE_SCORES} />);
    // Get all cells with text "5" — score and max for Operational
    const fiveCells = screen.getAllByText('5');
    for (const cell of fiveCells) {
      expect(cell).not.toHaveClass('text-destructive');
    }
  });
});
