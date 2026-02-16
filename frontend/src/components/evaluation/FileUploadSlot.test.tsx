import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { FileUploadSlot, type FileSlotConfig } from './FileUploadSlot';
import type { UploadInfo, UploadStatus } from '../../hooks/useUpload';

const CONFIG: FileSlotConfig = {
  label: 'Iklan Check Up V2A',
  fileType: 'cpc_ad_report',
  accept: '.csv',
  format: '.csv',
  calculator: 'Calculator 1 (Ads Keyword — Sheet 1)',
};

const SAMPLE_UPLOAD: UploadInfo = {
  id: 1,
  file_type: 'cpc_ad_report',
  filename: 'report.csv',
  file_size: 1024,
  row_count: 500,
  uploaded_at: '2026-02-11T10:00:00Z',
};

const noop = () => {};

function renderSlot(overrides: {
  uploadInfo?: UploadInfo | null;
  uploadStatus?: UploadStatus;
  uploadProgress?: number;
  uploadError?: string | null;
} = {}) {
  return render(
    <FileUploadSlot
      config={CONFIG}
      uploadInfo={overrides.uploadInfo ?? null}
      uploadStatus={overrides.uploadStatus ?? 'idle'}
      uploadProgress={overrides.uploadProgress ?? 0}
      uploadError={overrides.uploadError ?? null}
      onFileSelect={noop}
      onReset={noop}
    />
  );
}

describe('FileUploadSlot', () => {
  it('renders empty state with upload button', () => {
    renderSlot();

    expect(screen.getByText('Iklan Check Up V2A')).toBeInTheDocument();
    expect(screen.getByText(/Format: .csv/)).toBeInTheDocument();
    expect(screen.getByText(/Routes to: Calculator 1/)).toBeInTheDocument();
    expect(screen.getByText('No file uploaded')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /upload file/i })).toBeInTheDocument();
  });

  it('renders uploaded state with filename, timestamp, row count', () => {
    renderSlot({ uploadInfo: SAMPLE_UPLOAD });

    expect(screen.getByText('File uploaded successfully')).toBeInTheDocument();
    expect(screen.getByText('report.csv')).toBeInTheDocument();
    expect(screen.getByText(/500 rows/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /re-upload/i })).toBeInTheDocument();
  });

  it('renders error state with message', () => {
    renderSlot({
      uploadStatus: 'error',
      uploadError: 'Missing required columns',
    });

    expect(screen.getByText('Missing required columns')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('renders uploading state with progress', () => {
    renderSlot({ uploadStatus: 'uploading', uploadProgress: 45 });

    expect(screen.getByText(/Uploading… 45%/)).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders signing state', () => {
    renderSlot({ uploadStatus: 'signing' });

    expect(screen.getByText(/Preparing upload/)).toBeInTheDocument();
  });

  it('renders processing state', () => {
    renderSlot({ uploadStatus: 'processing' });

    expect(screen.getByText(/Processing file/)).toBeInTheDocument();
  });

  it('has correct file input accept attribute', () => {
    renderSlot();

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    expect(input).toBeTruthy();
    expect(input.accept).toBe('.csv');
  });
});
