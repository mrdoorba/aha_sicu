import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';

// Mock firebase auth
const mockGetCurrentUserToken = vi.fn();
vi.mock('../firebase/auth', () => ({
  getCurrentUserToken: () => mockGetCurrentUserToken(),
}));

// Mock EventSource
class MockEventSource {
  static instances: MockEventSource[] = [];
  url: string;
  onopen: (() => void) | null = null;
  onerror: (() => void) | null = null;
  listeners: Record<string, ((event: MessageEvent) => void)[]> = {};
  readyState = 0;

  constructor(url: string) {
    this.url = url;
    MockEventSource.instances.push(this);
  }

  addEventListener(event: string, handler: (event: MessageEvent) => void) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(handler);
  }

  close() {
    this.readyState = 2;
  }

  // Test helper: simulate event
  simulateEvent(eventName: string, data: string) {
    const handlers = this.listeners[eventName] || [];
    for (const handler of handlers) {
      handler(new MessageEvent(eventName, { data }));
    }
  }

  static reset() {
    MockEventSource.instances = [];
  }
}

vi.stubGlobal('EventSource', MockEventSource);

// Import after mocks are set up
import { useSSE } from './useSSE';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

describe('useSSE', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    MockEventSource.reset();
    mockGetCurrentUserToken.mockResolvedValue('test-token');
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it('starts in disconnected state and transitions to connecting', async () => {
    const { result } = renderHook(() => useSSE(), {
      wrapper: createWrapper(),
    });

    // Initially disconnected, then moves to connecting after token resolves
    expect(result.current.connectionState).toBe('disconnected');

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    expect(
      result.current.connectionState === 'connecting' ||
        result.current.connectionState === 'connected',
    ).toBe(true);
  });

  it('creates EventSource with correct URL and token', async () => {
    renderHook(() => useSSE(), { wrapper: createWrapper() });

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    expect(MockEventSource.instances.length).toBeGreaterThanOrEqual(1);
    const lastInstance =
      MockEventSource.instances[MockEventSource.instances.length - 1];
    expect(lastInstance.url).toContain('/api/v1/events?token=test-token');
  });

  it('transitions to connected on EventSource open', async () => {
    const { result } = renderHook(() => useSSE(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    const es =
      MockEventSource.instances[MockEventSource.instances.length - 1];

    await act(async () => {
      es.onopen?.();
    });

    expect(result.current.connectionState).toBe('connected');
  });

  it('does not connect when no token is available', async () => {
    mockGetCurrentUserToken.mockResolvedValue(null);

    const { result } = renderHook(() => useSSE(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    expect(result.current.connectionState).toBe('disconnected');
  });

  it('invalidates queries on sync_status event', async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

    const wrapper = ({ children }: { children: React.ReactNode }) =>
      React.createElement(
        QueryClientProvider,
        { client: queryClient },
        children,
      );

    renderHook(() => useSSE(), { wrapper });

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    const es =
      MockEventSource.instances[MockEventSource.instances.length - 1];

    await act(async () => {
      es.onopen?.();
      es.simulateEvent(
        'sync_status',
        JSON.stringify({ status: 'success', brands_synced: 150 }),
      );
    });

    expect(invalidateSpy).toHaveBeenCalledWith({
      queryKey: ['syncStatus'],
    });
    expect(invalidateSpy).toHaveBeenCalledWith({
      queryKey: ['brands'],
    });
  });

  it('transitions to failed after max retries', async () => {
    // Retry counting logic:
    //   onerror checks retryCount >= MAX_RETRIES(5) BEFORE incrementing.
    //   Errors 1-5: retryCount 0→4, each schedules reconnect (increments to 1→5).
    //   Error 6: retryCount=5, >= MAX_RETRIES, sets state to 'failed'.
    //   Total: 5 reconnect attempts + 1 final failure = 6 onerror calls.

    const { result } = renderHook(() => useSSE(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    // Errors 1-5: each triggers reconnect with backoff
    for (let i = 0; i < 5; i++) {
      const es =
        MockEventSource.instances[MockEventSource.instances.length - 1];

      await act(async () => {
        es.onerror?.();
        await vi.runAllTimersAsync();
      });
    }

    // Error 6: retryCount has reached MAX_RETRIES — should transition to 'failed'
    const es =
      MockEventSource.instances[MockEventSource.instances.length - 1];
    await act(async () => {
      es.onerror?.();
    });

    expect(result.current.connectionState).toBe('failed');
  });

  it('closes EventSource on unmount', async () => {
    const { unmount } = renderHook(() => useSSE(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await vi.runAllTimersAsync();
    });

    const es =
      MockEventSource.instances[MockEventSource.instances.length - 1];

    unmount();

    expect(es.readyState).toBe(2); // CLOSED
  });
});
