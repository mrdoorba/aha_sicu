import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock the hooks before importing the component
vi.mock('../../hooks/useUpload', () => ({
  useBrandUploads: vi.fn(() => ({ data: { brand_id: 1, uploads: [] } })),
  useUploadFile: vi.fn(() => ({
    upload: vi.fn(),
    progress: 0,
    status: 'idle',
    error: null,
    reset: vi.fn(),
  })),
}));

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

import { FileUploadSection } from './FileUploadSection';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

describe('FileUploadSection', () => {
  it('renders 4 upload slots with correct labels', () => {
    render(<FileUploadSection brandId={1} />, { wrapper: createWrapper() });

    expect(screen.getByText('CPC Ad Report')).toBeInTheDocument();
    expect(screen.getByText('Keyword Placement Report')).toBeInTheDocument();
    expect(screen.getByText('Order Export')).toBeInTheDocument();
    expect(screen.getByText('Mass Update / Sales Info')).toBeInTheDocument();
  });

  it('renders correct formats for each slot', () => {
    render(<FileUploadSection brandId={1} />, { wrapper: createWrapper() });

    const formatTexts = screen.getAllByText(/Format:/);
    expect(formatTexts.length).toBe(4);
  });

  it('renders file inputs with correct accept attributes', () => {
    render(<FileUploadSection brandId={1} />, { wrapper: createWrapper() });

    const inputs = document.querySelectorAll('input[type="file"]');
    expect(inputs.length).toBe(4);

    // CSV slots
    const csvInputs = Array.from(inputs).filter(
      (i) => (i as HTMLInputElement).accept === '.csv'
    );
    expect(csvInputs.length).toBe(2);

    // Excel+ZIP slots
    const excelInputs = Array.from(inputs).filter(
      (i) => (i as HTMLInputElement).accept === '.xlsx,.zip'
    );
    expect(excelInputs.length).toBe(2);
  });
});
