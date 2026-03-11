import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { EvaluationSections } from './EvaluationSections';
import { EMPTY_MANUAL_DATA } from './forms/formConfig';
import type { ScoringResult } from '../../hooks/useScoring';

// Mock heavy child components to isolate save button tests
vi.mock('./FileUploadSection', () => ({
  FileUploadSection: () => <div data-testid="file-upload-section">File Upload</div>,
}));

vi.mock('./calculators', () => ({
  CalculatorResultsSection: () => <div data-testid="calculator-results">Calculator Results</div>,
}));

vi.mock('../../firebase/config', () => ({
  firebaseApp: {},
  firebaseAuth: {},
}));

const MOCK_SCORING_RESULT: ScoringResult = {
  total_score: 82,
  category_scores: [
    { category: 'Operational', score: 5, max_score: 5, rows: [], available: true },
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

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const defaultProps = {
  brandId: 1,
  categoryType: 'fashion' as string | null,
  onCategoryChange: vi.fn(),
  onActiveSection: vi.fn(),
  manualData: EMPTY_MANUAL_DATA,
  onFieldChange: vi.fn(),
  onFieldBlur: vi.fn(),
  saveStatus: 'idle' as const,
  lastSaved: null,
  onRetrySave: vi.fn(),
  storeName: 'Test Store',
  brandName: 'Test Brand',
  onGenerateScore: vi.fn(),
  scoringResult: null as ScoringResult | null,
  isGenerating: false,
  isStale: false,
  scoringError: null as Error | null,
  onSaveEvaluation: vi.fn(),
  isSaving: false,
  isSaved: false,
  saveError: null as Error | null,
  onResetSave: vi.fn(),
};

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  );
}

describe('Save Evaluation Button', () => {
  it('is disabled when no category type', () => {
    renderWithProviders(<EvaluationSections {...defaultProps} categoryType={null} />);
    const saveBtn = screen.getByRole('button', { name: /simpan evaluasi/i });
    expect(saveBtn).toBeDisabled();
  });

  it('shows helper text when no category type', () => {
    renderWithProviders(<EvaluationSections {...defaultProps} categoryType={null} />);
    const matches = screen.getAllByText(/pilih tipe kategori/i);
    expect(matches.length).toBeGreaterThanOrEqual(1);
  });

  it('is enabled when scoring result available', () => {
    renderWithProviders(<EvaluationSections {...defaultProps} scoringResult={MOCK_SCORING_RESULT} />);
    const saveBtn = screen.getByRole('button', { name: /simpan evaluasi/i });
    expect(saveBtn).toBeEnabled();
  });

  it('shows loading state during save', () => {
    renderWithProviders(
      <EvaluationSections
        {...defaultProps}
        scoringResult={MOCK_SCORING_RESULT}
        isSaving={true}
      />,
    );
    const saveBtn = screen.getByRole('button', { name: /menyimpan/i });
    expect(saveBtn).toBeDisabled();
  });

  it('shows "Saved ✓" after successful save', () => {
    renderWithProviders(
      <EvaluationSections
        {...defaultProps}
        scoringResult={MOCK_SCORING_RESULT}
        isSaved={true}
      />,
    );
    const saveBtn = screen.getByRole('button', { name: /tersimpan ✓/i });
    expect(saveBtn).toBeDisabled();
  });

  it('shows error message on save failure', () => {
    renderWithProviders(
      <EvaluationSections
        {...defaultProps}
        scoringResult={MOCK_SCORING_RESULT}
        saveError={new Error('Network error')}
      />,
    );
    expect(screen.getByText(/gagal menyimpan evaluasi/i)).toBeInTheDocument();
  });

  it('calls onSaveEvaluation when clicked', async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();
    renderWithProviders(
      <EvaluationSections
        {...defaultProps}
        scoringResult={MOCK_SCORING_RESULT}
        onSaveEvaluation={onSave}
      />,
    );
    await user.click(screen.getByRole('button', { name: /simpan evaluasi/i }));
    expect(onSave).toHaveBeenCalledOnce();
  });
});
