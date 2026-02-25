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
    expect(screen.getByText(/Dikirim ke: Calculator 1/)).toBeInTheDocument();
    expect(screen.getByText('Belum ada file diunggah')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /unggah file/i })).toBeInTheDocument();
  });

  it('renders uploaded state with filename, timestamp, row count', () => {
    renderSlot({ uploadInfo: SAMPLE_UPLOAD });

    expect(screen.getByText('File berhasil diunggah')).toBeInTheDocument();
    expect(screen.getByText('report.csv')).toBeInTheDocument();
    expect(screen.getByText(/500 baris/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /unggah ulang/i })).toBeInTheDocument();
  });

  it('renders error state with message', () => {
    renderSlot({
      uploadStatus: 'error',
      uploadError: 'Missing required columns',
    });

    expect(screen.getByText('Missing required columns')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /coba lagi/i })).toBeInTheDocument();
  });

  it('renders uploading state with progress', () => {
    renderSlot({ uploadStatus: 'uploading', uploadProgress: 45 });

    expect(screen.getByText(/Mengunggah… 45%/)).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders signing state', () => {
    renderSlot({ uploadStatus: 'signing' });

    expect(screen.getByText(/Menyiapkan unggahan/)).toBeInTheDocument();
  });

  it('renders processing state', () => {
    renderSlot({ uploadStatus: 'processing' });

    expect(screen.getByText(/Memproses file/)).toBeInTheDocument();
  });

  it('renders verifying state with spinner', () => {
    renderSlot({ uploadStatus: 'verifying' });

    expect(screen.getByText(/Memverifikasi unggahan/)).toBeInTheDocument();
    // Should NOT show error or uploading states
    expect(screen.queryByRole('button', { name: /coba lagi/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
  });

  it('has correct file input accept attribute', () => {
    renderSlot();

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    expect(input).toBeTruthy();
    expect(input.accept).toBe('.csv');
  });
});
