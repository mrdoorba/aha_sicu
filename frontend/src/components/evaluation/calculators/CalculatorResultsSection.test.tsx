import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const mockMutate = vi.fn();

vi.mock('../../../hooks/useCalculator', () => ({
  useCalculatorResults: vi.fn(),
  useCalculatorStatus: vi.fn(),
  useRunAllCalculators: vi.fn(() => ({
    mutate: mockMutate,
    isPending: false,
  })),
  useRunCalculator: vi.fn(() => ({
    mutate: vi.fn(),
    isPending: false,
    isError: false,
    error: null,
  })),
  useAutoCalcErrors: vi.fn(() => []),
}));

import { CalculatorResultsSection } from './CalculatorResultsSection';
import {
  useCalculatorResults,
  useCalculatorStatus,
  useRunCalculator,
  useAutoCalcErrors,
} from '../../../hooks/useCalculator';

const mockedUseResults = vi.mocked(useCalculatorResults);
const mockedUseStatus = vi.mocked(useCalculatorStatus);
const mockedUseRunCalculator = vi.mocked(useRunCalculator);
const mockedUseAutoCalcErrors = vi.mocked(useAutoCalcErrors);

function mockRunCalcResult(overrides: Partial<ReturnType<typeof useRunCalculator>> = {}): ReturnType<typeof useRunCalculator> {
  return {
    mutate: vi.fn(),
    mutateAsync: vi.fn(),
    isPending: false,
    isError: false,
    isIdle: true,
    isSuccess: false,
    error: null,
    data: undefined,
    reset: vi.fn(),
    status: 'idle',
    variables: undefined,
    failureCount: 0,
    failureReason: null,
    submittedAt: 0,
    context: undefined,
    ...overrides,
  };
}

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

const SAMPLE_RESULTS = {
  brand_id: 1,
  results: [
    {
      calculator_type: 'ads_keyword',
      output_text: '34 dari 80 produk (42.5%) sudah beriklan',
      details: {
        ak2: '34 dari 80 produk',
        ak3: '',
        ak4: '',
        al2: '', al3: '', al5: '', al6: '', al7: '', al8: '', al9: '',
        thresholds: { am6: 0, am7: 0, am9: 0, am10: 0 },
      },
      calculated_at: '2026-02-11T10:00:00Z',
    },
    {
      calculator_type: 'discount',
      output_text: '% Diskon TOP SKU: 2.7%',
      details: {
        discount_pct: '2.7%',
        range_min: '0.0%',
        range_max: '6.7%',
        voucher_pct: '0.3%',
        paket_pct: '0.0%',
        fake_discount_flag: false,
        product_summary: [],
        top_sku: [],
        totals: {},
      },
      calculated_at: '2026-02-11T10:30:00Z',
    },
  ],
};

const SAMPLE_STATUS = {
  brand_id: 1,
  calculators: {
    ads_keyword: {
      status: 'ready' as const,
      has_result: true,
      required_files: ['cpc_ad_report', 'keyword_report'],
      required_manual: [],
      available_files: ['cpc_ad_report', 'keyword_report'],
      missing_files: [],
      missing_manual: [],
      calculated_at: '2026-02-11T10:00:00Z',
    },
    discount: {
      status: 'ready' as const,
      has_result: true,
      required_files: ['order_export'],
      required_manual: [],
      available_files: ['order_export'],
      missing_files: [],
      missing_manual: [],
      calculated_at: '2026-02-11T10:30:00Z',
    },
    top_sku: {
      status: 'pending' as const,
      has_result: false,
      required_files: ['order_export', 'mass_update'],
      required_manual: [],
      available_files: ['order_export'],
      missing_files: ['mass_update'],
      missing_manual: [],
      calculated_at: null,
    },
  },
};

beforeEach(() => {
  vi.clearAllMocks();
});

describe('CalculatorResultsSection', () => {
  it('renders results when data available', () => {
    mockedUseResults.mockReturnValue({
      data: SAMPLE_RESULTS,
      isLoading: false,
    } as ReturnType<typeof useCalculatorResults>);
    mockedUseStatus.mockReturnValue({
      data: SAMPLE_STATUS,
      isLoading: false,
    } as ReturnType<typeof useCalculatorStatus>);

    render(<CalculatorResultsSection brandId={1} />, { wrapper: createWrapper() });

    expect(screen.getByText(/34 dari 80 produk/)).toBeInTheDocument();
    expect(screen.getByText('2.7%')).toBeInTheDocument();
  });

  it('shows pending state with missing files', () => {
    mockedUseResults.mockReturnValue({
      data: { brand_id: 1, results: [] },
      isLoading: false,
    } as ReturnType<typeof useCalculatorResults>);
    mockedUseStatus.mockReturnValue({
      data: SAMPLE_STATUS,
      isLoading: false,
    } as ReturnType<typeof useCalculatorStatus>);

    render(<CalculatorResultsSection brandId={1} />, { wrapper: createWrapper() });

    expect(screen.getByText('Menunggu:')).toBeInTheDocument();
    expect(screen.getByText('Mass Update / Sales Info (.xlsx)')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    mockedUseResults.mockReturnValue({
      data: undefined,
      isLoading: true,
    } as ReturnType<typeof useCalculatorResults>);
    mockedUseStatus.mockReturnValue({
      data: undefined,
      isLoading: true,
    } as ReturnType<typeof useCalculatorStatus>);

    render(<CalculatorResultsSection brandId={1} />, { wrapper: createWrapper() });

    expect(screen.getByText('Memuat hasil kalkulator...')).toBeInTheDocument();
  });

  it('recalculate all button triggers mutation', async () => {
    const user = userEvent.setup();

    mockedUseResults.mockReturnValue({
      data: SAMPLE_RESULTS,
      isLoading: false,
    } as ReturnType<typeof useCalculatorResults>);
    mockedUseStatus.mockReturnValue({
      data: SAMPLE_STATUS,
      isLoading: false,
    } as ReturnType<typeof useCalculatorStatus>);

    render(<CalculatorResultsSection brandId={1} />, { wrapper: createWrapper() });

    const recalcBtn = screen.getByText('Hitung Ulang Semua');
    await user.click(recalcBtn);

    expect(mockMutate).toHaveBeenCalledOnce();
  });

  it('shows Calculate button in ready-but-no-result state', async () => {
    const user = userEvent.setup();
    const mockCalcMutate = vi.fn();

    mockedUseRunCalculator.mockReturnValue(mockRunCalcResult({ mutate: mockCalcMutate }));

    // All calculators ready, no results
    const allReadyStatus = {
      brand_id: 1,
      calculators: {
        ads_keyword: { ...SAMPLE_STATUS.calculators.ads_keyword, has_result: false },
        discount: { ...SAMPLE_STATUS.calculators.discount, has_result: false },
        top_sku: { ...SAMPLE_STATUS.calculators.top_sku, status: 'ready' as const, missing_files: [] },
      },
    };

    mockedUseResults.mockReturnValue({
      data: { brand_id: 1, results: [] },
      isLoading: false,
    } as ReturnType<typeof useCalculatorResults>);
    mockedUseStatus.mockReturnValue({
      data: allReadyStatus,
      isLoading: false,
    } as ReturnType<typeof useCalculatorStatus>);

    render(<CalculatorResultsSection brandId={1} />, { wrapper: createWrapper() });

    // Should show Calculate buttons (one per ready card)
    const calcButtons = screen.getAllByText('Calculate');
    expect(calcButtons.length).toBe(3);

    await user.click(calcButtons[0]);
    expect(mockCalcMutate).toHaveBeenCalledOnce();

    // Should also show "Hitung Semua" (not "Hitung Ulang Semua")
    expect(screen.getByText('Hitung Semua')).toBeInTheDocument();
  });

  it('shows auto-calc error warning with Calculate button', async () => {
    const user = userEvent.setup();
    const mockCalcMutate = vi.fn();

    mockedUseRunCalculator.mockReturnValue(mockRunCalcResult({ mutate: mockCalcMutate }));

    mockedUseAutoCalcErrors.mockReturnValue([
      { calculator_type: 'ads_keyword', status: 'error', reason: 'Data validation failed' },
    ]);

    // ads_keyword ready but no result, discount has result
    mockedUseResults.mockReturnValue({
      data: {
        brand_id: 1,
        results: [SAMPLE_RESULTS.results[1]], // only discount
      },
      isLoading: false,
    } as ReturnType<typeof useCalculatorResults>);
    mockedUseStatus.mockReturnValue({
      data: SAMPLE_STATUS,
      isLoading: false,
    } as ReturnType<typeof useCalculatorStatus>);

    render(<CalculatorResultsSection brandId={1} />, { wrapper: createWrapper() });

    // Warning banner should be visible
    expect(screen.getByText(/Perhitungan otomatis gagal: Data validation failed/)).toBeInTheDocument();

    // Calculate button in the warning should be clickable
    const calcButtons = screen.getAllByText('Calculate');
    expect(calcButtons.length).toBeGreaterThanOrEqual(1);
    await user.click(calcButtons[0]);
    expect(mockCalcMutate).toHaveBeenCalledOnce();
  });

  it('shows loading state on Calculate button during calculation', () => {
    mockedUseRunCalculator.mockReturnValue(mockRunCalcResult({ isPending: true }));

    // All ready, no results
    const allReadyStatus = {
      brand_id: 1,
      calculators: {
        ads_keyword: { ...SAMPLE_STATUS.calculators.ads_keyword, has_result: false },
        discount: { ...SAMPLE_STATUS.calculators.discount, has_result: false },
        top_sku: { ...SAMPLE_STATUS.calculators.top_sku, status: 'ready' as const, missing_files: [] },
      },
    };

    mockedUseResults.mockReturnValue({
      data: { brand_id: 1, results: [] },
      isLoading: false,
    } as ReturnType<typeof useCalculatorResults>);
    mockedUseStatus.mockReturnValue({
      data: allReadyStatus,
      isLoading: false,
    } as ReturnType<typeof useCalculatorStatus>);

    render(<CalculatorResultsSection brandId={1} />, { wrapper: createWrapper() });

    // Calculate buttons should be disabled during loading
    const calcButtons = screen.getAllByText('Calculate');
    for (const btn of calcButtons) {
      expect(btn.closest('button')).toBeDisabled();
    }
  });

  it('shows error state with retry button when calculator fails', async () => {
    const user = userEvent.setup();
    const mockRetryMutate = vi.fn();

    // Make ads_keyword return error state
    mockedUseRunCalculator.mockImplementation((_brandId, calcType) => {
      if (calcType === 'ads_keyword') {
        return mockRunCalcResult({
          mutate: mockRetryMutate,
          isError: true,
          error: new Error('Calculator execution failed'),
        });
      }
      return mockRunCalcResult();
    });

    // No ads_keyword result (so error state shows instead of result)
    mockedUseResults.mockReturnValue({
      data: {
        brand_id: 1,
        results: [SAMPLE_RESULTS.results[1]], // only discount, no ads_keyword
      },
      isLoading: false,
    } as ReturnType<typeof useCalculatorResults>);
    mockedUseStatus.mockReturnValue({
      data: SAMPLE_STATUS,
      isLoading: false,
    } as ReturnType<typeof useCalculatorStatus>);

    render(<CalculatorResultsSection brandId={1} />, { wrapper: createWrapper() });

    // Error message should be visible
    expect(screen.getByText(/Calculator execution failed/)).toBeInTheDocument();

    // Retry button should be visible and functional
    const retryBtn = screen.getByText('Coba Lagi');
    expect(retryBtn).toBeInTheDocument();
    await user.click(retryBtn);

    expect(mockRetryMutate).toHaveBeenCalledOnce();
  });
});
