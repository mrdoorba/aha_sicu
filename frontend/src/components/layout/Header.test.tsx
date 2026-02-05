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

  it('shows confirmation modal when logout is clicked', async () => {
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

    // Click the confirm logout button in modal
    const confirmButtons = screen.getAllByRole('button', { name: /logout/i });
    const confirmButton = confirmButtons.find(btn => btn.textContent === 'Logout' && btn.className.includes('bg-[#EF4444]'));
    if (confirmButton) {
      await user.click(confirmButton);
    }

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
    });
  });

  it('closes modal when cancel is clicked', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.click(screen.getByRole('button', { name: /^logout$/i }));
    expect(screen.getByText(/confirm logout/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /cancel/i }));

    expect(screen.queryByText(/confirm logout/i)).not.toBeInTheDocument();
    expect(mockLogout).not.toHaveBeenCalled();
  });

  it('closes modal when Escape key is pressed', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.click(screen.getByRole('button', { name: /^logout$/i }));
    expect(screen.getByText(/confirm logout/i)).toBeInTheDocument();

    await user.keyboard('{Escape}');

    expect(screen.queryByText(/confirm logout/i)).not.toBeInTheDocument();
    expect(mockLogout).not.toHaveBeenCalled();
  });

  it('modal has proper accessibility attributes', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.click(screen.getByRole('button', { name: /^logout$/i }));

    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby', 'logout-modal-title');
    expect(dialog).toHaveAttribute('aria-describedby', 'logout-modal-description');
  });

  it('closes modal when clicking backdrop', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.click(screen.getByRole('button', { name: /^logout$/i }));
    expect(screen.getByText(/confirm logout/i)).toBeInTheDocument();

    // Click on the backdrop (the dialog container)
    const dialog = screen.getByRole('dialog');
    await user.click(dialog);

    expect(screen.queryByText(/confirm logout/i)).not.toBeInTheDocument();
  });
});
