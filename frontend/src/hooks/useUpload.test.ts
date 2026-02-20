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
});
