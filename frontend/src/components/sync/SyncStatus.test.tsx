import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SyncStatus } from './SyncStatus';

const mockUseSyncStatus = vi.fn();
const mockUseTriggerSync = vi.fn();

vi.mock('../../hooks/useSync', () => ({
  useSyncStatus: () => mockUseSyncStatus(),
  useTriggerSync: () => mockUseTriggerSync(),
}));

vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
    user: { email: 'test@example.com' },
    logout: vi.fn(),
  }),
}));

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const renderSyncStatus = () => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <SyncStatus />
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('SyncStatus', () => {
  const mockMutate = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockUseTriggerSync.mockReturnValue({
      mutate: mockMutate,
      isPending: false,
    });
  });

  it('renders "Last synced" for success state', () => {
    mockUseSyncStatus.mockReturnValue({
      data: {
        id: 1,
        status: 'success',
        last_sync: new Date().toISOString(),
        brands_synced: 100,
        error_message: null,
        sync_details: {
          vp_sheet: { rows_synced: 80, rows_skipped: 0, status: 'success' },
          meeting_sheet: { rows_synced: 20, rows_skipped: 0, status: 'success' },
        },
      },
      isLoading: false,
    });

    renderSyncStatus();

    expect(screen.getByText(/last synced:/i)).toBeInTheDocument();
    expect(screen.getByText(/vp: 80 brands/i)).toBeInTheDocument();
    expect(screen.getByText(/meeting: 20 brands/i)).toBeInTheDocument();
  });

  it('renders "Syncing..." for in_progress state', () => {
    mockUseSyncStatus.mockReturnValue({
      data: {
        id: 1,
        status: 'in_progress',
        last_sync: new Date().toISOString(),
        brands_synced: 0,
        error_message: null,
        sync_details: null,
      },
      isLoading: false,
    });

    renderSyncStatus();

    // Badge shows "Syncing..." and button also shows "Syncing..."
    const syncTexts = screen.getAllByText('Syncing...');
    expect(syncTexts.length).toBeGreaterThanOrEqual(1);
  });

  it('renders error message for failed state', () => {
    mockUseSyncStatus.mockReturnValue({
      data: {
        id: 1,
        status: 'failed',
        last_sync: new Date().toISOString(),
        brands_synced: 0,
        error_message: 'Connection timeout',
        sync_details: null,
      },
      isLoading: false,
    });

    renderSyncStatus();

    expect(screen.getByText(/last sync failed: connection timeout/i)).toBeInTheDocument();
  });

  it('renders "Never synced" when no sync data exists', () => {
    mockUseSyncStatus.mockReturnValue({
      data: null,
      isLoading: false,
    });

    renderSyncStatus();

    expect(screen.getByText('Never synced')).toBeInTheDocument();
  });

  it('"Sync Now" button triggers sync mutation', async () => {
    const user = userEvent.setup();
    mockUseSyncStatus.mockReturnValue({
      data: null,
      isLoading: false,
    });

    renderSyncStatus();

    const syncButton = screen.getByRole('button', { name: /sync now/i });
    await user.click(syncButton);

    expect(mockMutate).toHaveBeenCalled();
  });

  it('"Sync Now" button is disabled while syncing', () => {
    mockUseSyncStatus.mockReturnValue({
      data: {
        id: 1,
        status: 'in_progress',
        last_sync: new Date().toISOString(),
        brands_synced: 0,
        error_message: null,
        sync_details: null,
      },
      isLoading: false,
    });

    renderSyncStatus();

    const syncButton = screen.getByRole('button', { name: /syncing/i });
    expect(syncButton).toBeDisabled();
  });

  it('shows loading skeleton while loading', () => {
    mockUseSyncStatus.mockReturnValue({
      data: null,
      isLoading: true,
    });

    renderSyncStatus();

    // Should not show any status text while loading
    expect(screen.queryByText(/last synced/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/never synced/i)).not.toBeInTheDocument();
  });
});
