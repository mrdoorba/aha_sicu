import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { EvaluationPage } from './EvaluationPage';
import { EMPTY_MANUAL_DATA } from '../components/evaluation/forms/formConfig';

const mockUseBrandDetail = vi.fn();
const mockUseEvaluationState = vi.fn();
const mockUseSaveEvaluationInputs = vi.fn();
const mockUseAutoSaveForm = vi.fn();
const mockUseScoring = vi.fn();
const mockUseSaveEvaluation = vi.fn();
const mockUseCalculatorResults = vi.fn();

vi.mock('../hooks/useBrandDetail', () => ({
  useBrandDetail: (...args: unknown[]) => mockUseBrandDetail(...args),
}));

vi.mock('../hooks/useEvaluation', () => ({
  useEvaluationState: (...args: unknown[]) => mockUseEvaluationState(...args),
  useSaveEvaluationInputs: (...args: unknown[]) => mockUseSaveEvaluationInputs(...args),
}));

vi.mock('../hooks/useAutoSaveForm', () => ({
  useAutoSaveForm: (...args: unknown[]) => mockUseAutoSaveForm(...args),
}));

vi.mock('../hooks/useScoring', () => ({
  useScoring: (...args: unknown[]) => mockUseScoring(...args),
}));

vi.mock('../hooks/useSaveEvaluation', () => ({
  useSaveEvaluation: (...args: unknown[]) => mockUseSaveEvaluation(...args),
}));

vi.mock('../hooks/useCalculator', () => ({
  useCalculatorResults: (...args: unknown[]) => mockUseCalculatorResults(...args),
  useCalculatorStatus: () => ({ data: null }),
  useRunCalculator: () => ({ mutate: vi.fn(), isPending: false }),
  useRunAllCalculators: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock('../firebase/config', () => ({
  firebaseApp: {},
  firebaseAuth: {},
}));

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: { email: 'test@example.com' },
    logout: vi.fn(),
  }),
}));

vi.mock('../hooks/useSSE', () => ({
  useSSE: () => ({ connectionState: 'connected' }),
}));

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const SAMPLE_BRAND = {
  id: 1,
  brand_name: 'Test Brand',
  raw_data: { category: 'Electronics', marketplace: 'Shopee' },
  updated_at: '2026-02-05T10:00:00Z',
  meeting_raw_data: { notes: 'Good meeting' },
};

function setupMocks() {
  mockUseBrandDetail.mockReturnValue({
    data: SAMPLE_BRAND,
    isLoading: false,
    isError: false,
  });
  mockUseEvaluationState.mockReturnValue({
    data: { brand_id: 1, category_type: null, manual_data: null, updated_at: null },
  });
  mockUseSaveEvaluationInputs.mockReturnValue({
    mutate: vi.fn(),
  });
  mockUseAutoSaveForm.mockReturnValue({
    manualData: EMPTY_MANUAL_DATA,
    handleFieldChange: vi.fn(),
    triggerSave: vi.fn(),
    retrySave: vi.fn(),
    saveStatus: 'idle',
    lastSaved: null,
  });
  mockUseScoring.mockReturnValue({
    generateScore: vi.fn(),
    scoringResult: null,
    isStale: false,
    markStale: vi.fn(),
    isGenerating: false,
    error: null,
  });
  mockUseSaveEvaluation.mockReturnValue({
    saveEvaluation: vi.fn(),
    isSaving: false,
    isSaved: false,
    error: null,
    reset: vi.fn(),
  });
  mockUseCalculatorResults.mockReturnValue({
    data: { brand_id: 1, results: [] },
  });
}

const renderEvaluationPage = (brandId = '1') => {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[`/evaluation/${brandId}`]}>
        <Routes>
          <Route path="/evaluation/:brandId" element={<EvaluationPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('EvaluationPage', () => {
  it('renders brand name when data loaded', () => {
    setupMocks();
    renderEvaluationPage();
    expect(screen.getByText('Test Brand')).toBeInTheDocument();
  });

  it('renders all 6 section navigation items', () => {
    setupMocks();
    renderEvaluationPage();
    const nav = screen.getByRole('navigation', { name: /evaluation sections/i });
    expect(nav).toBeInTheDocument();
    const navButtons = nav.querySelectorAll('button');
    expect(navButtons).toHaveLength(6);
  });

  it('renders file upload slot placeholders', () => {
    setupMocks();
    renderEvaluationPage();
    expect(screen.getByText('CPC Ad Report')).toBeInTheDocument();
    expect(screen.getByText('Keyword Placement Report')).toBeInTheDocument();
    expect(screen.getByText('Order Export')).toBeInTheDocument();
    expect(screen.getByText('Mass Update / Sales Info')).toBeInTheDocument();
  });

  it('renders Fashion/Non-Fashion category selector', () => {
    setupMocks();
    renderEvaluationPage();
    expect(screen.getByText('Fashion')).toBeInTheDocument();
    expect(screen.getByText('Non-Fashion')).toBeInTheDocument();
  });

  it('renders score summary panel', () => {
    setupMocks();
    renderEvaluationPage();
    expect(screen.getByText('Score Summary')).toBeInTheDocument();
  });

  it('renders back to brands button', () => {
    setupMocks();
    renderEvaluationPage();
    expect(screen.getByRole('button', { name: /back to brands/i })).toBeInTheDocument();
  });

  it('renders manual data form sections instead of placeholders', () => {
    setupMocks();
    renderEvaluationPage();
    // Operational fields should be rendered (not placeholders)
    expect(screen.getByLabelText(/Pesanan Tidak Terselesaikan/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Chat Dibalas/)).toBeInTheDocument();
    // Business fields
    expect(screen.getByLabelText(/Penjualan Bulan Ini/)).toBeInTheDocument();
    // Promo fields
    expect(screen.getByLabelText(/Promo Toko/)).toBeInTheDocument();
    // No placeholders text
    expect(screen.queryByText('Form fields will be added in Story 3.3')).not.toBeInTheDocument();
  });

  it('assembles correct save payload from scoring and calculator data', async () => {
    setupMocks();

    const mockSaveEvaluation = vi.fn();
    mockUseScoring.mockReturnValue({
      generateScore: vi.fn(),
      scoringResult: {
        total_score: 75.5,
        category_scores: [
          { category: 'Operational', score: 8.0, max_score: 10.0, rows: [], available: true },
        ],
        verdict: '✔️',
        template: 'fashion',
        email_body: 'Dear Store,\nScore: 75.5',
        conclusion: 'Approved',
        marketing_estimation: '10%',
        marketing_percentage: '10%',
        marketing_budget: 'Rp 1.000.000',
        closing_message: 'Thank you',
        email_subject: 'Result',
        whatsapp_link: 'https://wa.me/',
        rule_version: 3,
      },
      isStale: false,
      markStale: vi.fn(),
      isGenerating: false,
      error: null,
    });

    mockUseCalculatorResults.mockReturnValue({
      data: {
        brand_id: 1,
        results: [
          { calculator_type: 'ads_keyword', output_text: 'Ads output', details: { keyword: 'test' }, calculated_at: '2026-02-11' },
          { calculator_type: 'discount', output_text: 'Disc output', details: { flag: false }, calculated_at: '2026-02-11' },
        ],
      },
    });

    mockUseSaveEvaluation.mockReturnValue({
      saveEvaluation: mockSaveEvaluation,
      isSaving: false,
      isSaved: false,
      error: null,
      reset: vi.fn(),
    });

    const user = userEvent.setup();
    renderEvaluationPage();

    const saveBtn = screen.getByRole('button', { name: /save evaluation/i });
    await user.click(saveBtn);

    expect(mockSaveEvaluation).toHaveBeenCalledOnce();
    const [payload] = mockSaveEvaluation.mock.calls[0];

    expect(payload).toEqual(expect.objectContaining({
      template: 'fashion',
      final_score: 75.5,
      verdict: '✔️',
      rule_version: 3,
      email_output: 'Dear Store,\nScore: 75.5',
    }));
    expect(payload.score_breakdown).toEqual([
      { category: 'Operational', score: 8.0, max_score: 10.0, rows: [], available: true },
    ]);
    expect(payload.calculator_results).toEqual({
      ads_keyword: { details: { keyword: 'test' }, output_text: 'Ads output' },
      discount: { details: { flag: false }, output_text: 'Disc output' },
    });
    expect(payload.manual_inputs).toEqual(EMPTY_MANUAL_DATA);
  });
});
