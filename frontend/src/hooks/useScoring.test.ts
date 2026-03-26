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

import { useScoring } from './useScoring';

// ── Helpers ──────────────────────────────────────────────────────────────────

let queryClient: QueryClient;
const BRAND_ID = 1;

function createWrapper() {
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

const SCORING_REQUEST = {
  template: 'fashion' as const,
  verdict: '✔️',
  store_name: 'Test Store',
  period: 'Jan 2026',
  brand_name: 'Test',
};

const SCORING_RESPONSE = {
  total_score: 80,
  category_scores: [],
  verdict: '✔️',
  conclusion: '',
  marketing_estimation: '',
  marketing_percentage: '15%',
  marketing_budget: '',
  closing_message: '',
  email_subject: '',
  email_body: '',
  template: 'fashion',
  rule_version: 1,
};

// ── Tests ────────────────────────────────────────────────────────────────────

describe('useScoring – stale detection', () => {
  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    queryClient.clear();
  });

  it('should not be stale when preStep triggers delayed cache update after scoring completes', async () => {
    // Simulate the real scenario: preStep's onSuccess triggers invalidateQueries
    // which causes an async refetch that completes AFTER scoring onSuccess.
    const preStep = vi.fn(async () => {
      // Schedule a delayed cache update to simulate invalidateQueries refetch
      setTimeout(() => {
        queryClient.setQueryData(['calculatorResults', BRAND_ID], { results: [{ delayed: true }] });
      }, 20);
    });

    mockClientPOST.mockResolvedValue({ data: SCORING_RESPONSE, error: null });

    const { result } = renderHook(
      () => useScoring(BRAND_ID, preStep),
      { wrapper: createWrapper() },
    );

    // Generate score
    await act(async () => {
      result.current.generateScore(SCORING_REQUEST);
    });

    // At this point onSuccess has set isStale=false, but the delayed
    // cache update hasn't fired yet. Wait for it.
    await act(async () => {
      await new Promise((r) => setTimeout(r, 50));
    });

    expect(result.current.scoringResult).not.toBeNull();
    // BUG: this will be true because the delayed cache update triggers the
    // subscription after onSuccess already set isStale=false
    expect(result.current.isStale).toBe(false);
  });

  it('should be stale when calculatorResults changes after scoring completes from user edit', async () => {
    mockClientPOST.mockResolvedValue({ data: SCORING_RESPONSE, error: null });

    const { result } = renderHook(
      () => useScoring(BRAND_ID),
      { wrapper: createWrapper() },
    );

    // First, generate a score
    await act(async () => {
      result.current.generateScore(SCORING_REQUEST);
    });

    expect(result.current.scoringResult).not.toBeNull();
    expect(result.current.isStale).toBe(false);

    // Wait for the mutation suppression window (500ms) to expire
    await act(async () => {
      await new Promise((r) => setTimeout(r, 600));
    });

    // Now simulate external cache update (user edits data)
    await act(async () => {
      queryClient.setQueryData(['calculatorResults', BRAND_ID], { results: [{ changed: true }] });
    });

    await act(async () => {
      await new Promise((r) => setTimeout(r, 50));
    });

    expect(result.current.isStale).toBe(true);
  });
});
