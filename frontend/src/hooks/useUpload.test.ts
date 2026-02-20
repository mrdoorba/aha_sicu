import { renderHook, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';

// ── Mocks ────────────────────────────────────────────────────────────────────

const mockClientPOST = vi.fn();
const mockClientGET = vi.fn();

vi.mock('../services/apiClient', () => ({
  default: {
    POST: (...args: unknown[]) => mockClientPOST(...args),
    GET: (...args: unknown[]) => mockClientGET(...args),
  },
}));

import { useUploadFile, type BrandUploads, type UploadInfo } from './useUpload';

// Mock XMLHttpRequest — resolves immediately with 200
class MockXHR {
  upload = { onprogress: null as ((e: ProgressEvent) => void) | null };
  onload: (() => void) | null = null;
  onerror: (() => void) | null = null;
  status = 200;

  open() {}
  setRequestHeader() {}
  send() {
    queueMicrotask(() => this.onload?.());
  }
}

// ── Test data ────────────────────────────────────────────────────────────────

const BRAND_ID = 1;
const FILE_TYPE = 'order_export';

const OLD_UPLOAD: UploadInfo = {
  id: 1,
  brand_id: BRAND_ID,
  file_type: FILE_TYPE,
  filename: 'old.zip',
  file_size: 1000,
  row_count: 100,
  uploaded_at: '2026-02-19T00:00:00Z',
};

const NEW_UPLOAD: UploadInfo = {
  id: 2,
  brand_id: BRAND_ID,
  file_type: FILE_TYPE,
  filename: 'new.zip',
  file_size: 2000,
  row_count: 200,
  uploaded_at: '2026-02-20T00:00:00Z',
};

const OLD_BRAND_UPLOADS: BrandUploads = { brand_id: BRAND_ID, uploads: [OLD_UPLOAD] };
const NEW_BRAND_UPLOADS: BrandUploads = { brand_id: BRAND_ID, uploads: [NEW_UPLOAD] };
const EMPTY_BRAND_UPLOADS: BrandUploads = { brand_id: BRAND_ID, uploads: [] };

// ── Helpers ──────────────────────────────────────────────────────────────────

let queryClient: QueryClient;

function createWrapper() {
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

function setupProcessError() {
  mockClientPOST.mockImplementation(async (path: string) => {
    if (path === '/api/v1/upload/signed-url') {
      return {
        data: { upload_url: 'http://mock-gcs/upload', upload_id: 'upload-123', expires_at: '' },
        error: null,
      };
    }
    if (path === '/api/v1/upload/process') {
      throw new Error('Processing timed out');
    }
    return { data: null, error: 'Unknown path' };
  });
}

// ── Tests ────────────────────────────────────────────────────────────────────

describe('useUploadFile – verification on error', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.stubGlobal('XMLHttpRequest', MockXHR);

    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    // Pre-populate cache with the "before upload" state
    queryClient.setQueryData(['brandUploads', BRAND_ID], OLD_BRAND_UPLOADS);
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    queryClient.clear();
  });

  it('transitions to done when immediate verification confirms success', async () => {
    setupProcessError();
    // Verification fetch returns new upload (changed filename + timestamp)
    mockClientGET.mockResolvedValue({ data: NEW_BRAND_UPLOADS, error: null });

    const { result } = renderHook(() => useUploadFile(BRAND_ID), { wrapper: createWrapper() });
    const file = new File(['data'], 'new.zip', { type: 'application/zip' });

    await act(async () => {
      await result.current.upload(file, FILE_TYPE).catch(() => {});
      await vi.runAllTimersAsync();
    });

    expect(result.current.status).toBe('done');
    expect(result.current.error).toBeNull();
    expect(result.current.progress).toBe(100);
  });

  it('transitions to done after poll detects upload success', async () => {
    setupProcessError();
    // Immediate check: still old data → poll
    // First poll retry: new data → success
    mockClientGET
      .mockResolvedValueOnce({ data: OLD_BRAND_UPLOADS, error: null })
      .mockResolvedValueOnce({ data: NEW_BRAND_UPLOADS, error: null });

    const { result } = renderHook(() => useUploadFile(BRAND_ID), { wrapper: createWrapper() });
    const file = new File(['data'], 'new.zip', { type: 'application/zip' });

    let uploadPromise: Promise<unknown>;
    act(() => {
      uploadPromise = result.current.upload(file, FILE_TYPE).catch(() => {});
    });

    // Advance through the signed URL, XHR, process error, immediate check, then first poll interval
    await act(async () => {
      await vi.advanceTimersByTimeAsync(5_000);
    });

    await act(async () => {
      await uploadPromise!;
    });

    expect(result.current.status).toBe('done');
    expect(result.current.error).toBeNull();
  });

  it('transitions to error after all verification retries fail', async () => {
    setupProcessError();
    // All verification fetches return old data (no change)
    mockClientGET.mockResolvedValue({ data: OLD_BRAND_UPLOADS, error: null });

    const { result } = renderHook(() => useUploadFile(BRAND_ID), { wrapper: createWrapper() });
    const file = new File(['data'], 'new.zip', { type: 'application/zip' });

    let uploadError: unknown;
    let uploadPromise: Promise<unknown>;
    act(() => {
      uploadPromise = result.current.upload(file, FILE_TYPE).catch((e) => { uploadError = e; });
    });

    // Advance through all 3 poll retries (5s each = 15s total)
    await act(async () => {
      await vi.advanceTimersByTimeAsync(20_000);
    });

    await act(async () => {
      await uploadPromise!;
    });

    expect(result.current.status).toBe('error');
    expect(result.current.error).toBe('Processing timed out');
    expect(uploadError).toBeInstanceOf(Error);
  });

  it('treats any new record as success when no prior upload exists (null snapshot)', async () => {
    // Start with empty cache — no prior upload for this file_type
    queryClient.setQueryData(['brandUploads', BRAND_ID], EMPTY_BRAND_UPLOADS);

    setupProcessError();
    // Verification fetch finds a new upload record
    mockClientGET.mockResolvedValue({ data: NEW_BRAND_UPLOADS, error: null });

    const { result } = renderHook(() => useUploadFile(BRAND_ID), { wrapper: createWrapper() });
    const file = new File(['data'], 'new.zip', { type: 'application/zip' });

    await act(async () => {
      await result.current.upload(file, FILE_TYPE).catch(() => {});
      await vi.runAllTimersAsync();
    });

    expect(result.current.status).toBe('done');
    expect(result.current.error).toBeNull();
  });

  it('cancels verification polling when a new upload is initiated', async () => {
    setupProcessError();
    // All verification fetches return old data so poll loop stays active
    mockClientGET.mockResolvedValue({ data: OLD_BRAND_UPLOADS, error: null });

    const { result } = renderHook(() => useUploadFile(BRAND_ID), { wrapper: createWrapper() });
    const file = new File(['data'], 'new.zip', { type: 'application/zip' });

    // Start first upload — will enter verifying state
    let firstPromise: Promise<unknown>;
    act(() => {
      firstPromise = result.current.upload(file, FILE_TYPE).catch(() => {});
    });

    // Advance past initial async work + one poll interval so we're mid-verification
    await act(async () => {
      await vi.advanceTimersByTimeAsync(5_000);
    });

    expect(result.current.status).toBe('verifying');

    // Now start a second upload — should abort the first verification
    // Make the second upload's process call succeed
    mockClientPOST.mockImplementation(async (path: string) => {
      if (path === '/api/v1/upload/signed-url') {
        return {
          data: { upload_url: 'http://mock-gcs/upload', upload_id: 'upload-456', expires_at: '' },
          error: null,
        };
      }
      if (path === '/api/v1/upload/process') {
        return { data: { upload: NEW_UPLOAD, auto_calculated: [] }, error: null };
      }
      return { data: null, error: 'Unknown path' };
    });

    await act(async () => {
      await result.current.upload(file, FILE_TYPE);
      await vi.runAllTimersAsync();
    });

    // First promise should have resolved silently (aborted)
    await act(async () => {
      await firstPromise!;
    });

    // Second upload succeeded normally
    expect(result.current.status).toBe('done');
    expect(result.current.error).toBeNull();
  });

  it('aborts verification polling on unmount', async () => {
    setupProcessError();
    mockClientGET.mockResolvedValue({ data: OLD_BRAND_UPLOADS, error: null });

    const { result, unmount } = renderHook(() => useUploadFile(BRAND_ID), { wrapper: createWrapper() });
    const file = new File(['data'], 'new.zip', { type: 'application/zip' });

    let uploadPromise: Promise<unknown>;
    act(() => {
      uploadPromise = result.current.upload(file, FILE_TYPE).catch(() => {});
    });

    // Advance past initial async work so we're in verifying state
    await act(async () => {
      await vi.advanceTimersByTimeAsync(5_000);
    });

    // Record how many GET calls have been made so far
    const callsBefore = mockClientGET.mock.calls.length;

    // Unmount — should abort polling
    unmount();

    // Advance timers past the remaining poll intervals
    await act(async () => {
      await vi.advanceTimersByTimeAsync(15_000);
    });

    await act(async () => {
      await uploadPromise!;
    });

    // No additional GET calls should have been made after unmount
    expect(mockClientGET.mock.calls.length).toBe(callsBefore);
  });
});
