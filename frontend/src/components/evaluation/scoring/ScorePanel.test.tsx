import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ScorePanel } from './ScorePanel';
import type { ScoringResult } from '../../../hooks/useScoring';

const MOCK_RESULT: ScoringResult = {
  total_score: 75,
  category_scores: [
    { category: 'Operational', score: 5, max_score: 5, rows: [] },
    { category: 'Business', score: 10, max_score: 15, rows: [] },
    { category: 'Content', score: 8, max_score: 10, rows: [] },
  ],
  verdict: '✔️',
  conclusion: '',
  marketing_estimation: '',
  marketing_percentage: '',
  marketing_budget: '',
  closing_message: '',
  email_subject: '',
  email_body: '',
  whatsapp_link: '',
  template: 'fashion',
};

describe('ScorePanel', () => {
  it('renders Score Summary heading', () => {
    render(<ScorePanel scoringResult={null} />);
    expect(screen.getByText('Score Summary')).toBeInTheDocument();
  });

  it('shows dashes when no result', () => {
    render(<ScorePanel scoringResult={null} />);
    expect(screen.getByText('Total Score')).toBeInTheDocument();
    // All category rows should show em-dash
    const dashes = screen.getAllByText('\u2014');
    expect(dashes.length).toBeGreaterThanOrEqual(11); // 11 categories + total
  });

  it('shows total score when result exists', () => {
    render(<ScorePanel scoringResult={MOCK_RESULT} />);
    expect(screen.getByText('75')).toBeInTheDocument();
  });

  it('shows category scores', () => {
    render(<ScorePanel scoringResult={MOCK_RESULT} />);
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument();
  });

  it('renders all category labels', () => {
    render(<ScorePanel scoringResult={null} />);
    expect(screen.getByText('Operational')).toBeInTheDocument();
    expect(screen.getByText('Business')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
    expect(screen.getByText('Visitors')).toBeInTheDocument();
    expect(screen.getByText('Promo Tools')).toBeInTheDocument();
    expect(screen.getByText('Products/Status')).toBeInTheDocument();
    expect(screen.getByText('Ads')).toBeInTheDocument();
    expect(screen.getByText('Campaign')).toBeInTheDocument();
    expect(screen.getByText('Competition')).toBeInTheDocument();
    expect(screen.getByText('Stock')).toBeInTheDocument();
    expect(screen.getByText('Discount')).toBeInTheDocument();
  });
});
