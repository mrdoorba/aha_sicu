import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { EvaluationSections } from '../EvaluationSections';
import type { ManualData } from './formConfig';
import { EMPTY_MANUAL_DATA } from './formConfig';

// Mock FileUploadSection since it has its own hooks
vi.mock('../FileUploadSection', () => ({
  FileUploadSection: () => <div data-testid="file-upload-section">File Upload</div>,
}));

// Mock calculators to avoid QueryClient dependency from useCalculatorResults
vi.mock('../calculators', () => ({
  CalculatorResultsSection: () => <div data-testid="calculator-results">Calculator Results</div>,
}));

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

const defaultProps = {
  brandId: 1,
  categoryType: 'non_fashion' as string | null,
  onCategoryChange: vi.fn(),
  onActiveSection: vi.fn(),
  manualData: EMPTY_MANUAL_DATA,
  onFieldChange: vi.fn(),
  onFieldBlur: vi.fn(),
  saveStatus: 'idle' as const,
  lastSaved: null,
  onRetrySave: vi.fn(),
  storeName: 'Test Store',
  brandName: 'Test Brand',
  onGenerateScore: vi.fn(),
  scoringResult: null,
  isGenerating: false,
  isStale: false,
  scoringError: null,
  onSaveEvaluation: vi.fn(),
  isSaving: false,
  isSaved: false,
  saveError: null,
  onResetSave: vi.fn(),
};

const renderWithProviders = (props = {}) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <EvaluationSections {...defaultProps} {...props} />
    </QueryClientProvider>
  );
};

describe('EvaluationForms Integration', () => {
  it('renders form fields instead of placeholders in all sections', () => {
    renderWithProviders();

    // Section 1: Operational
    expect(screen.getByLabelText(/Pesanan Tidak Terselesaikan/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penilaian/)).toBeInTheDocument();

    // Section 2: Business, Content, Visitors
    expect(screen.getByLabelText(/Penjualan Bulan Ini/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Tingkat Konversi/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Perlu Ditingkatkan/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Total Pengunjung/)).toBeInTheDocument();

    // Section 3: Promo Tools, Products
    expect(screen.getByLabelText(/Promo Toko/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Jumlah Produk/)).toBeInTheDocument();

    // Section 5: Ads, Campaign, Competition
    expect(screen.getByLabelText(/Penjualan Iklan/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Sesi Dinominasikan/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Produk Kompetitor 1 — Keyword/)).toBeInTheDocument();

    // No placeholder text
    expect(screen.queryByText('Form fields will be added in Story 3.3')).not.toBeInTheDocument();
  });

  it('pre-fills forms when manual_data has saved values', () => {
    const savedData: ManualData = {
      ...EMPTY_MANUAL_DATA,
      operational: {
        unfulfilledOrderRate: 0.5,
        lateShipmentRate: 0.3,
        preparationTime: 0.8,
        chatResponseRate: 97,
        overallRating: 4.8,
      },
      business: {
        ...EMPTY_MANUAL_DATA.business,
        salesMonth0: 500000000,
        conversionRate: 3.5,
      },
      products: {
        productCount: 42,
        storeStatus: 'Shopee Mall',
      },
    };

    renderWithProviders({ manualData: savedData });

    // Operational pre-filled
    const opInputs = screen.getAllByRole('spinbutton');
    expect(opInputs[0]).toHaveValue(0.5);  // unfulfilledOrderRate

    // Products pre-filled
    expect(screen.getByText('Shopee Mall')).toBeInTheDocument();
  });

  it('calls onFieldChange when a field value changes', async () => {
    const onFieldChange = vi.fn();
    const user = userEvent.setup();
    renderWithProviders({ onFieldChange });

    const ratingInput = screen.getByLabelText(/Penilaian/);
    await user.type(ratingInput, '4');
    expect(onFieldChange).toHaveBeenCalledWith('operational', 'overallRating', 4);
  });

  it('calls onFieldBlur when a field loses focus', async () => {
    const onFieldBlur = vi.fn();
    const user = userEvent.setup();
    renderWithProviders({ onFieldBlur });

    const input = screen.getByLabelText(/Pesanan Tidak Terselesaikan/);
    await user.click(input);
    await user.tab();
    expect(onFieldBlur).toHaveBeenCalled();
  });

  it('renders save indicator when status is saving', () => {
    renderWithProviders({ saveStatus: 'saving' });
    expect(screen.getByText('Saving...')).toBeInTheDocument();
  });

  it('renders save indicator when status is saved', () => {
    renderWithProviders({ saveStatus: 'saved', lastSaved: new Date() });
    expect(screen.getByText('Saved just now')).toBeInTheDocument();
  });

  it('renders save error with retry button', async () => {
    const onRetry = vi.fn();
    const user = userEvent.setup();
    renderWithProviders({ saveStatus: 'error', onRetrySave: onRetry });

    expect(screen.getByText('Save failed.')).toBeInTheDocument();
    await user.click(screen.getByText('Retry'));
    expect(onRetry).toHaveBeenCalled();
  });

  it('keeps Section 4 file upload section intact', () => {
    renderWithProviders();
    expect(screen.getByTestId('file-upload-section')).toBeInTheDocument();
  });

  it('keeps calculator results and final score placeholders', () => {
    renderWithProviders();
    expect(screen.getByText('Calculator Results')).toBeInTheDocument();
    expect(screen.getByText('Final Score')).toBeInTheDocument();
  });
});
