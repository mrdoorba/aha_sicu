import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { FinalScoreDisplay } from './FinalScoreDisplay';

describe('FinalScoreDisplay', () => {
  it('renders total score rounded', () => {
    render(<FinalScoreDisplay totalScore={82.7} verdict="✔️" template="fashion" />);
    expect(screen.getByText('83')).toBeInTheDocument();
    expect(screen.getByText('Total Score')).toBeInTheDocument();
  });

  it('shows Approved label for checkmark verdict', () => {
    render(<FinalScoreDisplay totalScore={80} verdict="✔️" template="fashion" />);
    expect(screen.getByText('Approved')).toBeInTheDocument();
  });

  it('shows Rejected label for cross verdict', () => {
    render(<FinalScoreDisplay totalScore={50} verdict="❌" template="non_fashion" />);
    expect(screen.getByText('Rejected')).toBeInTheDocument();
  });

  it('shows Special label for circle verdict', () => {
    render(<FinalScoreDisplay totalScore={60} verdict="⭕️" template="fashion" />);
    expect(screen.getByText('Special')).toBeInTheDocument();
  });

  it('shows Fashion badge for fashion template', () => {
    render(<FinalScoreDisplay totalScore={80} verdict="✔️" template="fashion" />);
    expect(screen.getByText('Fashion')).toBeInTheDocument();
  });

  it('shows Non-Fashion badge for non_fashion template', () => {
    render(<FinalScoreDisplay totalScore={80} verdict="✔️" template="non_fashion" />);
    expect(screen.getByText('Non-Fashion')).toBeInTheDocument();
  });

  it('falls back to No Verdict for unknown verdict', () => {
    render(<FinalScoreDisplay totalScore={0} verdict="unknown" template="fashion" />);
    expect(screen.getByText('No Verdict')).toBeInTheDocument();
  });
});
