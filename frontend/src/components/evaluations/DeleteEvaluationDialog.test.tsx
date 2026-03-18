import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { DeleteEvaluationDialog } from './DeleteEvaluationDialog';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'id', changeLanguage: vi.fn() },
  }),
}));

vi.mock('sonner', () => ({
  toast: { error: vi.fn(), success: vi.fn() },
}));

const defaultProps = {
  open: true,
  onOpenChange: vi.fn(),
  brandName: 'Nike Indonesia',
  onConfirm: vi.fn(),
  isDeleting: false,
};

const renderDialog = (props = {}) => {
  return render(<DeleteEvaluationDialog {...defaultProps} {...props} />);
};

describe('DeleteEvaluationDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dialog with title and warning message', () => {
    renderDialog();

    expect(screen.getByText('deleteDialog.title')).toBeInTheDocument();
    expect(screen.getByText('deleteDialog.description')).toBeInTheDocument();
  });

  it('displays brand name to type for confirmation', () => {
    renderDialog();

    expect(screen.getByText('Nike Indonesia')).toBeInTheDocument();
    expect(screen.getByText('deleteDialog.confirmPrompt')).toBeInTheDocument();
  });

  it('delete button is disabled until brand name matches', () => {
    renderDialog();

    const deleteButton = screen.getByRole('button', { name: 'common.delete' });
    expect(deleteButton).toBeDisabled();
  });

  it('delete button enables when brand name matches (case-insensitive)', async () => {
    const user = userEvent.setup();
    renderDialog();

    const input = screen.getByRole('textbox', { name: 'deleteDialog.aria.confirmInput' });
    await user.type(input, 'nike indonesia');

    const deleteButton = screen.getByRole('button', { name: 'common.delete' });
    expect(deleteButton).not.toBeDisabled();
  });

  it('delete button stays disabled when brand name does not match', async () => {
    const user = userEvent.setup();
    renderDialog();

    const input = screen.getByRole('textbox', { name: 'deleteDialog.aria.confirmInput' });
    await user.type(input, 'wrong name');

    const deleteButton = screen.getByRole('button', { name: 'common.delete' });
    expect(deleteButton).toBeDisabled();
  });

  it('calls onConfirm when delete button is clicked', async () => {
    const onConfirm = vi.fn();
    const user = userEvent.setup();
    renderDialog({ onConfirm });

    const input = screen.getByRole('textbox', { name: 'deleteDialog.aria.confirmInput' });
    await user.type(input, 'Nike Indonesia');

    const deleteButton = screen.getByRole('button', { name: 'common.delete' });
    await user.click(deleteButton);

    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('calls onOpenChange(false) when cancel button is clicked', async () => {
    const onOpenChange = vi.fn();
    const user = userEvent.setup();
    renderDialog({ onOpenChange });

    const cancelButton = screen.getByRole('button', { name: 'common.cancel' });
    await user.click(cancelButton);

    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it('copy button copies brand name to clipboard', async () => {
    // Ensure clipboard API exists on navigator
    if (!navigator.clipboard) {
      Object.defineProperty(navigator, 'clipboard', {
        value: { writeText: vi.fn() },
        writable: true,
        configurable: true,
      });
    }
    const spy = vi.spyOn(navigator.clipboard, 'writeText').mockResolvedValue(undefined);
    const user = userEvent.setup();
    renderDialog();

    const copyButton = screen.getByRole('button', { name: 'deleteDialog.aria.copyBrand' });
    await user.click(copyButton);

    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('Nike Indonesia');
    });
  });

  it('shows loading spinner when isDeleting is true', () => {
    renderDialog({ isDeleting: true });

    const deleteButton = screen.getByRole('button', { name: 'common.delete' });
    expect(deleteButton).toBeDisabled();

    const cancelButton = screen.getByRole('button', { name: 'common.cancel' });
    expect(cancelButton).toBeDisabled();
  });
});
