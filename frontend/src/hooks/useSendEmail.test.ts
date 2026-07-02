import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';

// -- Mocks --

const mockClientPOST = vi.fn();

vi.mock('../services/apiClient', () => ({
  default: {
    POST: (...args: unknown[]) => mockClientPOST(...args),
  },
}));

import { useSendEmail } from './useSendEmail';

// -- Helpers --

let queryClient: QueryClient;

function createWrapper() {
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

const PARAMS = {
  evaluationId: 42,
  recipients: ['test@example.com'],
};

// -- Tests --

describe('useSendEmail', () => {
  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    queryClient.clear();
  });

  it('calls client.POST with correct path and body shape', async () => {
    mockClientPOST.mockResolvedValue({
      data: { success: true, message_id: 'msg-1', recipient: PARAMS.recipient },
      error: null,
    });

    const { result } = renderHook(() => useSendEmail(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync(PARAMS);
    });

    expect(mockClientPOST).toHaveBeenCalledWith('/api/v1/email/send', {
      body: {
        evaluation_id: 42,
        recipients: ['test@example.com'],
      },
    });
  });

  it('throws error when client returns error', async () => {
    mockClientPOST.mockResolvedValue({
      data: null,
      error: { detail: 'SMTP failure' },
    });

    const { result } = renderHook(() => useSendEmail(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      result.current.mutate(PARAMS);
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
      expect(result.current.error?.message).toBe('Failed to send email');
    });
  });

  it('returns data on success', async () => {
    const responseData = { success: true, message_id: 'msg-123', recipient: PARAMS.recipient };
    mockClientPOST.mockResolvedValue({ data: responseData, error: null });

    const { result } = renderHook(() => useSendEmail(), {
      wrapper: createWrapper(),
    });

    let returnedData: unknown;
    await act(async () => {
      returnedData = await result.current.mutateAsync(PARAMS);
    });

    expect(returnedData).toEqual(responseData);
  });
});
