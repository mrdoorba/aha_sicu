import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AccountsPage } from './AccountsPage';

// Mock sonner
vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

// Mock auth
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: { email: 'admin@company.com' },
    logout: vi.fn(),
  }),
}));

// Mock current user — admin
vi.mock('../hooks/useCurrentUser', () => ({
  useCurrentUser: () => ({
    profile: { id: '1', email: 'admin@company.com', role: 'admin', created_at: '', last_login: '' },
    isLoading: false,
    isError: false,
  }),
}));

const MOCK_ACCOUNTS = [
  {
    id: 1,
    email: 'admin@company.com',
    role: 'admin',
    created_at: '2026-02-05T00:00:00Z',
    last_login: '2026-02-20T10:00:00Z',
  },
  {
    id: 2,
    email: 'member@company.com',
    role: 'member',
    created_at: '2026-02-05T00:00:00Z',
    last_login: null,
  },
];

const mockMutateAsync = vi.fn();
const mockCreateMutateAsync = vi.fn();
const mockResetMutateAsync = vi.fn();
const mockDeleteMutateAsync = vi.fn();

vi.mock('../hooks/useAccounts', () => ({
  useAccounts: () => ({
    accounts: MOCK_ACCOUNTS,
    isLoading: false,
    isError: false,
    refetch: vi.fn(),
  }),
  useCreateAccount: () => ({
    mutateAsync: mockCreateMutateAsync,
    isPending: false,
  }),
  useUpdateRole: () => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  }),
  useResetPassword: () => ({
    mutateAsync: mockResetMutateAsync,
    isPending: false,
  }),
  useDeleteAccount: () => ({
    mutateAsync: mockDeleteMutateAsync,
    isPending: false,
  }),
}));

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const renderPage = () => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AccountsPage />
      </BrowserRouter>
    </QueryClientProvider>,
  );
};

describe('AccountsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the page title and create button', () => {
    renderPage();
    expect(screen.getByText('Manajemen Akun')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /buat akun/i })).toBeInTheDocument();
  });

  it('renders user table with correct columns', () => {
    renderPage();
    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByText('Peran')).toBeInTheDocument();
    expect(screen.getByText('Login Terakhir')).toBeInTheDocument();
    expect(screen.getByText('Aksi')).toBeInTheDocument();
  });

  it('displays account emails in the table', () => {
    renderPage();
    // admin email appears in both header and table, so use getAllByText
    expect(screen.getAllByText('admin@company.com').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('member@company.com')).toBeInTheDocument();
  });

  it('disables action buttons on admin own row', () => {
    renderPage();
    const rows = screen.getAllByRole('row');
    // Row 0 = header, Row 1 = admin (self), Row 2 = member
    const adminRow = rows[1];
    const deleteButtons = adminRow.querySelectorAll('button');
    const resetPwButton = Array.from(deleteButtons).find(
      (btn) => btn.textContent === 'Reset PW',
    );
    const hapusButton = Array.from(deleteButtons).find(
      (btn) => btn.textContent === 'Hapus',
    );
    expect(resetPwButton).toBeDisabled();
    expect(hapusButton).toBeDisabled();
  });

  it('enables action buttons on other users', () => {
    renderPage();
    const rows = screen.getAllByRole('row');
    const memberRow = rows[2];
    const buttons = memberRow.querySelectorAll('button');
    const resetPwButton = Array.from(buttons).find(
      (btn) => btn.textContent === 'Reset PW',
    );
    const hapusButton = Array.from(buttons).find(
      (btn) => btn.textContent === 'Hapus',
    );
    expect(resetPwButton).not.toBeDisabled();
    expect(hapusButton).not.toBeDisabled();
  });

  it('opens create account dialog', async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByRole('button', { name: /buat akun/i }));
    expect(screen.getByText('Buat Akun Baru')).toBeInTheDocument();
  });

  it('opens delete confirmation dialog', async () => {
    const user = userEvent.setup();
    renderPage();

    // Click delete on member row
    const rows = screen.getAllByRole('row');
    const memberRow = rows[2];
    const hapusButton = Array.from(memberRow.querySelectorAll('button')).find(
      (btn) => btn.textContent === 'Hapus',
    )!;
    await user.click(hapusButton);

    expect(screen.getByText('Hapus Akun')).toBeInTheDocument();
    // Check within dialog for the email
    const dialog = screen.getByRole('dialog');
    expect(within(dialog).getByText(/member@company.com/)).toBeInTheDocument();
  });

  it('opens reset password dialog', async () => {
    const user = userEvent.setup();
    renderPage();

    const rows = screen.getAllByRole('row');
    const memberRow = rows[2];
    const resetButton = Array.from(memberRow.querySelectorAll('button')).find(
      (btn) => btn.textContent === 'Reset PW',
    )!;
    await user.click(resetButton);

    expect(screen.getByText('Reset Password')).toBeInTheDocument();
    const dialog = screen.getByRole('dialog');
    expect(within(dialog).getByText(/member@company.com/)).toBeInTheDocument();
  });

  it('calls delete mutation when confirmed', async () => {
    mockDeleteMutateAsync.mockResolvedValueOnce(undefined);
    const user = userEvent.setup();
    renderPage();

    // Open delete dialog for member
    const rows = screen.getAllByRole('row');
    const memberRow = rows[2];
    const hapusButton = Array.from(memberRow.querySelectorAll('button')).find(
      (btn) => btn.textContent === 'Hapus',
    )!;
    await user.click(hapusButton);

    // Click confirm delete in dialog
    const dialog = screen.getByRole('dialog');
    const confirmButton = Array.from(dialog.querySelectorAll('button')).find(
      (btn) => btn.textContent === 'Hapus',
    )!;
    await user.click(confirmButton);

    await waitFor(() => {
      expect(mockDeleteMutateAsync).toHaveBeenCalledWith(2);
    });
  });
});
