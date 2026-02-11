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
}));

import { CalculatorResultsSection } from './CalculatorResultsSection';
import {
  useCalculatorResults,
  useCalculatorStatus,
} from '../../../hooks/useCalculator';

const mockedUseResults = vi.mocked(useCalculatorResults);
const mockedUseStatus = vi.mocked(useCalculatorStatus);

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
      details: { ak2: 'text', thresholds: {} },
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

    expect(screen.getByText('Waiting for:')).toBeInTheDocument();
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

    expect(screen.getByText('Loading calculator results...')).toBeInTheDocument();
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

    const recalcBtn = screen.getByText('Recalculate All');
    await user.click(recalcBtn);

    expect(mockMutate).toHaveBeenCalledOnce();
  });
});
