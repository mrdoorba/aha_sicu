import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { EvaluationPage } from './EvaluationPage';

const mockUseBrandDetail = vi.fn();
const mockUseEvaluationState = vi.fn();
const mockUseSaveEvaluationInputs = vi.fn();

vi.mock('../hooks/useBrandDetail', () => ({
  useBrandDetail: (...args: unknown[]) => mockUseBrandDetail(...args),
}));

vi.mock('../hooks/useEvaluation', () => ({
  useEvaluationState: (...args: unknown[]) => mockUseEvaluationState(...args),
  useSaveEvaluationInputs: (...args: unknown[]) => mockUseSaveEvaluationInputs(...args),
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

    renderEvaluationPage();

    expect(screen.getByText('Test Brand')).toBeInTheDocument();
  });

  it('renders all 5 section navigation items', () => {
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

    renderEvaluationPage();

    // Section nav renders inside a <nav> landmark
    const nav = screen.getByRole('navigation', { name: /evaluation sections/i });
    expect(nav).toBeInTheDocument();
    // 5 buttons inside the nav (one per step)
    const navButtons = nav.querySelectorAll('button');
    expect(navButtons).toHaveLength(5);
  });

  it('renders file upload slot placeholders', () => {
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

    renderEvaluationPage();

    expect(screen.getByText('CPC Ad Report')).toBeInTheDocument();
    expect(screen.getByText('Keyword Placement Report')).toBeInTheDocument();
    expect(screen.getByText('Order Export')).toBeInTheDocument();
    expect(screen.getByText('Mass Update / Sales Info')).toBeInTheDocument();
  });

  it('renders Fashion/Non-Fashion category selector', () => {
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

    renderEvaluationPage();

    expect(screen.getByText('Fashion')).toBeInTheDocument();
    expect(screen.getByText('Non-Fashion')).toBeInTheDocument();
  });

  it('renders score summary panel', () => {
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

    renderEvaluationPage();

    expect(screen.getByText('Score Summary')).toBeInTheDocument();
  });

  it('renders back to brands button', () => {
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

    renderEvaluationPage();

    expect(screen.getByRole('button', { name: /back to brands/i })).toBeInTheDocument();
  });
});
