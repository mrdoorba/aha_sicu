import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { FinalScoreDisplay } from './FinalScoreDisplay';

describe('FinalScoreDisplay', () => {
  it('renders total score rounded', () => {
    render(<FinalScoreDisplay totalScore={82.7} verdict="✔️" template="fashion" />);
    expect(screen.getByText('83')).toBeInTheDocument();
    expect(screen.getByText('Skor Total')).toBeInTheDocument();
  });

  it('shows Disetujui label for checkmark verdict', () => {
    render(<FinalScoreDisplay totalScore={80} verdict="✔️" template="fashion" />);
    expect(screen.getByText('Disetujui')).toBeInTheDocument();
  });

  it('shows Ditolak label for cross verdict', () => {
    render(<FinalScoreDisplay totalScore={50} verdict="❌" template="non_fashion" />);
    expect(screen.getByText('Ditolak')).toBeInTheDocument();
  });

  it('shows score and verdict for fashion template', () => {
    render(<FinalScoreDisplay totalScore={80} verdict="✔️" template="fashion" />);
    expect(screen.getByText('80')).toBeInTheDocument();
    expect(screen.getByText('Disetujui')).toBeInTheDocument();
  });

  it('shows score and verdict for non_fashion template', () => {
    render(<FinalScoreDisplay totalScore={80} verdict="✔️" template="non_fashion" />);
    expect(screen.getByText('80')).toBeInTheDocument();
    expect(screen.getByText('Disetujui')).toBeInTheDocument();
  });

  it('shows Stok label for stock verdict', () => {
    render(<FinalScoreDisplay totalScore={50} verdict="❌ Stock" template="fashion" />);
    expect(screen.getByText('Stok')).toBeInTheDocument();
  });

  it('falls back to Tanpa Keputusan for unknown verdict', () => {
    render(<FinalScoreDisplay totalScore={0} verdict="unknown" template="fashion" />);
    expect(screen.getByText('Tanpa Keputusan')).toBeInTheDocument();
  });
});
