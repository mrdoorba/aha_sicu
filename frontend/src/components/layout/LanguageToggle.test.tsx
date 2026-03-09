import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { LanguageToggle } from './LanguageToggle';

const { mockChangeLanguage, mockToastError, mockUpdateLanguage, mockLanguageRef } = vi.hoisted(() => ({
  mockChangeLanguage: vi.fn(),
  mockToastError: vi.fn(),
  mockUpdateLanguage: vi.fn(),
  mockLanguageRef: { value: 'id' },
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    i18n: {
      get language() { return mockLanguageRef.value; },
      changeLanguage: mockChangeLanguage,
    },
    t: (key: string) => key,
  }),
}));

vi.mock('sonner', () => ({
  toast: { error: mockToastError },
}));

vi.mock('../../services/apiClient', () => ({
  updateLanguage: (...args: unknown[]) => mockUpdateLanguage(...args),
}));

describe('LanguageToggle', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLanguageRef.value = 'id';
    mockUpdateLanguage.mockResolvedValue({});
  });

  it('should render all language options when dropdown opened', async () => {
    const user = userEvent.setup();
    render(<LanguageToggle />);

    await user.click(screen.getByTestId('language-toggle'));

    expect(screen.getByTestId('language-option-id')).toBeInTheDocument();
    expect(screen.getByTestId('language-option-en')).toBeInTheDocument();
    expect(screen.getByTestId('language-option-th')).toBeInTheDocument();
  });

  it('should call changeLanguage when option selected', async () => {
    const user = userEvent.setup();
    render(<LanguageToggle />);

    await user.click(screen.getByTestId('language-toggle'));
    await user.click(screen.getByTestId('language-option-en'));

    expect(mockChangeLanguage).toHaveBeenCalledWith('en');
  });

  it('should revert language and show toast when API fails', async () => {
    mockUpdateLanguage.mockRejectedValue(new Error('Network error'));

    const user = userEvent.setup();
    render(<LanguageToggle />);

    await user.click(screen.getByTestId('language-toggle'));
    await user.click(screen.getByTestId('language-option-en'));

    expect(mockChangeLanguage).toHaveBeenCalledWith('en');

    await waitFor(() => {
      expect(mockChangeLanguage).toHaveBeenCalledWith('id');
    });

    expect(mockToastError).toHaveBeenCalledWith('Failed to save language preference');
  });

  it('should render icon-only when isCollapsed', () => {
    render(<LanguageToggle isCollapsed />);

    const button = screen.getByTestId('language-toggle');
    expect(button).toBeInTheDocument();
    expect(screen.queryByText('ID')).not.toBeInTheDocument();
  });
});
