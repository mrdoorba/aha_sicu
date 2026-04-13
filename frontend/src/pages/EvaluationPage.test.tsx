import { render, screen, within } from '@testing-library/react';
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
const mockUseBrandUploads = vi.fn();

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

vi.mock('../hooks/useUpload', () => ({
  useBrandUploads: (...args: unknown[]) => mockUseBrandUploads(...args),
  useUploadFile: () => ({
    upload: vi.fn(),
    progress: 0,
    status: 'idle',
    error: null,
    reset: vi.fn(),
  }),
  useDownloadFile: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}));

const mockUseRunAllCalculators = vi.fn();

vi.mock('../hooks/useCalculator', () => ({
  useCalculatorResults: (...args: unknown[]) => mockUseCalculatorResults(...args),
  useCalculatorStatus: () => ({ data: null }),
  useRunCalculator: () => ({ mutate: vi.fn(), isPending: false }),
  useRunAllCalculators: (...args: unknown[]) => mockUseRunAllCalculators(...args),
  useAutoCalcErrors: () => [],
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

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const SAMPLE_BRAND = {
  id: 1,
  brand_name: 'Test Brand',
  raw_data: { category: 'Electronics', marketplace: 'Shopee', 'Link Shopee': 'https://shopee.co.id/store' },
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
    lastPeriod: '',
    isStale: false,
    markStale: vi.fn(),
    isGenerating: false,
    scoringStep: 'idle',
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
  mockUseBrandUploads.mockReturnValue({
    data: { brand_id: 1, uploads: [] },
  });
  mockUseRunAllCalculators.mockReturnValue({
    mutate: vi.fn(),
    mutateAsync: vi.fn().mockResolvedValue({ results: [] }),
    isPending: false,
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

  it('shows step 4 partial progress based on uploaded files', () => {
    setupMocks();
    mockUseBrandUploads.mockReturnValue({
      data: {
        brand_id: 1,
        uploads: [
          { id: 1, file_type: 'cpc_ad_report', filename: 'ads.csv', file_size: 100, row_count: 10, uploaded_at: '2026-02-11T10:00:00Z' },
          { id: 2, file_type: 'order_export', filename: 'orders.xlsx', file_size: 100, row_count: 10, uploaded_at: '2026-02-11T10:00:00Z' },
        ],
      },
    });

    renderEvaluationPage();

    const step4Button = screen.getByRole('button', { name: /step 4\./i });
    expect(within(step4Button).getByText('2/4')).toBeInTheDocument();
  });

  it('shows step 4 green check when all required files are uploaded', () => {
    setupMocks();
    mockUseBrandUploads.mockReturnValue({
      data: {
        brand_id: 1,
        uploads: [
          { id: 1, file_type: 'cpc_ad_report', filename: 'ads.csv', file_size: 100, row_count: 10, uploaded_at: '2026-02-11T10:00:00Z' },
          { id: 2, file_type: 'keyword_report', filename: 'keywords.csv', file_size: 100, row_count: 10, uploaded_at: '2026-02-11T10:00:00Z' },
          { id: 3, file_type: 'order_export', filename: 'orders.xlsx', file_size: 100, row_count: 10, uploaded_at: '2026-02-11T10:00:00Z' },
          { id: 4, file_type: 'mass_update', filename: 'mass.xlsx', file_size: 100, row_count: 10, uploaded_at: '2026-02-11T10:00:00Z' },
        ],
      },
    });

    renderEvaluationPage();

    const step4Button = screen.getByRole('button', { name: /step 4\./i });
    expect(within(step4Button).getByLabelText('Complete')).toBeInTheDocument();
    expect(within(step4Button).queryByText('4/4')).not.toBeInTheDocument();
  });

  it('renders file upload slot placeholders', () => {
    setupMocks();
    renderEvaluationPage();
    expect(screen.getByText('Iklan Check Up V2A (Keseluruhan Iklan)')).toBeInTheDocument();
    expect(screen.getByText('Iklan Check Up V2B (Kata Pencarian)')).toBeInTheDocument();
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
    expect(screen.getByText('Ringkasan Skor')).toBeInTheDocument();
  });

  it('renders back to brands button', () => {
    setupMocks();
    renderEvaluationPage();
    expect(screen.getByRole('button', { name: /kembali ke brand/i })).toBeInTheDocument();
  });

  it('renders manual data form sections instead of placeholders', () => {
    setupMocks();
    renderEvaluationPage();
    // Operational fields (renamed)
    expect(screen.getByLabelText(/Tingkat Pesanan Tidak Terselesaikan/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Persentase Chat Dibalas/)).toBeInTheDocument();
    // Business fields (6 sales month fields)
    expect(screen.getAllByLabelText(/Penjualan Bulan/)).toHaveLength(6);
    // Promo fields (renamed with prefix)
    expect(screen.getByLabelText(/Penjualan dari Promo Toko/)).toBeInTheDocument();
    // No placeholders text
    expect(screen.queryByText('Form fields will be added in Story 3.3')).not.toBeInTheDocument();
  });

  it('assembles correct save payload from scoring and calculator data', async () => {
    setupMocks();

    const scoringData = {
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
      marketing_budget: 'IDR 1,000,000',
      closing_message: 'Thank you',
      email_subject: 'Result',
      rule_version: 3,
    };

    const mockSaveEvaluation = vi.fn((_payload, opts) => {
      opts?.onSuccess?.();
    });

    // Need category_type set for the chained save guard
    mockUseEvaluationState.mockReturnValue({
      data: { brand_id: 1, category_type: 'fashion', manual_data: null, updated_at: null },
    });

    // generateScore must invoke onSuccess with scoring data
    mockUseScoring.mockReturnValue({
      generateScore: vi.fn((_req, opts) => {
        opts?.onSuccess?.(scoringData);
      }),
      scoringResult: scoringData,
      lastPeriod: '',
      isStale: false,
      markStale: vi.fn(),
      isGenerating: false,
      scoringStep: 'idle',
      error: null,
    });

    // Seed calculator results into the query cache
    const calcResultsData = {
      brand_id: 1,
      results: [
        { calculator_type: 'ads_keyword', output_text: 'Ads output', details: { keyword: 'test' }, calculated_at: '2026-02-11' },
        { calculator_type: 'discount', output_text: 'Disc output', details: { flag: false }, calculated_at: '2026-02-11' },
      ],
    };
    mockUseCalculatorResults.mockReturnValue({ data: calcResultsData });
    queryClient.setQueryData(['calculatorResults', 1], calcResultsData);

    mockUseSaveEvaluation.mockReturnValue({
      saveEvaluation: mockSaveEvaluation,
      isSaving: false,
      isSaved: false,
      error: null,
      reset: vi.fn(),
    });

    const user = userEvent.setup();
    renderEvaluationPage();

    const saveBtn = screen.getByRole('button', { name: /simpan evaluasi/i });
    await user.click(saveBtn);

    // Wait for the chained async flow to complete
    await vi.waitFor(() => {
      expect(mockSaveEvaluation).toHaveBeenCalledOnce();
    });
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
      scoring_summary: {
        conclusion: 'Approved',
        marketing_estimation: '10%',
        marketing_budget: 'IDR 1,000,000',
        closing_message: 'Thank you',
      },
    });
    expect(payload.manual_inputs).toEqual(EMPTY_MANUAL_DATA);
  });

  it('should include scoring_summary in calculator_results when saving', async () => {
    setupMocks();

    const scoringData = {
      total_score: 60,
      category_scores: [],
      verdict: '❌',
      template: 'non_fashion',
      email_body: '',
      conclusion: '- Finding A\n- Finding B',
      marketing_estimation: '22.4% ~ 26.2%',
      marketing_percentage: '24%',
      marketing_budget: '',
      closing_message: '',
      email_subject: '',
      rule_version: 1,
    };

    const mockSaveEvaluation = vi.fn((_payload, opts) => {
      opts?.onSuccess?.();
    });

    // Need category_type set for the chained save guard
    mockUseEvaluationState.mockReturnValue({
      data: { brand_id: 1, category_type: 'non_fashion', manual_data: null, updated_at: null },
    });

    mockUseScoring.mockReturnValue({
      generateScore: vi.fn((_req, opts) => {
        opts?.onSuccess?.(scoringData);
      }),
      scoringResult: scoringData,
      lastPeriod: '',
      isStale: false,
      markStale: vi.fn(),
      isGenerating: false,
      scoringStep: 'idle',
      error: null,
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

    const saveBtn = screen.getByRole('button', { name: /simpan evaluasi/i });
    await user.click(saveBtn);

    await vi.waitFor(() => {
      expect(mockSaveEvaluation).toHaveBeenCalledOnce();
    });
    const [payload] = mockSaveEvaluation.mock.calls[0];
    expect(payload.calculator_results.scoring_summary).toEqual({
      conclusion: '- Finding A\n- Finding B',
      marketing_estimation: '22.4% ~ 26.2%',
      marketing_budget: '',
      closing_message: '',
    });
  });
});
