import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { PasswordConfirmDialog } from './PasswordConfirmDialog';

// Mock firebase/auth
const mockReauthenticateUser = vi.fn();
vi.mock('../../firebase/auth', () => ({
  reauthenticateUser: (...args: unknown[]) => mockReauthenticateUser(...args),
}));

beforeEach(() => {
  vi.clearAllMocks();
});

describe('PasswordConfirmDialog', () => {
  it('has accessible title and description', () => {
    render(
      <PasswordConfirmDialog
        open={true}
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
        isLoading={false}
      />,
    );

    expect(screen.getByText('Confirm Password')).toBeInTheDocument();
    expect(screen.getByText(/enter your password to confirm/i)).toBeInTheDocument();
  });

  it('Confirm button disabled when password is empty', () => {
    render(
      <PasswordConfirmDialog
        open={true}
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
        isLoading={false}
      />,
    );

    const confirmBtn = screen.getByRole('button', { name: /confirm/i });
    expect(confirmBtn).toBeDisabled();
  });

  it('Confirm button enabled when password is entered', async () => {
    const user = userEvent.setup();
    render(
      <PasswordConfirmDialog
        open={true}
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
        isLoading={false}
      />,
    );

    const passwordInput = screen.getByLabelText('Password');
    await user.type(passwordInput, 'mypassword');

    const confirmBtn = screen.getByRole('button', { name: /confirm/i });
    expect(confirmBtn).toBeEnabled();
  });

  it('calls onConfirm after successful reauthentication', async () => {
    const user = userEvent.setup();
    const mockOnConfirm = vi.fn().mockResolvedValue(undefined);
    mockReauthenticateUser.mockResolvedValue(undefined);

    render(
      <PasswordConfirmDialog
        open={true}
        onConfirm={mockOnConfirm}
        onCancel={vi.fn()}
        isLoading={false}
      />,
    );

    const passwordInput = screen.getByLabelText('Password');
    await user.type(passwordInput, 'correctpassword');

    const confirmBtn = screen.getByRole('button', { name: /confirm/i });
    await user.click(confirmBtn);

    expect(mockReauthenticateUser).toHaveBeenCalledWith('correctpassword');
    expect(mockOnConfirm).toHaveBeenCalled();
  });

  it('shows error on incorrect password', async () => {
    const user = userEvent.setup();
    const mockOnConfirm = vi.fn();
    mockReauthenticateUser.mockRejectedValue(new Error('auth/wrong-password'));

    render(
      <PasswordConfirmDialog
        open={true}
        onConfirm={mockOnConfirm}
        onCancel={vi.fn()}
        isLoading={false}
      />,
    );

    const passwordInput = screen.getByLabelText('Password');
    await user.type(passwordInput, 'wrongpassword');

    const confirmBtn = screen.getByRole('button', { name: /confirm/i });
    await user.click(confirmBtn);

    expect(await screen.findByText('Incorrect password')).toBeInTheDocument();
    expect(mockOnConfirm).not.toHaveBeenCalled();
  });

  it('calls onCancel when Cancel is clicked', async () => {
    const user = userEvent.setup();
    const mockOnCancel = vi.fn();

    render(
      <PasswordConfirmDialog
        open={true}
        onConfirm={vi.fn()}
        onCancel={mockOnCancel}
        isLoading={false}
      />,
    );

    const cancelBtn = screen.getByRole('button', { name: /^cancel$/i });
    await user.click(cancelBtn);

    expect(mockOnCancel).toHaveBeenCalled();
  });
});
