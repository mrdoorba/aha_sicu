import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ScorePanel } from './ScorePanel';
import type { ScoringResult } from '../../../hooks/useScoring';

const MOCK_RESULT: ScoringResult = {
  total_score: 75,
  category_scores: [
    { category: 'Kesehatan Operasional Toko', score: 5, max_score: 10, rows: [], available: true },
    { category: 'Bisnis Analisis', score: 10, max_score: 20, rows: [], available: true },
    { category: 'Skor Kesehatan Konten', score: 0, max_score: 0, rows: [], available: true },
    { category: 'Tinjauan Pengunjung', score: 3, max_score: 5, rows: [], available: true },
    { category: 'Promo Toko', score: 15, max_score: 15, rows: [], available: true },
    { category: 'Jumlah Produk & Status Toko', score: 15, max_score: 15, rows: [], available: true },
    { category: 'Data Iklan', score: 5, max_score: 10, rows: [], available: true },
    { category: 'Partisipasi Campaign', score: 10, max_score: 10, rows: [], available: true },
    { category: 'Kompetisi TOP Produk', score: 0, max_score: 0, rows: [], available: true },
    { category: 'Stok', score: -5, max_score: 10, rows: [], available: true },
    { category: 'Discount', score: 5, max_score: 5, rows: [], available: true },
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
  it('renders Ringkasan Skor heading', () => {
    render(<ScorePanel scoringResult={null} />);
    expect(screen.getByText('Ringkasan Skor')).toBeInTheDocument();
  });

  it('shows dashes when no result', () => {
    render(<ScorePanel scoringResult={null} />);
    expect(screen.getByText('Skor Total')).toBeInTheDocument();
    // All category rows should show em-dash
    const dashes = screen.getAllByText('\u2014');
    expect(dashes.length).toBeGreaterThanOrEqual(11); // 11 categories + total
  });

  it('shows total score when result exists', () => {
    render(<ScorePanel scoringResult={MOCK_RESULT} />);
    expect(screen.getByText('75')).toBeInTheDocument();
  });

  it('shows category scores from backend Indonesian names', () => {
    render(<ScorePanel scoringResult={MOCK_RESULT} />);
    // Multiple categories share the same score value (5 appears 3 times)
    expect(screen.getAllByText('5')).toHaveLength(3);     // Operational, Ads, Discount
    expect(screen.getAllByText('10')).toHaveLength(2);    // Business, Campaign
    expect(screen.getByText('3')).toBeInTheDocument();    // Visitors
    expect(screen.getByText('-5')).toBeInTheDocument();   // Stock (negative)
  });

  it('renders all category labels in Indonesian', () => {
    render(<ScorePanel scoringResult={null} />);
    expect(screen.getByText('Operasional')).toBeInTheDocument();
    expect(screen.getByText('Bisnis')).toBeInTheDocument();
    expect(screen.getByText('Konten')).toBeInTheDocument();
    expect(screen.getByText('Pengunjung')).toBeInTheDocument();
    expect(screen.getByText('Alat Promo')).toBeInTheDocument();
    expect(screen.getByText('Produk & Status')).toBeInTheDocument();
    expect(screen.getByText('Iklan')).toBeInTheDocument();
    expect(screen.getByText('Kampanye')).toBeInTheDocument();
    expect(screen.getByText('Kompetisi')).toBeInTheDocument();
    expect(screen.getByText('Stok')).toBeInTheDocument();
    expect(screen.getByText('Diskon')).toBeInTheDocument();
  });
});
