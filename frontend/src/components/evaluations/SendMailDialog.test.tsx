import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SendMailDialog } from './SendMailDialog';
import { buildSubject, buildBody } from './sendMailUtils';

const mockMutate = vi.fn();
const mockToastSuccess = vi.fn();
const mockToastError = vi.fn();

vi.mock('../../hooks/useSendPlainEmail', () => ({
  useSendPlainEmail: () => ({
    mutate: mockMutate,
    isPending: false,
  }),
}));

vi.mock('sonner', () => ({
  toast: {
    success: (...args: unknown[]) => mockToastSuccess(...args),
    error: (...args: unknown[]) => mockToastError(...args),
  },
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, options?: Record<string, unknown>) => {
      const map: Record<string, string> = {
        'sendMail.title': 'Kirim Email',
        'sendMail.description': 'Dialog kirim email',
        'sendMail.to': 'Kepada',
        'sendMail.picEmail': 'Email PIC',
        'sendMail.subject': 'Subjek',
        'sendMail.body': 'Isi Email',
        'sendMail.send': 'Kirim Email',
        'sendMail.cancel': 'Batal',
      };
      if (map[key]) return map[key];
      if (options && typeof options.defaultValue === 'string') {
        return options.defaultValue as string;
      }
      return key;
    },
  }),
}));

const defaultProps = {
  open: true,
  onOpenChange: vi.fn(),
  evaluationId: 42,
  brandName: 'Nike Indonesia',
  period: 'Jan 2026',
  emailOutput: 'Skor akhir: 78.5\nKesimpulan: Layak.',
  brandRawData: {
    email: 'pic@nike.com',
    pic_name: 'Budi Santoso',
    store_link: 'https://shopee.co.id/nike',
    kategori: 'Fashion',
  },
};

let queryClient: QueryClient;

const renderDialog = (props = {}) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <SendMailDialog {...defaultProps} {...props} />
    </QueryClientProvider>,
  );
};

const clickSend = async () => {
  const user = userEvent.setup();
  const sendButtons = screen.getAllByText('Kirim Email');
  const sendButton = sendButtons.find((el) => el.closest('button') !== null)!;
  await user.click(sendButton.closest('button')!);
};

describe('SendMailDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    });
  });

  it('renders dialog title', () => {
    renderDialog();
    expect(screen.getByRole('heading', { name: 'Kirim Email' })).toBeInTheDocument();
  });

  it('defaults "Kepada" field to bot@ahacommerce.net', () => {
    renderDialog();
    const toInput = screen.getByLabelText('Kepada');
    expect(toInput).toHaveValue('bot@ahacommerce.net');
  });

  it('defaults "Email PIC" field to brand_raw_data.email', () => {
    renderDialog();
    const picInput = screen.getByLabelText('Email PIC');
    expect(picInput).toHaveValue('pic@nike.com');
  });

  it('shows empty "Email PIC" when brand_raw_data.email is null', () => {
    renderDialog({
      brandRawData: { email: null, pic_name: null, store_link: null, kategori: null },
    });
    const picInput = screen.getByLabelText('Email PIC');
    expect(picInput).toHaveValue('');
  });

  it('displays reconstructed email subject with Indonesian month', () => {
    renderDialog();
    const subject = screen.getByTestId('mail-subject');
    expect(subject).toHaveTextContent(
      '\u{1F3E5} AHA Store Internal Check Up (Store ICU) - Nike Indonesia Jan 2026',
    );
  });

  it('displays composed email body with greeting header and email_output', () => {
    renderDialog();
    const body = screen.getByTestId('mail-body');
    expect(body).toHaveTextContent('[EMAIL TO: pic@nike.com]');
    expect(body).toHaveTextContent('Kepada Pimpinan Nike Indonesia (Bapak/Ibu Budi Santoso)');
    expect(body).toHaveTextContent('https://shopee.co.id/nike');
    expect(body).toHaveTextContent('kategori Fashion');
    expect(body).toHaveTextContent('Skor akhir: 78.5');
  });

  it('updates [EMAIL TO:] line when PIC email field changes', async () => {
    const user = userEvent.setup();
    renderDialog();

    const picInput = screen.getByLabelText('Email PIC');
    await user.clear(picInput);
    await user.type(picInput, 'new@brand.com');

    const body = screen.getByTestId('mail-body');
    expect(body).toHaveTextContent('[EMAIL TO: new@brand.com]');
  });

  it('fires sendPlainEmail mutation with evaluationId, To, subject, and body on "Kirim Email"', async () => {
    renderDialog();
    await clickSend();

    expect(mockMutate).toHaveBeenCalledTimes(1);
    const [params] = mockMutate.mock.calls[0];
    expect(params.evaluationId).toBe(42);
    expect(params.recipients).toEqual(['bot@ahacommerce.net']);
    expect(params.subject).toContain('Nike Indonesia');
    expect(params.subject).toContain('Jan 2026');
    expect(params.body).toContain('[EMAIL TO: pic@nike.com]');
    expect(params.body).toContain('Skor akhir: 78.5');
  });

  it('closes dialog and toasts success on mutation success', async () => {
    mockMutate.mockImplementation((_params, { onSuccess }) => onSuccess?.());
    const onOpenChange = vi.fn();
    renderDialog({ onOpenChange });
    await clickSend();

    expect(mockToastSuccess).toHaveBeenCalledWith('Email sent.');
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it('toasts error and keeps dialog open on mutation error', async () => {
    mockMutate.mockImplementation((_params, { onError }) =>
      onError?.(new Error('SMTP auth failed')),
    );
    const onOpenChange = vi.fn();
    renderDialog({ onOpenChange });
    await clickSend();

    expect(mockToastError).toHaveBeenCalledTimes(1);
    expect(mockToastError.mock.calls[0][0]).toContain('Failed to send email');
    expect(mockToastError.mock.calls[0][0]).toContain('SMTP auth failed');
    expect(onOpenChange).not.toHaveBeenCalledWith(false);
  });

  it('uses edited "Kepada" value as the mutation recipient', async () => {
    const user = userEvent.setup();
    renderDialog();

    const toInput = screen.getByLabelText('Kepada');
    await user.clear(toInput);
    await user.type(toInput, 'custom@recipient.com');
    await clickSend();

    expect(mockMutate).toHaveBeenCalledTimes(1);
    expect(mockMutate.mock.calls[0][0].recipients).toEqual(['custom@recipient.com']);
  });

  it('calls onOpenChange(false) when cancel button is clicked', async () => {
    const onOpenChange = vi.fn();
    const user = userEvent.setup();
    renderDialog({ onOpenChange });

    const cancelButton = screen.getByRole('button', { name: /batal/i });
    await user.click(cancelButton);

    expect(onOpenChange).toHaveBeenCalledWith(false);
  });
});


describe('buildSubject', () => {
  it('formats subject with brand name and period', () => {
    expect(buildSubject('Salt', 'Jan 2026')).toBe(
      '[ID] \u{1F3E5} AHA Store Internal Check Up (Store ICU) - Salt Jan 2026',
    );
  });

  it('handles different periods correctly', () => {
    expect(buildSubject('Brand', 'Mei 2026')).toContain('Mei 2026');
    expect(buildSubject('Brand', 'Des 2026')).toContain('Des 2026');
  });
});

describe('buildBody', () => {
  it('composes body with greeting header and email output', () => {
    const body = buildBody(
      'pic@test.com',
      'TestBrand',
      'John',
      'https://shopee.co.id/test',
      'Electronics',
      'Score: 80',
    );
    expect(body).toContain('[EMAIL TO: pic@test.com]');
    expect(body).toContain('Kepada Pimpinan TestBrand (Bapak/Ibu John)');
    expect(body).toContain('https://shopee.co.id/test');
    expect(body).toContain('kategori Electronics');
    expect(body).toContain('Score: 80');
  });

  it('handles empty values gracefully', () => {
    const body = buildBody('', 'Brand', '', '', '', 'output');
    expect(body).toContain('[EMAIL TO: ]');
    expect(body).toContain('(Bapak/Ibu )');
    expect(body).toContain('output');
  });

  it('uses emailBodyOverride when provided', () => {
    const body = buildBody(
      'pic@test.com',
      'TestBrand',
      'John',
      'https://shopee.co.id/test',
      'Electronics',
      'Original email output',
      undefined,
      'Override body content',
    );
    expect(body).toContain('Override body content');
    expect(body).not.toContain('Original email output');
  });

  it('uses optional TFunction for translations', () => {
    const mockT = ((key: string, vars?: Record<string, unknown>) => {
      if (key === 'sendMailUtils.salutation') return `Dear ${vars?.brandName} (${vars?.picName})`;
      if (key === 'sendMailUtils.intro') return `Intro for ${vars?.brandName}`;
      return key;
    }) as unknown as import('i18next').TFunction;

    const body = buildBody(
      'pic@test.com',
      'TestBrand',
      'John',
      'https://shopee.co.id/test',
      'Electronics',
      'Score: 80',
      mockT,
    );
    expect(body).toContain('Dear TestBrand (John)');
    expect(body).toContain('Intro for TestBrand');
  });
});

describe('SendMailDialog — language selector', () => {
  it('renders language selector in the dialog', () => {
    renderDialog();
    expect(screen.getByTestId('email-language-select')).toBeInTheDocument();
  });

  it('works without scoreBreakdown (old evaluations) — no regression', () => {
    renderDialog();
    expect(screen.getByLabelText('Kepada')).toBeInTheDocument();
    expect(screen.getByLabelText('Email PIC')).toBeInTheDocument();
    expect(screen.getByTestId('mail-subject')).toBeInTheDocument();
    expect(screen.getByTestId('mail-body')).toBeInTheDocument();
    expect(screen.getByTestId('mail-body')).toHaveTextContent('Skor akhir: 78.5');
  });

  it('subject updates via buildSubject with TFunction when scoreBreakdown has i18n data', () => {
    const scoreBreakdown = [
      {
        category: 'Operations',
        score: 10,
        max_score: 15,
        available: true,
        rows: [
          {
            row: 1,
            metric: 'Test',
            value: 100,
            benchmark: '>50',
            verdict: '✔️',
            message: 'Good',
            message_i18n: { key: 'scoring.ops.good', vars: {} },
            score: 5,
          },
        ],
      },
    ];

    renderDialog({ scoreBreakdown });

    const subject = screen.getByTestId('mail-subject');
    expect(subject).toHaveTextContent('AHA Store Internal Check Up');
    expect(subject).toHaveTextContent('Nike Indonesia');
  });

  it('body uses i18n body override when scoreBreakdown with i18n data is provided', () => {
    const scoreBreakdown = [
      {
        category: 'Operations',
        score: 10,
        max_score: 15,
        available: true,
        rows: [
          {
            row: 1,
            metric: 'Test',
            value: 100,
            benchmark: '>50',
            verdict: '✔️',
            message: 'Good',
            message_i18n: { key: 'scoring.ops.good', vars: {} },
            score: 5,
          },
        ],
      },
    ];

    renderDialog({ scoreBreakdown });

    const body = screen.getByTestId('mail-body');
    expect(body).toHaveTextContent('[EMAIL TO: pic@nike.com]');
    expect(body).toHaveTextContent('Kepada Pimpinan Nike Indonesia');
  });

  it('Thai language compose still fires the SMTP mutation', async () => {
    const scoreBreakdown = [
      {
        category: 'Operations',
        score: 10,
        max_score: 15,
        available: true,
        rows: [
          {
            row: 1,
            metric: 'Test',
            value: 100,
            benchmark: '>50',
            verdict: '✔️',
            message: 'Good',
            message_i18n: { key: 'scoring.ops.good', vars: {} },
            score: 5,
          },
        ],
      },
    ];

    const user = userEvent.setup();
    renderDialog({ scoreBreakdown });

    await user.selectOptions(screen.getByTestId('email-language-select'), 'th');
    await clickSend();

    expect(mockMutate).toHaveBeenCalledTimes(1);
    const [params] = mockMutate.mock.calls[0];
    expect(params.evaluationId).toBe(42);
    expect(params.subject.length).toBeGreaterThan(0);
    expect(params.body.length).toBeGreaterThan(0);
  });

  it('resets language when dialog closes', async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    renderDialog({ onOpenChange });

    const select = screen.getByTestId('email-language-select');
    await user.selectOptions(select, 'th');

    const cancelButton = screen.getByRole('button', { name: /batal/i });
    await user.click(cancelButton);

    expect(onOpenChange).toHaveBeenCalledWith(false);
  });
});
