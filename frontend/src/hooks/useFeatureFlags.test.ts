import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';

// -- Mocks --

const mockClientGET = vi.fn();

vi.mock('../services/apiClient', () => ({
  default: {
    GET: (...args: unknown[]) => mockClientGET(...args),
  },
}));

import { useFeatureFlags } from './useFeatureFlags';

// -- Helpers --

let queryClient: QueryClient;

function createWrapper() {
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

// -- Tests --

describe('useFeatureFlags', () => {
  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    queryClient.clear();
  });

  it('should return feature flags when fetch succeeds', async () => {
    mockClientGET.mockResolvedValue({
      data: { email_enabled: true },
      error: null,
    });

    const { result } = renderHook(() => useFeatureFlags(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual({ email_enabled: true });
    expect(mockClientGET).toHaveBeenCalledWith('/api/v1/config/features');
  });

  it('should return error when fetch fails', async () => {
    mockClientGET.mockResolvedValue({
      data: null,
      error: { detail: 'Server error' },
    });

    const { result } = renderHook(() => useFeatureFlags(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error?.message).toBe('Failed to fetch feature flags');
  });
});
