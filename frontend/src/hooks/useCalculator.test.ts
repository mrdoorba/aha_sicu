import { renderHook, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';

// ── Mocks ────────────────────────────────────────────────────────────────────

const mockClientPOST = vi.fn();

vi.mock('../services/apiClient', () => ({
  default: {
    POST: (...args: unknown[]) => mockClientPOST(...args),
    GET: vi.fn(),
  },
}));

import { useRunCalculator, type AutoCalcError } from './useCalculator';

// ── Helpers ──────────────────────────────────────────────────────────────────

let queryClient: QueryClient;
const BRAND_ID = 1;

function createWrapper() {
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

// ── Tests ────────────────────────────────────────────────────────────────────

describe('useRunCalculator – auto-calc error clearing', () => {
  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    queryClient.clear();
  });

  it('clears auto-calc error for the calculator type on successful run', async () => {
    // Pre-seed auto-calc errors for two calculator types
    const initialErrors: AutoCalcError[] = [
      { calculator_type: 'ads_keyword', status: 'error', reason: 'Data validation failed' },
      { calculator_type: 'discount', status: 'error', reason: 'Missing columns' },
    ];
    queryClient.setQueryData(['autoCalcErrors', BRAND_ID], initialErrors);

    // Mock successful calculator run
    mockClientPOST.mockResolvedValue({
      data: {
        calculator_type: 'ads_keyword',
        output_text: 'result',
        details: {},
        calculated_at: '2026-02-20T00:00:00Z',
      },
      error: null,
    });

    const { result } = renderHook(
      () => useRunCalculator(BRAND_ID, 'ads_keyword'),
      { wrapper: createWrapper() },
    );

    await act(async () => {
      await result.current.mutateAsync();
    });

    // ads_keyword error should be cleared, discount error should remain
    const remaining = queryClient.getQueryData<AutoCalcError[]>(['autoCalcErrors', BRAND_ID]);
    expect(remaining).toEqual([
      { calculator_type: 'discount', status: 'error', reason: 'Missing columns' },
    ]);
  });

  it('does not modify cache when no auto-calc error exists for the type', async () => {
    // Pre-seed error only for discount
    const initialErrors: AutoCalcError[] = [
      { calculator_type: 'discount', status: 'error', reason: 'Missing columns' },
    ];
    queryClient.setQueryData(['autoCalcErrors', BRAND_ID], initialErrors);

    mockClientPOST.mockResolvedValue({
      data: {
        calculator_type: 'ads_keyword',
        output_text: 'result',
        details: {},
        calculated_at: '2026-02-20T00:00:00Z',
      },
      error: null,
    });

    const { result } = renderHook(
      () => useRunCalculator(BRAND_ID, 'ads_keyword'),
      { wrapper: createWrapper() },
    );

    await act(async () => {
      await result.current.mutateAsync();
    });

    // discount error should remain untouched
    const remaining = queryClient.getQueryData<AutoCalcError[]>(['autoCalcErrors', BRAND_ID]);
    expect(remaining).toEqual(initialErrors);
  });
});
