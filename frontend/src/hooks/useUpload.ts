import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useCallback, useRef, useEffect } from 'react';
import client from '../services/apiClient';

export interface UploadInfo {
  id: number;
  brand_id: number;
  file_type: string;
  filename: string;
  file_size: number;
  row_count: number;
  uploaded_at: string;
}

export interface BrandUploads {
  brand_id: number;
  uploads: UploadInfo[];
}

export function useBrandUploads(brandId: number) {
  return useQuery<BrandUploads>({
    queryKey: ['brandUploads', brandId],
    queryFn: async () => {
      const { data, error } = await client.GET(
        '/api/v1/upload/brands/{brand_id}',
        { params: { path: { brand_id: brandId } } },
      );
      if (error) throw new Error('Failed to fetch brand uploads');
      return data as BrandUploads;
    },
    enabled: brandId > 0,
  });
}

export function useRequestSignedUrl() {
  return useMutation({
    mutationFn: async (body: {
      filename: string;
      content_type: string;
      file_type: string;
      brand_id: number;
    }) => {
      const { data, error } = await client.POST('/api/v1/upload/signed-url', {
        body,
      });
      if (error) {
        const detail = (error as Record<string, unknown>).detail;
        throw new Error(typeof detail === 'string' ? detail : 'Failed to get signed URL');
      }
      return data as { upload_url: string; upload_id: string; expires_at: string };
    },
  });
}

export interface AutoCalculatedItem {
  calculator_type: string;
  status: 'success' | 'skipped' | 'error';
  result?: Record<string, unknown>;
  reason?: string;
}

export interface ProcessUploadResponse {
  upload: UploadInfo;
  auto_calculated: AutoCalculatedItem[];
}

const PROCESS_TIMEOUT_MS = 120_000;

export function useProcessUpload() {
  return useMutation({
    mutationFn: async (body: {
      upload_id: string;
      brand_id: number;
      file_type: string;
    }) => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), PROCESS_TIMEOUT_MS);

      try {
        const { data, error } = await client.POST('/api/v1/upload/process', {
          body,
          signal: controller.signal,
        });
        if (error) {
          const detail = (error as Record<string, unknown>).detail;
          throw new Error(typeof detail === 'string' ? detail : 'Failed to process upload');
        }
        return data as ProcessUploadResponse;
      } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') {
          throw new Error(
            'Processing timed out. The file may be too large \u2014 try splitting it into smaller parts.',
          );
        }
        throw err;
      } finally {
        clearTimeout(timeoutId);
      }
    },
  });
}

export type UploadStatus = 'idle' | 'signing' | 'uploading' | 'processing' | 'verifying' | 'done' | 'error';

interface UploadSnapshot {
  filename: string;
  uploaded_at: string;
}

const VERIFY_POLL_INTERVAL_MS = 5_000;
const VERIFY_MAX_RETRIES = 3;

export function useUploadFile(brandId: number) {
  const queryClient = useQueryClient();
  const requestSignedUrl = useRequestSignedUrl();
  const processUpload = useProcessUpload();
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<UploadStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const verifyAbortRef = useRef<AbortController | null>(null);

  const getUploadSnapshot = useCallback(
    (fileType: string): UploadSnapshot | null => {
      const cached = queryClient.getQueryData<BrandUploads>(['brandUploads', brandId]);
      const record = cached?.uploads.find((u) => u.file_type === fileType);
      if (!record) return null;
      return { filename: record.filename, uploaded_at: record.uploaded_at };
    },
    [queryClient, brandId],
  );

  const checkUploadChanged = useCallback(
    async (fileType: string, snapshot: UploadSnapshot | null): Promise<boolean> => {
      await queryClient.invalidateQueries({ queryKey: ['brandUploads', brandId] });
      const fresh = await queryClient.fetchQuery<BrandUploads>({
        queryKey: ['brandUploads', brandId],
        queryFn: async () => {
          const { data, error } = await client.GET(
            '/api/v1/upload/brands/{brand_id}',
            { params: { path: { brand_id: brandId } } },
          );
          if (error) throw new Error('Failed to fetch brand uploads');
          return data as BrandUploads;
        },
        staleTime: 0,
      });
      const record = fresh?.uploads.find((u) => u.file_type === fileType);
      if (!snapshot) return !!record;
      if (!record) return false;
      return record.filename !== snapshot.filename || record.uploaded_at !== snapshot.uploaded_at;
    },
    [queryClient, brandId],
  );

  const verifyUpload = useCallback(
    async (fileType: string, snapshot: UploadSnapshot | null, signal: AbortSignal): Promise<boolean> => {
      // Immediate check
      if (await checkUploadChanged(fileType, snapshot)) return true;

      // Short poll loop
      for (let i = 0; i < VERIFY_MAX_RETRIES; i++) {
        if (signal.aborted) return false;
        await new Promise<void>((resolve) => {
          const timer = setTimeout(resolve, VERIFY_POLL_INTERVAL_MS);
          signal.addEventListener('abort', () => { clearTimeout(timer); resolve(); }, { once: true });
        });
        if (signal.aborted) return false;
        if (await checkUploadChanged(fileType, snapshot)) return true;
      }

      return false;
    },
    [checkUploadChanged],
  );

  const upload = useCallback(
    async (file: File, fileType: string) => {
      // Cancel any in-flight verification from a previous attempt
      verifyAbortRef.current?.abort();
      verifyAbortRef.current = null;

      setProgress(0);
      setStatus('signing');
      setError(null);

      // 0. Snapshot current upload state for post-error verification
      const snapshot = getUploadSnapshot(fileType);

      try {
        // 1. Request signed URL
        const signedData = await requestSignedUrl.mutateAsync({
          filename: file.name,
          content_type: file.type || 'application/octet-stream',
          file_type: fileType,
          brand_id: brandId,
        });

        // 2. Upload file directly to GCS (or local endpoint) via XHR for progress
        setStatus('uploading');
        await new Promise<void>((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
              setProgress(Math.round((e.loaded / e.total) * 100));
            }
          };
          xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              resolve();
            } else {
              reject(new Error(`Upload failed with status ${xhr.status}`));
            }
          };
          xhr.onerror = () => reject(new Error('Upload network error'));
          xhr.open('PUT', signedData.upload_url);
          xhr.setRequestHeader('Content-Type', file.type || 'application/octet-stream');
          xhr.send(file);
        });

        // 3. Trigger processing
        setStatus('processing');
        const result = await processUpload.mutateAsync({
          upload_id: signedData.upload_id,
          brand_id: brandId,
          file_type: fileType,
        });

        // 4. Invalidate query caches (uploads + calculator results/status if auto-calculated)
        queryClient.invalidateQueries({ queryKey: ['brandUploads', brandId] });
        if (result.auto_calculated && result.auto_calculated.length > 0) {
          queryClient.invalidateQueries({ queryKey: ['calculatorResults', brandId] });
          queryClient.invalidateQueries({ queryKey: ['calculatorStatus', brandId] });
        }

        setStatus('done');
        setProgress(100);
        return result;
      } catch (err) {
        // Attempt verification before showing error
        const abortController = new AbortController();
        verifyAbortRef.current = abortController;
        setStatus('verifying');

        try {
          const uploadSucceeded = await verifyUpload(fileType, snapshot, abortController.signal);

          if (abortController.signal.aborted) return;

          if (uploadSucceeded) {
            queryClient.invalidateQueries({ queryKey: ['brandUploads', brandId] });
            queryClient.invalidateQueries({ queryKey: ['calculatorResults', brandId] });
            queryClient.invalidateQueries({ queryKey: ['calculatorStatus', brandId] });
            setStatus('done');
            setProgress(100);
            return;
          }
        } catch {
          // Verification itself failed — fall through to error state
        }

        if (abortController.signal.aborted) return;

        let message = 'Upload failed';
        if (err instanceof Error) {
          const detail = (err as unknown as Record<string, unknown>).detail;
          message = typeof detail === 'string' ? detail : err.message;
        }
        setError(message);
        setStatus('error');
        throw err;
      }
    },
    [brandId, requestSignedUrl, processUpload, queryClient, getUploadSnapshot, verifyUpload],
  );

  // Abort verification polling on unmount
  useEffect(() => {
    return () => {
      verifyAbortRef.current?.abort();
    };
  }, []);

  const reset = useCallback(() => {
    verifyAbortRef.current?.abort();
    verifyAbortRef.current = null;
    setProgress(0);
    setStatus('idle');
    setError(null);
  }, []);

  return { upload, progress, status, error, reset };
}
