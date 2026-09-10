import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ScorePanel } from './ScorePanel';
import type { ScoringResult } from '../../../hooks/useScoring';

const MOCK_RESULT: ScoringResult = {
  total_score: 75,
  category_total: 75,
  vp_adjustment: 0,
  category_scores: [
    { category: 'Kesehatan Operasional Toko', score: 5, max_score: 10, rows: [], available: true },
    { category: 'Bisnis Analisis', score: 10, max_score: 20, rows: [], available: true },
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
    expect(dashes.length).toBeGreaterThanOrEqual(10); // 10 categories + total
  });

  it('shows total score when result exists', () => {
    // category_total differs from the total so the assertion names one element.
    render(
      <ScorePanel
        scoringResult={{ ...MOCK_RESULT, total_score: 75, category_total: 85, vp_adjustment: -10 }}
      />
    );
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
    expect(screen.getByText('Pengunjung')).toBeInTheDocument();
    expect(screen.getByText('Alat Promo')).toBeInTheDocument();
    expect(screen.getByText('Produk & Status')).toBeInTheDocument();
    expect(screen.getByText('Iklan')).toBeInTheDocument();
    expect(screen.getByText('Campaign')).toBeInTheDocument();
    expect(screen.getByText('Kompetisi')).toBeInTheDocument();
    expect(screen.getByText('Stok')).toBeInTheDocument();
    expect(screen.getByText('Diskon')).toBeInTheDocument();
  });

  it('shows the category total and a nil VP adjustment', () => {
    render(<ScorePanel scoringResult={MOCK_RESULT} />);

    expect(screen.getByText('Jumlah kategori')).toBeInTheDocument();
    expect(screen.getByText('Penyesuaian VP')).toBeInTheDocument();
  });

  it('shows the shortfall and its reason when VP misses the bar', () => {
    render(
      <ScorePanel
        scoringResult={{ ...MOCK_RESULT, total_score: 65, category_total: 75, vp_adjustment: -10 }}
        packageFit={{ package: 'Rising Star', vp: 65, bar: 80, adjustment: -10, met: false }}
      />
    );

    expect(screen.getByText('65')).toBeInTheDocument();          // total after the cut
    expect(screen.getByText('\u221210')).toBeInTheDocument();     // minus sign, not hyphen
    expect(
      screen.getByText('VP 65 di bawah ambang Rising Star (80).')
    ).toBeInTheDocument();
  });

  it('explains a met bar rather than leaving the nil adjustment bare', () => {
    render(
      <ScorePanel
        scoringResult={MOCK_RESULT}
        packageFit={{ package: 'New Star', vp: 65, bar: 65, adjustment: 0, met: true }}
      />
    );

    expect(
      screen.getByText('VP 65 memenuhi ambang New Star (65).')
    ).toBeInTheDocument();
  });

  it('says so when VP or package cannot be judged', () => {
    render(
      <ScorePanel
        scoringResult={MOCK_RESULT}
        packageFit={{ package: 'New Star', vp: null, bar: 65, adjustment: 0, met: null }}
      />
    );

    expect(
      screen.getByText('VP atau Package brand ini belum bisa dinilai — skor tidak disesuaikan.')
    ).toBeInTheDocument();
  });

  it('leaves the adjustment rows out entirely before a score exists', () => {
    render(<ScorePanel scoringResult={null} />);

    expect(screen.queryByText('Jumlah kategori')).not.toBeInTheDocument();
  });
});
