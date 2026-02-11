import { render, screen, waitFor } from '@testing-library/react';
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

    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
  });

  it('shows confirmation dialog when logout is clicked', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.click(screen.getByRole('button', { name: /logout/i }));

    expect(screen.getByText(/confirm logout/i)).toBeInTheDocument();
    expect(screen.getByText(/are you sure you want to log out/i)).toBeInTheDocument();
  });

  it('calls logout when confirmation is confirmed', async () => {
    const user = userEvent.setup();
    mockLogout.mockResolvedValueOnce(undefined);
    renderHeader();

    await user.click(screen.getByRole('button', { name: /^logout$/i }));

    // Find the destructive logout button inside the dialog (via data-variant attribute)
    const dialog = screen.getByRole('dialog');
    const confirmButton = dialog.querySelector('button[data-variant="destructive"]') as HTMLElement;
    await user.click(confirmButton);

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
    });
  });

  it('closes dialog when cancel is clicked', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.click(screen.getByRole('button', { name: /^logout$/i }));
    expect(screen.getByText(/confirm logout/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /cancel/i }));

    await waitFor(() => {
      expect(screen.queryByText(/confirm logout/i)).not.toBeInTheDocument();
    });
    expect(mockLogout).not.toHaveBeenCalled();
  });

  it('closes dialog when Escape key is pressed', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.click(screen.getByRole('button', { name: /^logout$/i }));
    expect(screen.getByText(/confirm logout/i)).toBeInTheDocument();

    await user.keyboard('{Escape}');

    await waitFor(() => {
      expect(screen.queryByText(/confirm logout/i)).not.toBeInTheDocument();
    });
    expect(mockLogout).not.toHaveBeenCalled();
  });

  it('dialog has accessible title and description', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.click(screen.getByRole('button', { name: /^logout$/i }));

    const dialog = screen.getByRole('dialog');
    expect(dialog).toBeInTheDocument();

    // Radix Dialog auto-links DialogTitle and DialogDescription via aria-labelledby/aria-describedby
    expect(dialog).toHaveAttribute('aria-labelledby');
    expect(dialog).toHaveAttribute('aria-describedby');

    // Verify the actual title and description text are rendered
    expect(screen.getByText('Confirm Logout')).toBeInTheDocument();
    expect(screen.getByText('Are you sure you want to log out?')).toBeInTheDocument();
  });
});
