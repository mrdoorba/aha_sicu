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

  it('renders "Terakhir disinkronkan" for success state', () => {
    mockUseSyncStatus.mockReturnValue({
      data: {
        id: 1,
        status: 'success',
        last_sync: new Date().toISOString(),
        brands_synced: 100,
        error_message: null,
        sync_details: {
          vp_id: { rows_synced: 80, rows_skipped: 0, status: 'success' },
          m1_id: { rows_synced: 20, rows_skipped: 0, status: 'success' },
        },
      },
      isLoading: false,
    });

    renderSyncStatus();

    expect(screen.getByText(/terakhir disinkronkan/i)).toBeInTheDocument();
    expect(screen.getByText(/VP_ID: 80/)).toBeInTheDocument();
    expect(screen.getByText(/M1_ID: 20/)).toBeInTheDocument();
  });

  it('renders "Menyinkronkan..." for in_progress state', () => {
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

    // Badge shows "Menyinkronkan..." and button also shows "Menyinkronkan..."
    const syncTexts = screen.getAllByText('Menyinkronkan...');
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

    expect(screen.getByText(/sinkronisasi terakhir gagal: connection timeout/i)).toBeInTheDocument();
  });

  it('shows explicit drift summary from sync details', () => {
    mockUseSyncStatus.mockReturnValue({
      data: {
        id: 1,
        status: 'failed',
        last_sync: new Date().toISOString(),
        brands_synced: 0,
        error_message: 'Column drift',
        sync_details: {
          vp_id: {
            status: 'column_drift',
            sheet: 'VP',
            marketplace: 'ID',
            error: 'No WA* → No WA',
            changed_columns: [
              { position: 19, expected: 'No WA*', actual: 'No WA' },
            ],
            missing: ['No WA*'],
            unexpected: ['No WA'],
          },
        },
      },
      isLoading: false,
    });

    renderSyncStatus();

    expect(screen.getByRole('button', { name: /no wa\* → no wa/i })).toBeInTheDocument();
  });

  it('renders "Belum pernah disinkronkan" when no sync data exists', () => {
    mockUseSyncStatus.mockReturnValue({
      data: null,
      isLoading: false,
    });

    renderSyncStatus();

    expect(screen.getByText('Belum pernah disinkronkan')).toBeInTheDocument();
  });

  it('"Sinkronisasi" button triggers sync mutation', async () => {
    const user = userEvent.setup();
    mockUseSyncStatus.mockReturnValue({
      data: null,
      isLoading: false,
    });

    renderSyncStatus();

    const syncButton = screen.getByRole('button', { name: /sinkronisasi/i });
    await user.click(syncButton);

    expect(mockMutate).toHaveBeenCalled();
  });

  it('opens drift dialog from trigger response sync_details', async () => {
    const user = userEvent.setup();
    mockUseSyncStatus.mockReturnValue({
      data: null,
      isLoading: false,
    });
    mockUseTriggerSync.mockReturnValue({
      isPending: false,
      mutate: (_arg: unknown, options?: { onSuccess?: (data: unknown) => void }) => {
        options?.onSuccess?.({
          id: 1,
          status: 'failed',
          last_sync: new Date().toISOString(),
          started_at: new Date().toISOString(),
          completed_at: new Date().toISOString(),
          brands_synced: 0,
          error_message: 'Column drift',
          sync_details: {
            vp_id: {
              status: 'column_drift',
              sheet: 'VP',
              marketplace: 'ID',
              error: 'No WA* → No WA',
              changed_columns: [
                { position: 19, expected: 'No WA*', actual: 'No WA' },
              ],
              expected_headers: ['Nama Brand', 'No WA*'],
              actual_headers: ['Nama Brand', 'No WA'],
              missing: ['No WA*'],
              unexpected: ['No WA'],
            },
          },
        });
      },
    });

    renderSyncStatus();

    await user.click(screen.getByRole('button', { name: /sinkronisasi/i }));

    expect(screen.getByText(/column mismatch detected/i)).toBeInTheDocument();
    expect(screen.getByText(/no wa\* → no wa/i)).toBeInTheDocument();
    expect(screen.getByText(/expected headers/i)).toBeInTheDocument();
    expect(screen.getAllByText(/actual headers/i).length).toBeGreaterThanOrEqual(1);
  });

  it('cycles through multiple drift entries from one trigger response', async () => {
    const user = userEvent.setup();
    mockUseSyncStatus.mockReturnValue({
      data: null,
      isLoading: false,
    });
    mockUseTriggerSync.mockReturnValue({
      isPending: false,
      mutate: (_arg: unknown, options?: { onSuccess?: (data: unknown) => void }) => {
        options?.onSuccess?.({
          id: 1,
          status: 'failed',
          last_sync: new Date().toISOString(),
          started_at: new Date().toISOString(),
          completed_at: new Date().toISOString(),
          brands_synced: 0,
          error_message: 'Column drift',
          sync_details: {
            vp_id: {
              status: 'column_drift',
              sheet: 'VP',
              marketplace: 'ID',
              error: 'No WA* → No WA',
              changed_columns: [
                { position: 19, expected: 'No WA*', actual: 'No WA' },
              ],
            },
            m1_id: {
              status: 'column_drift',
              sheet: 'Meeting',
              marketplace: 'ID',
              error: 'Duration (mins) → Minutes',
              changed_columns: [
                { position: 3, expected: 'Duration (mins)', actual: 'Minutes' },
              ],
            },
          },
        });
      },
    });

    renderSyncStatus();

    await user.click(screen.getByRole('button', { name: /sinkronisasi/i }));

    expect(screen.getByText(/no wa\* → no wa/i)).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /next drift/i }));
    expect(screen.getByText(/duration \(mins\) → minutes/i)).toBeInTheDocument();
  });

  it('"Sinkronisasi" button is disabled while syncing', () => {
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

    const syncButton = screen.getByRole('button', { name: /menyinkronkan/i });
    expect(syncButton).toBeDisabled();
  });

  it('shows loading skeleton while loading', () => {
    mockUseSyncStatus.mockReturnValue({
      data: null,
      isLoading: true,
    });

    renderSyncStatus();

    // Should not show any status text while loading
    expect(screen.queryByText(/terakhir disinkronkan/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/belum pernah disinkronkan/i)).not.toBeInTheDocument();
  });

  it('shows error state when sync status fetch fails', () => {
    mockUseSyncStatus.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
    });

    renderSyncStatus();

    expect(screen.getByText(/gagal memuat status sinkronisasi/i)).toBeInTheDocument();
    expect(screen.queryByText(/belum pernah disinkronkan/i)).not.toBeInTheDocument();
  });

  it('has aria-live="polite" region for sync status announcements', () => {
    mockUseSyncStatus.mockReturnValue({
      data: null,
      isLoading: false,
    });

    const { container } = renderSyncStatus();

    const liveRegion = container.querySelector('[aria-live="polite"]');
    expect(liveRegion).toBeInTheDocument();
    expect(liveRegion).toHaveAttribute('aria-atomic', 'true');
  });

  it('decorative icons inside badges have aria-hidden="true"', () => {
    mockUseSyncStatus.mockReturnValue({
      data: {
        id: 1,
        status: 'success',
        last_sync: new Date().toISOString(),
        brands_synced: 100,
        error_message: null,
        sync_details: null,
      },
      isLoading: false,
    });

    const { container } = renderSyncStatus();

    // All SVG icons within the aria-live region should be aria-hidden
    const liveRegion = container.querySelector('[aria-live="polite"]');
    const icons = liveRegion?.querySelectorAll('svg');
    icons?.forEach((icon) => {
      expect(icon).toHaveAttribute('aria-hidden', 'true');
    });
  });
});
