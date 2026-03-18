import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { EvaluationHistoryTable } from './EvaluationHistoryTable';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'id', changeLanguage: vi.fn() },
  }),
}));

const mockRefetch = vi.fn();

const MOCK_BRANDS = [
  {
    brand_id: 10,
    brand_name: 'Nike Indonesia',
    evaluation_count: 5,
    top_score: 82.5,
    top_verdict: '\u2714\uFE0F',
    latest_date: '2026-02-15T10:00:00Z',
  },
  {
    brand_id: 20,
    brand_name: 'Adidas SEA',
    evaluation_count: 3,
    top_score: 75.0,
    top_verdict: '\u2714\uFE0F',
    latest_date: '2026-02-14T14:00:00Z',
  },
];

let mockGroupedReturn = {
  brands: MOCK_BRANDS,
  total: 2,
  page: 1,
  pages: 1,
  isLoading: false,
  isError: false,
  error: null as Error | null,
  refetch: mockRefetch,
  isPlaceholderData: false,
};

const MOCK_BRAND_EVALS = [
  { id: 101, final_score: 82.5, verdict: '\u2714\uFE0F', template: 'fashion', evaluator_email: 'rina@company.com', created_at: '2026-02-15T10:00:00Z' },
  { id: 102, final_score: 78.0, verdict: '\u2714\uFE0F', template: 'fashion', evaluator_email: 'budi@company.com', created_at: '2026-02-12T14:00:00Z' },
];

const MOCK_BRAND_EVALS_MANY = [
  { id: 101, final_score: 82.5, verdict: '\u2714\uFE0F', template: 'fashion', evaluator_email: 'a@co.com', created_at: '2026-02-15T10:00:00Z' },
  { id: 102, final_score: 80.0, verdict: '\u2714\uFE0F', template: 'fashion', evaluator_email: 'b@co.com', created_at: '2026-02-14T10:00:00Z' },
  { id: 103, final_score: 78.0, verdict: '\u2714\uFE0F', template: 'fashion', evaluator_email: 'c@co.com', created_at: '2026-02-13T10:00:00Z' },
  { id: 104, final_score: 76.0, verdict: '\u2714\uFE0F', template: 'fashion', evaluator_email: 'd@co.com', created_at: '2026-02-12T10:00:00Z' },
  { id: 105, final_score: 74.0, verdict: '\u2714\uFE0F', template: 'fashion', evaluator_email: 'e@co.com', created_at: '2026-02-11T10:00:00Z' },
];

let mockBrandReturn = {
  evaluations: MOCK_BRAND_EVALS,
  total: 2,
  isLoading: false,
  isError: false,
  refetch: vi.fn(),
};

const mockUseGrouped = vi.fn(() => mockGroupedReturn);
const mockUseBrand = vi.fn(() => mockBrandReturn);

vi.mock('../../hooks/useGroupedEvaluations', () => ({
  useGroupedEvaluations: (...args: unknown[]) => mockUseGrouped(...args),
}));

vi.mock('../../hooks/useBrandEvaluations', () => ({
  useBrandEvaluations: (...args: unknown[]) => mockUseBrand(...args),
}));

function LocationDisplay() {
  const location = useLocation();
  return (
    <div data-testid="location">
      {location.pathname}
      {location.search}
    </div>
  );
}

const renderTable = (initialEntries = ['/history']) => {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <EvaluationHistoryTable />
      <LocationDisplay />
    </MemoryRouter>,
  );
};

describe('EvaluationHistoryTable — Accordion', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGroupedReturn = {
      brands: MOCK_BRANDS,
      total: 2,
      page: 1,
      pages: 1,
      isLoading: false,
      isError: false,
      error: null,
      refetch: mockRefetch,
      isPlaceholderData: false,
    };
    mockBrandReturn = {
      evaluations: MOCK_BRAND_EVALS,
      total: 2,
      isLoading: false,
      isError: false,
      refetch: vi.fn(),
    };
  });

  // --- Render grouped data ---

  it('renders i18n column headers: BRAND, EVALUATIONS, TOP SCORE, LATEST', () => {
    renderTable();

    expect(screen.getByText('history.table.brand')).toBeInTheDocument();
    expect(screen.getByText('history.table.evaluations')).toBeInTheDocument();
    expect(screen.getByText('history.table.topScore')).toBeInTheDocument();
    expect(screen.getByText('history.table.latest')).toBeInTheDocument();
  });

  it('renders brand summary rows with name, count, score, and date', () => {
    renderTable();

    expect(screen.getByText('Nike Indonesia')).toBeInTheDocument();
    expect(screen.getAllByText('history.table.evaluationCount').length).toBeGreaterThan(0);
    expect(screen.getByText(/82\.50/)).toBeInTheDocument();
    expect(screen.getByText('Adidas SEA')).toBeInTheDocument();
  });

  // --- Expand/Collapse ---

  it('expands brand on click showing individual evaluations', async () => {
    const user = userEvent.setup();
    renderTable();

    const nikeRow = screen.getByText('Nike Indonesia').closest('tr')!;
    await user.click(nikeRow);

    await waitFor(() => {
      expect(screen.getByText('rina@company.com')).toBeInTheDocument();
      expect(screen.getByText('budi@company.com')).toBeInTheDocument();
    });
  });

  it('collapses expanded brand on second click', async () => {
    const user = userEvent.setup();
    renderTable();

    const nikeRow = screen.getByText('Nike Indonesia').closest('tr')!;

    // Expand
    await user.click(nikeRow);
    await waitFor(() => {
      expect(screen.getByText('rina@company.com')).toBeInTheDocument();
    });

    // Collapse — expanded row's aria-expanded should flip
    await user.click(nikeRow);
    expect(nikeRow).toHaveAttribute('aria-expanded', 'false');
  });

  // --- Limit 5 & "Tampilkan semua" ---

  it('shows "show all" button when total > 5', async () => {
    mockBrandReturn = {
      evaluations: MOCK_BRAND_EVALS_MANY,
      total: 8,
      isLoading: false,
      isError: false,
      refetch: vi.fn(),
    };
    const user = userEvent.setup();
    renderTable();

    const nikeRow = screen.getByText('Nike Indonesia').closest('tr')!;
    await user.click(nikeRow);

    await waitFor(() => {
      expect(screen.getByText('history.table.showAll')).toBeInTheDocument();
    });
  });

  it('does not show "show all" when total <= 5', async () => {
    const user = userEvent.setup();
    renderTable();

    const nikeRow = screen.getByText('Nike Indonesia').closest('tr')!;
    await user.click(nikeRow);

    await waitFor(() => {
      expect(screen.getByText('rina@company.com')).toBeInTheDocument();
    });
    expect(screen.queryByText('history.table.showAll')).not.toBeInTheDocument();
  });

  // --- Pagination ---

  it('shows pagination controls for multiple pages', () => {
    mockGroupedReturn = {
      ...mockGroupedReturn,
      pages: 3,
      total: 50,
    };
    renderTable();

    expect(screen.getByText('common.pageOf')).toBeInTheDocument();
    expect(screen.getByText('common.previous')).toBeInTheDocument();
    expect(screen.getByText('common.next')).toBeInTheDocument();
  });

  it('pagination next button updates URL', async () => {
    const user = userEvent.setup();
    mockGroupedReturn = {
      ...mockGroupedReturn,
      total: 40,
      pages: 2,
    };
    renderTable();

    const nextButton = screen.getByRole('button', { name: /common\.next/i });
    await user.click(nextButton);

    expect(screen.getByTestId('location')).toHaveTextContent('?page=2');
  });

  // --- Search ---

  it('search input has i18n placeholder', () => {
    renderTable();

    const searchInput = screen.getByRole('textbox', {
      name: /history\.table\.aria\.searchInput/i,
    });
    expect(searchInput).toBeInTheDocument();
    expect(searchInput).toHaveAttribute('placeholder', 'history.table.searchPlaceholder');
  });

  it('typing in search updates URL with search param after debounce', async () => {
    const user = userEvent.setup();
    renderTable();

    const searchInput = screen.getByRole('textbox', {
      name: /history\.table\.aria\.searchInput/i,
    });
    await user.type(searchInput, 'Nike');

    await waitFor(() => {
      expect(screen.getByTestId('location')).toHaveTextContent('search=Nike');
    });
  });

  // --- Date filters ---

  it('date pickers have i18n labels', () => {
    renderTable();

    const fromPicker = screen.getByRole('button', { name: /history\.table\.aria\.dateFrom/i });
    const toPicker = screen.getByRole('button', { name: /history\.table\.aria\.dateTo/i });
    expect(fromPicker).toBeInTheDocument();
    expect(toPicker).toBeInTheDocument();
  });

  it('clearing date picker removes the corresponding URL param', async () => {
    const user = userEvent.setup();
    renderTable(['/history?date_from=2026-01-01&date_to=2026-01-31']);

    const clearFromButton = screen.getByRole('button', { name: /history\.table\.aria\.clearDateFrom/i });
    await user.click(clearFromButton);

    await waitFor(() => {
      const location = screen.getByTestId('location').textContent ?? '';
      expect(location).not.toContain('date_from=');
      expect(location).toContain('date_to=2026-01-31');
    });
  });

  // --- Empty / Error / Loading states ---

  it('shows empty state message when no brands', () => {
    mockGroupedReturn = {
      ...mockGroupedReturn,
      brands: [],
      total: 0,
    };
    renderTable();

    expect(screen.getByText('history.table.emptyState')).toBeInTheDocument();
  });

  it('shows error state with retry button', async () => {
    const user = userEvent.setup();
    mockGroupedReturn = {
      ...mockGroupedReturn,
      brands: [],
      total: 0,
      isError: true,
      error: new Error('Network error'),
    };
    renderTable();

    expect(screen.getByText('Network error')).toBeInTheDocument();
    const retryButton = screen.getByRole('button', { name: /common\.retry/i });
    await user.click(retryButton);
    expect(mockRefetch).toHaveBeenCalled();
  });

  it('shows loading skeleton with aria-busy', () => {
    mockGroupedReturn = {
      ...mockGroupedReturn,
      brands: [],
      total: 0,
      isLoading: true,
    };
    renderTable();

    const table = screen.getByRole('table');
    expect(table).toHaveAttribute('aria-busy', 'true');
  });

  it('shows contextual empty message for search filter', () => {
    mockGroupedReturn = {
      ...mockGroupedReturn,
      brands: [],
      total: 0,
    };
    renderTable(['/history?search=Nike']);

    expect(screen.getByText('history.table.noMatchSearch')).toBeInTheDocument();
  });

  it('shows contextual empty message for date filter', () => {
    mockGroupedReturn = {
      ...mockGroupedReturn,
      brands: [],
      total: 0,
    };
    renderTable(['/history?date_from=2026-01-01&date_to=2026-01-31']);

    expect(
      screen.getByText('history.table.noMatchDate'),
    ).toBeInTheDocument();
  });
});
