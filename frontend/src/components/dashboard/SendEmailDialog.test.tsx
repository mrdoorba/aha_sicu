import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// -- Mocks --

const mockMutate = vi.fn();
const mockReset = vi.fn();

vi.mock('../../hooks/useSendEmail', () => ({
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

const mockCaptureChart = vi.fn();
vi.mock('../../lib/captureChart', () => ({
  captureChartAsPng: (...args: unknown[]) => mockCaptureChart(...args),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, opts?: Record<string, unknown>) => {
      if (opts?.count !== undefined) return `${key} ${opts.count}`;
      if (opts?.recipient) return `${key} ${opts.recipient}`;
      return key;
    },
    i18n: { language: 'id' },
  }),
}));

const mockToastSuccess = vi.fn();
vi.mock('sonner', () => ({
  toast: { success: (...args: unknown[]) => mockToastSuccess(...args) },
}));

vi.mock('../../firebase/auth', () => ({
  getCurrentUserToken: vi.fn().mockResolvedValue('mock-token'),
}));

vi.mock('../../config', () => ({
  API_BASE_URL: 'http://localhost:8000',
}));

const mockFixedT = (key: string, opts?: Record<string, unknown>) => {
  if (opts) {
    return Object.entries(opts).reduce(
      (acc, [k, v]) => acc.replace(`{{${k}}}`, String(v ?? '')),
      key,
    );
  }
  return key;
};
vi.mock('../../i18n', () => ({
  default: {
    language: 'id',
    getFixedT: () => mockFixedT,
  },
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
    mockCaptureChart.mockReset();
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

  it('pre-fills PIC email as first chip in To field', () => {
    renderDialog();
    expect(screen.getByText('pic@example.com')).toBeInTheDocument();
  });

  it('shows empty To field when brandRawData.email is null', () => {
    renderDialog({
      brandRawData: { email: null, pic_name: null, store_link: null, kategori: null },
    });
    // Placeholder should be visible when no chips exist
    expect(screen.getByPlaceholderText('sendEmail.recipientPlaceholder')).toBeInTheDocument();
    // The chip for pic email should NOT be there
    expect(screen.queryByText('pic@example.com')).not.toBeInTheDocument();
  });

  it('disables send button when no To recipients', () => {
    renderDialog({
      brandRawData: { email: null, pic_name: null, store_link: null, kategori: null },
    });
    const sendBtn = screen.getByRole('button', { name: /sendEmail\.send/i });
    expect(sendBtn).toBeDisabled();
  });

  it('enables send button when To recipients exist', () => {
    renderDialog();
    const sendBtn = screen.getByRole('button', { name: /sendEmail\.send/i });
    expect(sendBtn).toBeEnabled();
  });

  it('shows CC field pre-filled with default CC for ID language', () => {
    renderDialog();
    // CC field should be visible by default (pre-filled with ID defaults)
    expect(screen.getByText('sendEmail.cc')).toBeInTheDocument();
    // CC toggle button should not be present since CC is already shown
    expect(screen.queryByRole('button', { name: 'CC' })).not.toBeInTheDocument();
  });

  it('shows BCC link and clicking it reveals BCC field', () => {
    renderDialog();
    const bccLink = screen.getByRole('button', { name: 'BCC' });
    expect(bccLink).toBeInTheDocument();
    fireEvent.click(bccLink);
    expect(screen.getByText('sendEmail.bcc')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'BCC' })).not.toBeInTheDocument();
  });

  it('shows "sendEmail.sending" text and disables buttons when loading', () => {
    mockMutationReturn = { ...mockMutationReturn, isPending: true };
    renderDialog();
    expect(screen.getByRole('button', { name: /sendEmail\.sending/i })).toBeInTheDocument();
    const cancelBtn = screen.getByRole('button', { name: /sendEmail\.cancel/i });
    expect(cancelBtn).toBeDisabled();
  });

  it('shows error message and "sendEmail.retry" button text when isError', () => {
    mockMutationReturn = { ...mockMutationReturn, isError: true };
    renderDialog();
    expect(screen.getByText('sendEmail.error')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sendEmail\.retry/i })).toBeInTheDocument();
  });

  it('proceeds with send when chart capture fails (chart is optional)', async () => {
    mockCaptureChart.mockRejectedValue(new Error('canvas error'));
    renderDialog();

    const sendBtn = screen.getByRole('button', { name: /sendEmail\.send/i });
    fireEvent.click(sendBtn);

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalled();
    });
    // Chart image should be empty string when capture fails
    expect(mockMutate.mock.calls[0][0].chartImage).toBe('');
  });

  it('renders note textarea pre-filled with default opening message', () => {
    renderDialog();
    const textarea = screen.getByPlaceholderText('sendEmail.notePlaceholder') as HTMLTextAreaElement;
    expect(textarea).toBeInTheDocument();
    expect(textarea.value).toContain('sendMailUtils.salutation');
    expect(textarea.value).toContain('sendMailUtils.intro');
    expect(screen.getByText(`${textarea.value.length}/500`)).toBeInTheDocument();
  });

  it('updates character count as note is typed', () => {
    renderDialog();
    const textarea = screen.getByPlaceholderText('sendEmail.notePlaceholder');
    fireEvent.change(textarea, { target: { value: 'Hello' } });
    expect(screen.getByText('5/500')).toBeInTheDocument();
  });

  it('note textarea respects 500-char maxLength', () => {
    renderDialog();
    const textarea = screen.getByPlaceholderText('sendEmail.notePlaceholder') as HTMLTextAreaElement;
    expect(textarea.maxLength).toBe(500);
  });

  it('preview toggle shows preview section', () => {
    // Mock the fetch for preview
    global.fetch = vi.fn().mockResolvedValue({
      text: () => Promise.resolve('<html><body>Preview</body></html>'),
    });

    renderDialog();
    const toggleBtn = screen.getByRole('button', { name: /sendEmail\.previewToggle/i });
    expect(toggleBtn).toBeInTheDocument();
    fireEvent.click(toggleBtn);

    // Should show loading or preview container
    expect(screen.getByText('sendEmail.previewLoading')).toBeInTheDocument();
  });

  it('sends correct payload shape with recipients array, cc, bcc, note', async () => {
    mockCaptureChart.mockResolvedValue('abc123');
    mockMutate.mockImplementation(
      (_params: Record<string, unknown>, opts?: { onSuccess?: () => void }) => {
        opts?.onSuccess?.();
      },
    );

    renderDialog();

    // Add a note
    const textarea = screen.getByPlaceholderText('sendEmail.notePlaceholder');
    fireEvent.change(textarea, { target: { value: 'Test note' } });

    const sendBtn = screen.getByRole('button', { name: /sendEmail\.send/i });

    await act(async () => {
      fireEvent.click(sendBtn);
      await Promise.resolve();
    });

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalled();
      const [params] = mockMutate.mock.calls[0];
      expect(params.recipients).toEqual(['pic@example.com']);
      expect(params.chartImage).toBe('abc123');
      expect(params.note).toBe('Test note');
    });
  });

  it('calls onSuccess callback on successful send', async () => {
    mockCaptureChart.mockResolvedValue('abc123');
    mockMutate.mockImplementation(
      (_params: Record<string, unknown>, opts?: { onSuccess?: () => void }) => {
        opts?.onSuccess?.();
      },
    );

    const { props } = renderDialog();

    const sendBtn = screen.getByRole('button', { name: /sendEmail\.send/i });

    await act(async () => {
      fireEvent.click(sendBtn);
      await Promise.resolve();
    });

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalled();
      expect(props.onSuccess).toHaveBeenCalled();
    });
  });

  it('calls mutation.reset() when dialog closes', () => {
    renderDialog();
    const cancelBtn = screen.getByRole('button', { name: /sendEmail\.cancel/i });
    fireEvent.click(cancelBtn);
    expect(mockReset).toHaveBeenCalled();
  });

  // ── Language selector integration ────────────────────────────────

  it('renders email language selector in the dialog', () => {
    renderDialog();
    expect(screen.getByTestId('email-language-select')).toBeInTheDocument();
  });

  it('mutation payload includes the selected email language', async () => {
    mockCaptureChart.mockResolvedValue('abc123');
    mockMutate.mockImplementation(
      (_params: Record<string, unknown>, opts?: { onSuccess?: () => void }) => {
        opts?.onSuccess?.();
      },
    );

    renderDialog();

    // Default language should be 'id' (from mock i18n.language)
    const sendBtn = screen.getByRole('button', { name: /sendEmail\.send/i });

    await act(async () => {
      fireEvent.click(sendBtn);
      await Promise.resolve();
    });

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalled();
      const [params] = mockMutate.mock.calls[0];
      expect(params.language).toBe('id');
    });
  });

  it('sends changed language in mutation payload when selector is changed', async () => {
    mockCaptureChart.mockResolvedValue('abc123');
    mockMutate.mockImplementation(
      (_params: Record<string, unknown>, opts?: { onSuccess?: () => void }) => {
        opts?.onSuccess?.();
      },
    );

    renderDialog();

    // Change language to 'th'
    const langSelect = screen.getByTestId('email-language-select');
    fireEvent.change(langSelect, { target: { value: 'th' } });

    const sendBtn = screen.getByRole('button', { name: /sendEmail\.send/i });

    await act(async () => {
      fireEvent.click(sendBtn);
      await Promise.resolve();
    });

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalled();
      const [params] = mockMutate.mock.calls[0];
      expect(params.language).toBe('th');
    });
  });

  it('preview URL includes language param when preview is opened', async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      text: () => Promise.resolve('<html><body>Preview</body></html>'),
    });
    global.fetch = fetchSpy;

    renderDialog();

    // Change language to 'en'
    const langSelect = screen.getByTestId('email-language-select');
    fireEvent.change(langSelect, { target: { value: 'en' } });

    // Open preview
    const toggleBtn = screen.getByRole('button', { name: /sendEmail\.previewToggle/i });
    fireEvent.click(toggleBtn);

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalled();
      const fetchUrl: string = fetchSpy.mock.calls[0][0];
      expect(fetchUrl).toContain('language=en');
    });
  });

  it('refreshes preview with the new language when selector changes while preview is open', async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      text: () => Promise.resolve('<html><body>Preview</body></html>'),
    });
    global.fetch = fetchSpy;

    renderDialog();

    const toggleBtn = screen.getByRole('button', { name: /sendEmail\.previewToggle/i });
    fireEvent.click(toggleBtn);

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledTimes(1);
      const initialUrl: string = fetchSpy.mock.calls[0][0];
      expect(initialUrl).toContain('language=id');
    });

    const langSelect = screen.getByTestId('email-language-select');
    fireEvent.change(langSelect, { target: { value: 'en' } });

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledTimes(2);
      const refreshedUrl: string = fetchSpy.mock.calls[1][0];
      expect(refreshedUrl).toContain('language=en');
    });
  });
});
