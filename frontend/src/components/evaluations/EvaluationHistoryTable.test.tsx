import { render, screen } from '@testing-library/react';
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

vi.mock('../../hooks/useEvaluationHistory', () => ({
  useEvaluationHistory: () => mockHookReturn,
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
    expect(screen.getByText('Fashion')).toBeInTheDocument();
    expect(screen.getByText('Non-Fashion')).toBeInTheDocument();
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
});
