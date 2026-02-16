import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { EvaluationHistoryTable } from './EvaluationHistoryTable';

const mockRefetch = vi.fn();

const MOCK_EVALUATIONS = [
  {
    id: 1,
    brand_name: 'Nike Indonesia',
    final_score: 78.5,
    verdict: '\u2714\uFE0F',
    template: 'fashion',
    evaluator_email: 'rina@company.com',
    created_at: '2026-02-10T10:30:00Z',
  },
  {
    id: 2,
    brand_name: 'Unilever ID',
    final_score: 65.0,
    verdict: '\u274C',
    template: 'non_fashion',
    evaluator_email: 'budi@company.com',
    created_at: '2026-02-09T14:00:00Z',
  },
];

let mockHookReturn = {
  evaluations: MOCK_EVALUATIONS,
  total: 2,
  page: 1,
  pages: 1,
  isLoading: false,
  isError: false,
  error: null as Error | null,
  refetch: mockRefetch,
  isPlaceholderData: false,
};

const mockUseEvaluationHistory = vi.fn(() => mockHookReturn);

vi.mock('../../hooks/useEvaluationHistory', () => ({
  useEvaluationHistory: (...args: unknown[]) => mockUseEvaluationHistory(...args),
}));

/** Helper that renders current location for assertions. */
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

describe('EvaluationHistoryTable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockHookReturn = {
      evaluations: MOCK_EVALUATIONS,
      total: 2,
      page: 1,
      pages: 1,
      isLoading: false,
      isError: false,
      error: null,
      refetch: mockRefetch,
      isPlaceholderData: false,
    };
  });

  it('renders evaluation history table with data', () => {
    renderTable();

    expect(screen.getByText('Nike Indonesia')).toBeInTheDocument();
    expect(screen.getByText('Unilever ID')).toBeInTheDocument();
    expect(screen.getByText('rina@company.com')).toBeInTheDocument();
    expect(screen.getByText('budi@company.com')).toBeInTheDocument();
  });

  it('pagination buttons navigate between pages and update URL', async () => {
    const user = userEvent.setup();
    mockHookReturn = {
      ...mockHookReturn,
      total: 40,
      pages: 2,
    };
    renderTable();

    expect(screen.getByText('Page 1 of 2')).toBeInTheDocument();
    const prevButton = screen.getByRole('button', { name: /previous/i });
    const nextButton = screen.getByRole('button', { name: /next/i });
    expect(prevButton).toBeDisabled();
    expect(nextButton).not.toBeDisabled();

    // Click Next — URL should update with ?page=2
    await user.click(nextButton);
    expect(screen.getByTestId('location')).toHaveTextContent('?page=2');
  });

  it('column header click triggers sort and updates URL', async () => {
    const user = userEvent.setup();
    renderTable();

    // Date and Score columns should be sortable (rendered as buttons)
    const dateButton = screen.getByRole('button', { name: /sort by date/i });
    expect(dateButton).toBeInTheDocument();

    const scoreButton = screen.getByRole('button', { name: /sort by score/i });
    expect(scoreButton).toBeInTheDocument();

    // Click score to sort — URL should update with sort_by param
    await user.click(scoreButton);
    expect(screen.getByTestId('location')).toHaveTextContent('sort_by=final_score');
  });

  it('row click navigates to evaluation detail', async () => {
    const user = userEvent.setup();
    renderTable();

    // Click the first row (Nike Indonesia)
    const row = screen.getByText('Nike Indonesia').closest('tr')!;
    await user.click(row);

    // Should navigate to /history/1
    expect(screen.getByTestId('location')).toHaveTextContent('/history/1');
  });

  it('shows loading state during fetch', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluations: [],
      total: 0,
      isLoading: true,
    };
    renderTable();

    const table = screen.getByRole('table', { name: /evaluation history/i });
    expect(table).toHaveAttribute('aria-busy', 'true');
    // Should not show data
    expect(screen.queryByText('Nike Indonesia')).not.toBeInTheDocument();
  });

  it('shows aria-busy during placeholder data transitions', () => {
    mockHookReturn = {
      ...mockHookReturn,
      isPlaceholderData: true,
    };
    renderTable();

    const table = screen.getByRole('table', { name: /evaluation history/i });
    expect(table).toHaveAttribute('aria-busy', 'true');
  });

  it('shows empty state when no evaluations', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluations: [],
      total: 0,
    };
    renderTable();

    expect(screen.getByText('No evaluations found')).toBeInTheDocument();
  });

  it('shows error state with retry button', async () => {
    const user = userEvent.setup();
    mockHookReturn = {
      ...mockHookReturn,
      evaluations: [],
      total: 0,
      isError: true,
      error: new Error('Failed to load evaluations'),
    };
    renderTable();

    expect(screen.getByText('Failed to load evaluations')).toBeInTheDocument();
    const retryButton = screen.getByRole('button', { name: /retry/i });
    expect(retryButton).toBeInTheDocument();

    await user.click(retryButton);
    expect(mockRefetch).toHaveBeenCalled();
  });

  // --- Search tests (Story 4.2) ---

  it('search input renders with accessible label', () => {
    renderTable();

    const searchInput = screen.getByRole('textbox', {
      name: /search evaluations by brand name/i,
    });
    expect(searchInput).toBeInTheDocument();
    expect(searchInput).toHaveAttribute('placeholder', 'Search by brand name...');
  });

  it('typing in search triggers API call with search param', async () => {
    const user = userEvent.setup();
    renderTable();

    const searchInput = screen.getByRole('textbox', {
      name: /search evaluations by brand name/i,
    });

    await user.type(searchInput, 'Nike');

    // Wait for debounce to fire and URL to update
    await waitFor(() => {
      const lastCall = mockUseEvaluationHistory.mock.calls.at(-1);
      expect(lastCall?.[4]).toBe('Nike');
    });
  });

  it('search updates URL query params', async () => {
    const user = userEvent.setup();
    renderTable();

    const searchInput = screen.getByRole('textbox', {
      name: /search evaluations by brand name/i,
    });

    await user.type(searchInput, 'Nike');

    await waitFor(() => {
      expect(screen.getByTestId('location')).toHaveTextContent('search=Nike');
    });
  });

  it('clear button clears search and resets page', async () => {
    const user = userEvent.setup();
    renderTable(['/history?search=Nike']);

    // Clear button should be visible
    const clearButton = screen.getByRole('button', { name: /clear search/i });
    expect(clearButton).toBeInTheDocument();

    await user.click(clearButton);

    await waitFor(() => {
      const location = screen.getByTestId('location').textContent ?? '';
      expect(location).not.toContain('search=');
    });
  });

  it('empty search results show contextual message with search term', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluations: [],
      total: 0,
    };
    renderTable(['/history?search=Nike']);

    expect(
      screen.getByText("No evaluations found for 'Nike'"),
    ).toBeInTheDocument();
  });

  it('search persists across sort changes', async () => {
    const user = userEvent.setup();
    renderTable(['/history?search=Nike']);

    // Click sort by score
    const scoreButton = screen.getByRole('button', { name: /sort by score/i });
    await user.click(scoreButton);

    await waitFor(() => {
      const location = screen.getByTestId('location').textContent ?? '';
      expect(location).toContain('search=Nike');
      expect(location).toContain('sort_by=final_score');
    });
  });

  // --- Date filter tests (Story 4.3) ---

  it('date pickers render with accessible labels', () => {
    renderTable();

    const fromPicker = screen.getByRole('button', { name: /filter from date/i });
    const toPicker = screen.getByRole('button', { name: /filter to date/i });
    expect(fromPicker).toBeInTheDocument();
    expect(toPicker).toBeInTheDocument();
  });

  it('selecting from-date updates URL with date_from param and resets page', async () => {
    const user = userEvent.setup();
    renderTable(['/history?page=3']);

    // Click the from-date picker to open it
    const fromPicker = screen.getByRole('button', { name: /filter from date/i });
    await user.click(fromPicker);

    // Find the "15th" day button — uses ordinal suffix to avoid ambiguous matches
    const dayButton = screen.getByRole('button', { name: /15th/ });
    await user.click(dayButton);

    await waitFor(() => {
      const location = screen.getByTestId('location').textContent ?? '';
      expect(location).toContain('date_from=');
      expect(location).not.toContain('page=3');
    });
  });

  it('selecting to-date updates URL with date_to param', async () => {
    const user = userEvent.setup();
    renderTable();

    // Click the to-date picker to open it
    const toPicker = screen.getByRole('button', { name: /filter to date/i });
    await user.click(toPicker);

    // Find the "18th" day button — uses ordinal suffix to avoid matching "2026"
    const dayButton = screen.getByRole('button', { name: /18th/ });
    await user.click(dayButton);

    await waitFor(() => {
      const location = screen.getByTestId('location').textContent ?? '';
      expect(location).toContain('date_to=');
    });
  });

  it('clearing date picker removes the corresponding URL param', async () => {
    const user = userEvent.setup();
    renderTable(['/history?date_from=2026-01-01&date_to=2026-01-31']);

    // Clear from-date
    const clearFromButton = screen.getByRole('button', { name: /clear from date/i });
    expect(clearFromButton).toBeInTheDocument();
    await user.click(clearFromButton);

    await waitFor(() => {
      const location = screen.getByTestId('location').textContent ?? '';
      expect(location).not.toContain('date_from=');
      expect(location).toContain('date_to=2026-01-31');
    });
  });

  it('date filter combines with search in URL and hook call', () => {
    renderTable(['/history?search=Nike&date_from=2026-01-01']);

    const location = screen.getByTestId('location').textContent ?? '';
    expect(location).toContain('search=Nike');
    expect(location).toContain('date_from=2026-01-01');

    // Verify hook receives both params
    const lastCall = mockUseEvaluationHistory.mock.calls.at(-1);
    expect(lastCall?.[4]).toBe('Nike');       // search
    expect(lastCall?.[5]).toBe('2026-01-01'); // dateFrom
  });

  it('empty state with date filter shows contextual message', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluations: [],
      total: 0,
    };
    renderTable(['/history?date_from=2026-01-01&date_to=2026-01-31']);

    expect(
      screen.getByText('No evaluations found for the selected date range'),
    ).toBeInTheDocument();
  });

  it('date filter persists across sort changes', async () => {
    const user = userEvent.setup();
    renderTable(['/history?date_from=2026-01-01&date_to=2026-01-31']);

    // Click sort by score
    const scoreButton = screen.getByRole('button', { name: /sort by score/i });
    await user.click(scoreButton);

    await waitFor(() => {
      const location = screen.getByTestId('location').textContent ?? '';
      expect(location).toContain('date_from=2026-01-01');
      expect(location).toContain('date_to=2026-01-31');
      expect(location).toContain('sort_by=final_score');
    });
  });

});
