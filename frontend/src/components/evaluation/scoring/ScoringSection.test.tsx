import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { ScoringSection } from './ScoringSection';
import { generatePeriodOptions } from './periodOptions';
import type { ScoringResult } from '../../../hooks/useScoring';

// EmailOutput (rendered when a scoringResult exists) re-renders per language via
// this query hook; mock it so these tests need no QueryClient/backend.
vi.mock('../../../hooks/usePreviewEmailTextFromResult', () => ({
  usePreviewEmailTextFromResult: () => ({ data: undefined }),
}));

const MOCK_RESULT: ScoringResult = {
  total_score: 82,
  category_scores: [
    { category: 'Operational', score: 5, max_score: 5, rows: [] },
  ],
  verdict: '✔️',
  conclusion: 'Store approved',
  marketing_estimation: '10%',
  marketing_percentage: '10%',
  marketing_budget: 'IDR 1,000,000',
  closing_message: 'Thank you',
  email_subject: 'Evaluation Result',
  email_body: 'Dear Store,\nScore: 82',
  template: 'fashion',
};

const defaultProps = {
  onGenerate: vi.fn(),
  scoringResult: null as ScoringResult | null,
  isGenerating: false,
  isStale: false,
  error: null as Error | null,
  categoryType: 'fashion' as string | null,
  storeName: 'Test Store',
  brandName: 'Test Brand',
};

describe('ScoringSection', () => {
  it('renders Hitung Skor button', () => {
    render(<ScoringSection {...defaultProps} />);
    expect(screen.getByRole('button', { name: /hitung skor/i })).toBeInTheDocument();
  });

  it('disables button when categoryType is null', () => {
    render(<ScoringSection {...defaultProps} categoryType={null} />);
    expect(screen.getByRole('button', { name: /hitung skor/i })).toBeDisabled();
  });

  it('shows category type prompt when null', () => {
    render(<ScoringSection {...defaultProps} categoryType={null} />);
    expect(screen.getByText(/pilih tipe kategori/i)).toBeInTheDocument();
  });

  it('calls onGenerate with correct params', async () => {
    const user = userEvent.setup();
    const onGenerate = vi.fn();
    render(<ScoringSection {...defaultProps} onGenerate={onGenerate} />);

    await user.click(screen.getByRole('button', { name: /hitung skor/i }));

    expect(onGenerate).toHaveBeenCalledWith({
      template: 'fashion',
      verdict: '✔️',
      store_name: 'Test Store',
      period: generatePeriodOptions()[0],
      brand_name: 'Test Brand',
    });
  });

  it('shows Hitung Ulang when result exists and not stale', () => {
    render(<ScoringSection {...defaultProps} scoringResult={MOCK_RESULT} />);
    expect(screen.getByRole('button', { name: /^hitung ulang$/i })).toBeInTheDocument();
  });

  it('shows stale warning when data changed', () => {
    render(<ScoringSection {...defaultProps} scoringResult={MOCK_RESULT} isStale />);
    expect(screen.getByText(/skor sudah tidak akurat/i)).toBeInTheDocument();
  });

  it('shows error message', () => {
    render(<ScoringSection {...defaultProps} error={new Error('Server error')} />);
    expect(screen.getByText(/server error/i)).toBeInTheDocument();
  });

  it('shows result sections when scoring exists', () => {
    render(<ScoringSection {...defaultProps} scoringResult={MOCK_RESULT} />);
    expect(screen.getByText('82')).toBeInTheDocument();
    expect(screen.getByText(/rincian per kategori/i)).toBeInTheDocument();
    expect(screen.getByText(/email output/i)).toBeInTheDocument();
  });

  it('should show recalculating label when scoringStep is recalculating', () => {
    render(
      <ScoringSection
        {...defaultProps}
        isGenerating
        scoringStep="recalculating"
      />,
    );
    expect(screen.getByText(/menghitung ulang data/i)).toBeInTheDocument();
  });

  it('should show scoring label when scoringStep is scoring', () => {
    render(
      <ScoringSection
        {...defaultProps}
        isGenerating
        scoringStep="scoring"
      />,
    );
    expect(screen.getByText(/menghitung skor/i)).toBeInTheDocument();
  });

  it('disables button while generating', () => {
    render(<ScoringSection {...defaultProps} isGenerating />);
    // Period is empty by default so button is disabled for multiple reasons,
    // but the button should still be in the DOM
    expect(screen.getByRole('button', { name: /hitung skor/i })).toBeDisabled();
  });

  it('auto-triggers onGenerate when verdict changes and scoringResult exists', async () => {
    const user = userEvent.setup();
    const onGenerate = vi.fn();
    render(
      <ScoringSection
        {...defaultProps}
        onGenerate={onGenerate}
        scoringResult={MOCK_RESULT}
      />,
    );

    // Find the verdict combobox (first one) and change it
    const comboboxes = screen.getAllByRole('combobox');
    await user.click(comboboxes[0]); // verdict selector
    await user.click(screen.getByText('❌ Ditolak'));

    await waitFor(() => {
      expect(onGenerate).toHaveBeenCalledWith(
        expect.objectContaining({ verdict: '❌' }),
      );
    });
  });

  it('does NOT auto-trigger onGenerate when scoringResult is null', () => {
    const onGenerate = vi.fn();
    // Render without scoringResult — dropdowns are not shown
    render(
      <ScoringSection
        {...defaultProps}
        onGenerate={onGenerate}
        scoringResult={null}
      />,
    );

    // Dropdowns should not be visible when scoringResult is null
    expect(screen.queryAllByRole('combobox')).toHaveLength(0);
    // onGenerate should not have been called by any auto-refresh
    expect(onGenerate).not.toHaveBeenCalled();
  });
});
