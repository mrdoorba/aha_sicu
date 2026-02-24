import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Header } from './Header';

// Mock the AuthContext
const mockLogout = vi.fn();

vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
    user: { email: 'test@example.com' },
    logout: mockLogout,
  }),
}));

const mockProfile = { id: '1', email: 'test@example.com', role: 'leader', created_at: '', last_login: '' };

vi.mock('../../hooks/useCurrentUser', () => ({
  useCurrentUser: () => ({
    profile: mockProfile,
    isLoading: false,
    isError: false,
  }),
}));

const renderHeader = () => {
  return render(
    <BrowserRouter>
      <Header />
    </BrowserRouter>
  );
};

describe('Header', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockProfile.role = 'leader';
  });

  it('displays user email', () => {
    renderHeader();

    expect(screen.getByText('test@example.com')).toBeInTheDocument();
  });

  it('displays Store ICU title', () => {
    renderHeader();

    expect(screen.getByText('Store ICU')).toBeInTheDocument();
  });

  it('displays logout button', () => {
    renderHeader();

    expect(screen.getByRole('button', { name: /keluar/i })).toBeInTheDocument();
  });

  it('shows confirmation dialog when logout is clicked', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.click(screen.getByRole('button', { name: /keluar/i }));

    expect(screen.getByText(/konfirmasi keluar/i)).toBeInTheDocument();
    expect(screen.getByText(/apakah anda yakin ingin keluar/i)).toBeInTheDocument();
  });

  it('calls logout when confirmation is confirmed', async () => {
    const user = userEvent.setup();
    mockLogout.mockResolvedValueOnce(undefined);
    renderHeader();

    await user.click(screen.getByRole('button', { name: /^keluar$/i }));

    // Find the logout button inside the dialog using accessible role query
    const dialog = screen.getByRole('dialog');
    const confirmButton = within(dialog).getByRole('button', { name: /keluar/i });
    await user.click(confirmButton);

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
    });
  });

  it('closes dialog when cancel is clicked', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.click(screen.getByRole('button', { name: /^keluar$/i }));
    expect(screen.getByText(/konfirmasi keluar/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /batal/i }));

    await waitFor(() => {
      expect(screen.queryByText(/konfirmasi keluar/i)).not.toBeInTheDocument();
    });
    expect(mockLogout).not.toHaveBeenCalled();
  });

  it('closes dialog when Escape key is pressed', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.click(screen.getByRole('button', { name: /^keluar$/i }));
    expect(screen.getByText(/konfirmasi keluar/i)).toBeInTheDocument();

    await user.keyboard('{Escape}');

    await waitFor(() => {
      expect(screen.queryByText(/konfirmasi keluar/i)).not.toBeInTheDocument();
    });
    expect(mockLogout).not.toHaveBeenCalled();
  });

  it('displays Riwayat navigation link', () => {
    renderHeader();

    const historyLink = screen.getByRole('link', { name: /riwayat/i });
    expect(historyLink).toBeInTheDocument();
    expect(historyLink).toHaveAttribute('href', '/history');
  });

  it('dialog has accessible title and description', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.click(screen.getByRole('button', { name: /^keluar$/i }));

    const dialog = screen.getByRole('dialog');
    expect(dialog).toBeInTheDocument();

    // Radix Dialog auto-links DialogTitle and DialogDescription via aria-labelledby/aria-describedby
    expect(dialog).toHaveAttribute('aria-labelledby');
    expect(dialog).toHaveAttribute('aria-describedby');

    // Verify the actual title and description text are rendered
    expect(screen.getByText('Konfirmasi Keluar')).toBeInTheDocument();
    expect(screen.getByText('Apakah Anda yakin ingin keluar?')).toBeInTheDocument();
  });

  it('does not show Akun link for leader role', () => {
    renderHeader();
    expect(screen.queryByRole('link', { name: /^akun$/i })).not.toBeInTheDocument();
  });

  it('shows Aturan link for leader role', () => {
    renderHeader();
    expect(screen.getByRole('link', { name: /^aturan$/i })).toBeInTheDocument();
  });

  it('shows Akun link for admin role', () => {
    mockProfile.role = 'admin';
    renderHeader();
    const akunLink = screen.getByRole('link', { name: /^akun$/i });
    expect(akunLink).toBeInTheDocument();
    expect(akunLink).toHaveAttribute('href', '/accounts');
  });

  it('shows Aturan link for admin role', () => {
    mockProfile.role = 'admin';
    renderHeader();
    expect(screen.getByRole('link', { name: /^aturan$/i })).toBeInTheDocument();
  });

  it('does not show Akun link for member role', () => {
    mockProfile.role = 'member';
    renderHeader();
    expect(screen.queryByRole('link', { name: /^akun$/i })).not.toBeInTheDocument();
  });

  it('does not show Aturan link for member role', () => {
    mockProfile.role = 'member';
    renderHeader();
    expect(screen.queryByRole('link', { name: /^aturan$/i })).not.toBeInTheDocument();
  });
});
