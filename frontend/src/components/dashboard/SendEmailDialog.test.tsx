import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// -- Mocks --

const mockMutate = vi.fn();
const mockReset = vi.fn();

vi.mock('../../../hooks/useSendEmail', () => ({
  useSendEmail: () => mockMutationReturn,
}));

let mockMutationReturn: {
  mutate: typeof mockMutate;
  isPending: boolean;
  isError: boolean;
  reset: typeof mockReset;
} = {
  mutate: mockMutate,
  isPending: false,
  isError: false,
  reset: mockReset,
};

const mockToPng = vi.fn();
vi.mock('html-to-image', () => ({
  toPng: (...args: unknown[]) => mockToPng(...args),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, opts?: Record<string, string>) =>
      opts?.recipient ? `${key} ${opts.recipient}` : key,
  }),
}));

const mockToastSuccess = vi.fn();
vi.mock('sonner', () => ({
  toast: { success: (...args: unknown[]) => mockToastSuccess(...args) },
}));

import { SendEmailDialog } from './SendEmailDialog';

// -- Helpers --

let queryClient: QueryClient;

function renderDialog(overrides: Record<string, unknown> = {}) {
  const defaultProps = {
    open: true,
    onOpenChange: vi.fn(),
    evaluationId: 1,
    brandName: 'Test Brand',
    period: '2026-01',
    score: 85.7,
    brandRawData: { email: 'pic@example.com', pic_name: 'PIC', store_link: null, kategori: null },
    chartRef: { current: document.createElement('div') },
    onSuccess: vi.fn(),
    ...overrides,
  };

  return {
    ...render(
      React.createElement(
        QueryClientProvider,
        { client: queryClient },
        React.createElement(SendEmailDialog, defaultProps as never),
      ),
    ),
    props: defaultProps,
  };
}

// -- Tests --

describe('SendEmailDialog', () => {
  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    mockMutationReturn = {
      mutate: mockMutate,
      isPending: false,
      isError: false,
      reset: mockReset,
    };
    mockMutate.mockReset();
    mockReset.mockReset();
    mockToPng.mockReset();
    mockToastSuccess.mockReset();
  });

  afterEach(() => {
    queryClient.clear();
  });

  it('renders with title "sendEmail.title" when open', () => {
    renderDialog();
    expect(screen.getByText('sendEmail.title')).toBeInTheDocument();
  });

  it('shows brand summary card with brand name, period, and score', () => {
    renderDialog();
    expect(screen.getByText('Test Brand')).toBeInTheDocument();
    expect(screen.getByText('2026-01')).toBeInTheDocument();
    expect(screen.getByText('86')).toBeInTheDocument(); // rounded
  });

  it('pre-fills recipient input with PIC email when brandRawData.email exists', () => {
    renderDialog();
    const input = screen.getByPlaceholderText('sendEmail.recipientPlaceholder') as HTMLInputElement;
    expect(input.value).toBe('pic@example.com');
  });

  it('leaves recipient input empty when brandRawData.email is null', () => {
    renderDialog({
      brandRawData: { email: null, pic_name: null, store_link: null, kategori: null },
    });
    const input = screen.getByPlaceholderText('sendEmail.recipientPlaceholder') as HTMLInputElement;
    expect(input.value).toBe('');
  });

  it('disables send button when email input is empty', () => {
    renderDialog({
      brandRawData: { email: null, pic_name: null, store_link: null, kategori: null },
    });
    const sendBtn = screen.getByRole('button', { name: /sendEmail\.send/i });
    expect(sendBtn).toBeDisabled();
  });

  it('disables send button when email input has invalid format', () => {
    renderDialog({
      brandRawData: { email: null, pic_name: null, store_link: null, kategori: null },
    });
    const input = screen.getByPlaceholderText('sendEmail.recipientPlaceholder');
    fireEvent.change(input, { target: { value: 'not-an-email' } });
    const sendBtn = screen.getByRole('button', { name: /sendEmail\.send/i });
    expect(sendBtn).toBeDisabled();
  });

  it('enables send button when email input has valid format', () => {
    renderDialog();
    const sendBtn = screen.getByRole('button', { name: /sendEmail\.send/i });
    expect(sendBtn).toBeEnabled();
  });

  it('shows "sendEmail.sending" text and disables input and buttons when loading', () => {
    mockMutationReturn = { ...mockMutationReturn, isPending: true };
    renderDialog();
    expect(screen.getByText('sendEmail.sending')).toBeInTheDocument();
    const input = screen.getByPlaceholderText('sendEmail.recipientPlaceholder') as HTMLInputElement;
    expect(input).toBeDisabled();
    const cancelBtn = screen.getByRole('button', { name: /sendEmail\.cancel/i });
    expect(cancelBtn).toBeDisabled();
  });

  it('shows error message and "sendEmail.retry" button text when isError', () => {
    mockMutationReturn = { ...mockMutationReturn, isError: true };
    renderDialog();
    expect(screen.getByText('sendEmail.error')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sendEmail\.retry/i })).toBeInTheDocument();
  });

  it('shows capture error message when chart capture fails', async () => {
    mockToPng.mockRejectedValue(new Error('canvas error'));
    renderDialog();

    const sendBtn = screen.getByRole('button', { name: /sendEmail\.send/i });
    fireEvent.click(sendBtn);

    await waitFor(() => {
      expect(screen.getByText('sendEmail.captureError')).toBeInTheDocument();
    });
    expect(mockMutate).not.toHaveBeenCalled();
  });

  it('calls onSuccess callback on successful send', async () => {
    mockToPng.mockResolvedValue('data:image/png;base64,abc123');
    mockMutate.mockImplementation((_params: unknown, opts: { onSuccess?: () => void }) => {
      opts.onSuccess?.();
    });

    const { props } = renderDialog();

    const sendBtn = screen.getByRole('button', { name: /sendEmail\.send/i });
    fireEvent.click(sendBtn);

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalled();
      expect(props.onSuccess).toHaveBeenCalled();
    });
  });

  it('calls mutation.reset() when dialog closes', () => {
    const { props } = renderDialog();
    // Simulate closing
    (props.onOpenChange as ReturnType<typeof vi.fn>)(false);
    // The component's onOpenChange wrapper calls reset
    // We need to trigger the Dialog's onOpenChange
    // Since we mocked onOpenChange, we verify through the component behavior
    // Let's click cancel instead which triggers onOpenChange(false)
    const cancelBtn = screen.getByRole('button', { name: /sendEmail\.cancel/i });
    fireEvent.click(cancelBtn);
    expect(mockReset).toHaveBeenCalled();
  });
});
