import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrandsPage } from './BrandsPage';

const mockUseBrands = vi.fn();
const mockUseSyncStatus = vi.fn();
const mockUseTriggerSync = vi.fn();

vi.mock('../hooks/useBrands', () => ({
  useBrands: (...args: unknown[]) => mockUseBrands(...args),
}));

vi.mock('../hooks/useSync', () => ({
  useSyncStatus: () => mockUseSyncStatus(),
  useTriggerSync: () => mockUseTriggerSync(),
}));

vi.mock('../hooks/useSSE', () => ({
  useSSE: () => ({ connectionState: 'connected' }),
}));

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: { email: 'test@example.com' },
    logout: vi.fn(),
  }),
}));

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const renderBrandsPage = () => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <BrandsPage />
      </BrowserRouter>
    </QueryClientProvider>
  );
};

const BRANDS_RESPONSE = {
  items: [
    {
      id: 1,
      brand_name: 'Brand ABC',
      raw_data: { category: 'Electronics' },
      updated_at: '2026-02-05T10:00:00Z',
      meeting_raw_data: { notes: 'Good' },
    },
    {
      id: 2,
      brand_name: 'Brand DEF',
      raw_data: { category: 'Fashion' },
      updated_at: '2026-02-05T11:00:00Z',
      meeting_raw_data: null,
    },
  ],
  total: 2,
  page: 1,
  limit: 20,
  pages: 1,
};

describe('BrandsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseTriggerSync.mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    });
    mockUseSyncStatus.mockReturnValue({
      data: null,
      isLoading: false,
    });
  });

  it('renders brands page with title', () => {
    mockUseBrands.mockReturnValue({
      data: BRANDS_RESPONSE,
      isLoading: false,
    });

    renderBrandsPage();

    // Title is an h2, nav link also says "Brands"
    const heading = screen.getByRole('heading', { name: 'Brands', level: 2 });
    expect(heading).toBeInTheDocument();
  });

  it('renders brand data in table', () => {
    mockUseBrands.mockReturnValue({
      data: BRANDS_RESPONSE,
      isLoading: false,
    });

    renderBrandsPage();

    expect(screen.getByText('Brand ABC')).toBeInTheDocument();
    expect(screen.getByText('Brand DEF')).toBeInTheDocument();
  });

  it('shows empty state when no brands synced', () => {
    mockUseBrands.mockReturnValue({
      data: { items: [], total: 0, page: 1, limit: 20, pages: 0 },
      isLoading: false,
    });

    renderBrandsPage();

    expect(
      screen.getByText(/no brands synced yet/i)
    ).toBeInTheDocument();
  });

  it('shows no results message when search has no matches', async () => {
    const user = userEvent.setup();
    // First render with no search — return brands
    mockUseBrands.mockReturnValue({
      data: BRANDS_RESPONSE,
      isLoading: false,
    });

    renderBrandsPage();

    // Now type search — mock returns empty
    mockUseBrands.mockReturnValue({
      data: { items: [], total: 0, page: 1, limit: 20, pages: 0 },
      isLoading: false,
    });

    const searchInput = screen.getByPlaceholderText(/search brands/i);
    await user.type(searchInput, 'nonexistent');

    await waitFor(() => {
      expect(screen.getByText(/no brands found matching/i)).toBeInTheDocument();
    });
  });

  it('search input triggers filtered query', async () => {
    const user = userEvent.setup();
    mockUseBrands.mockReturnValue({
      data: BRANDS_RESPONSE,
      isLoading: false,
    });

    renderBrandsPage();

    const searchInput = screen.getByPlaceholderText(/search brands/i);
    await user.type(searchInput, 'ABC');

    // Wait for debounce (300ms) and verify useBrands was called with search term
    await waitFor(() => {
      expect(mockUseBrands).toHaveBeenCalledWith(1, 20, 'ABC');
    });
  });

  it('pagination controls navigate between pages', async () => {
    const user = userEvent.setup();
    mockUseBrands.mockReturnValue({
      data: {
        items: BRANDS_RESPONSE.items,
        total: 100,
        page: 1,
        limit: 20,
        pages: 5,
      },
      isLoading: false,
    });

    renderBrandsPage();

    expect(screen.getByText('Page 1 of 5')).toBeInTheDocument();

    const nextButton = screen.getByRole('button', { name: /next/i });
    await user.click(nextButton);

    await waitFor(() => {
      expect(mockUseBrands).toHaveBeenCalledWith(2, 20, '');
    });
  });

  it('hides pagination when only one page', () => {
    mockUseBrands.mockReturnValue({
      data: BRANDS_RESPONSE,
      isLoading: false,
    });

    renderBrandsPage();

    expect(screen.queryByText(/page \d+ of/i)).not.toBeInTheDocument();
  });
});
