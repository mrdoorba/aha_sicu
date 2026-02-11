import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { EvaluationPage } from './EvaluationPage';
import { EMPTY_MANUAL_DATA } from '../components/evaluation/forms/formConfig';

const mockUseBrandDetail = vi.fn();
const mockUseEvaluationState = vi.fn();
const mockUseSaveEvaluationInputs = vi.fn();
const mockUseAutoSaveForm = vi.fn();

vi.mock('../hooks/useBrandDetail', () => ({
  useBrandDetail: (...args: unknown[]) => mockUseBrandDetail(...args),
}));

vi.mock('../hooks/useEvaluation', () => ({
  useEvaluationState: (...args: unknown[]) => mockUseEvaluationState(...args),
  useSaveEvaluationInputs: (...args: unknown[]) => mockUseSaveEvaluationInputs(...args),
}));

vi.mock('../hooks/useAutoSaveForm', () => ({
  useAutoSaveForm: (...args: unknown[]) => mockUseAutoSaveForm(...args),
}));

vi.mock('../firebase/config', () => ({
  firebaseApp: {},
  firebaseAuth: {},
}));

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: { email: 'test@example.com' },
    logout: vi.fn(),
  }),
}));

vi.mock('../hooks/useSSE', () => ({
  useSSE: () => ({ connectionState: 'connected' }),
}));

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const SAMPLE_BRAND = {
  id: 1,
  brand_name: 'Test Brand',
  raw_data: { category: 'Electronics', marketplace: 'Shopee' },
  updated_at: '2026-02-05T10:00:00Z',
  meeting_raw_data: { notes: 'Good meeting' },
};

function setupMocks() {
  mockUseBrandDetail.mockReturnValue({
    data: SAMPLE_BRAND,
    isLoading: false,
    isError: false,
  });
  mockUseEvaluationState.mockReturnValue({
    data: { brand_id: 1, category_type: null, manual_data: null, updated_at: null },
  });
  mockUseSaveEvaluationInputs.mockReturnValue({
    mutate: vi.fn(),
  });
  mockUseAutoSaveForm.mockReturnValue({
    manualData: EMPTY_MANUAL_DATA,
    handleFieldChange: vi.fn(),
    triggerSave: vi.fn(),
    retrySave: vi.fn(),
    saveStatus: 'idle',
    lastSaved: null,
  });
}

const renderEvaluationPage = (brandId = '1') => {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[`/evaluation/${brandId}`]}>
        <Routes>
          <Route path="/evaluation/:brandId" element={<EvaluationPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('EvaluationPage', () => {
  it('renders brand name when data loaded', () => {
    setupMocks();
    renderEvaluationPage();
    expect(screen.getByText('Test Brand')).toBeInTheDocument();
  });

  it('renders all 5 section navigation items', () => {
    setupMocks();
    renderEvaluationPage();
    const nav = screen.getByRole('navigation', { name: /evaluation sections/i });
    expect(nav).toBeInTheDocument();
    const navButtons = nav.querySelectorAll('button');
    expect(navButtons).toHaveLength(5);
  });

  it('renders file upload slot placeholders', () => {
    setupMocks();
    renderEvaluationPage();
    expect(screen.getByText('CPC Ad Report')).toBeInTheDocument();
    expect(screen.getByText('Keyword Placement Report')).toBeInTheDocument();
    expect(screen.getByText('Order Export')).toBeInTheDocument();
    expect(screen.getByText('Mass Update / Sales Info')).toBeInTheDocument();
  });

  it('renders Fashion/Non-Fashion category selector', () => {
    setupMocks();
    renderEvaluationPage();
    expect(screen.getByText('Fashion')).toBeInTheDocument();
    expect(screen.getByText('Non-Fashion')).toBeInTheDocument();
  });

  it('renders score summary panel', () => {
    setupMocks();
    renderEvaluationPage();
    expect(screen.getByText('Score Summary')).toBeInTheDocument();
  });

  it('renders back to brands button', () => {
    setupMocks();
    renderEvaluationPage();
    expect(screen.getByRole('button', { name: /back to brands/i })).toBeInTheDocument();
  });

  it('renders manual data form sections instead of placeholders', () => {
    setupMocks();
    renderEvaluationPage();
    // Operational fields should be rendered (not placeholders)
    expect(screen.getByLabelText(/Pesanan Tidak Terselesaikan/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Chat Dibalas/)).toBeInTheDocument();
    // Business fields
    expect(screen.getByLabelText(/Penjualan Bulan Ini/)).toBeInTheDocument();
    // Promo fields
    expect(screen.getByLabelText(/Promo Toko/)).toBeInTheDocument();
    // No placeholders text
    expect(screen.queryByText('Form fields will be added in Story 3.3')).not.toBeInTheDocument();
  });
});
