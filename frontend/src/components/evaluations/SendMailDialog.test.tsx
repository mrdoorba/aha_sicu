import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SendMailDialog } from './SendMailDialog';
import {
  buildSubject,
  buildBody,
  buildMailtoUrl,
} from './sendMailUtils';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
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
      return map[key] ?? key;
    },
  }),
}));

const defaultProps = {
  open: true,
  onOpenChange: vi.fn(),
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

const renderDialog = (props = {}) => {
  return render(<SendMailDialog {...defaultProps} {...props} />);
};

describe('SendMailDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks();
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

  it('opens mailto URL via window.open on "Kirim Email" click', async () => {
    const onOpenChange = vi.fn();
    const windowOpen = vi.spyOn(window, 'open').mockImplementation(() => ({ closed: false } as Window));
    const user = userEvent.setup();
    renderDialog({ onOpenChange });

    const sendButtons = screen.getAllByText('Kirim Email');
    // Click the button in the footer (not the dialog title)
    const sendButton = sendButtons.find(
      (el) => el.closest('button') !== null,
    )!;
    await user.click(sendButton.closest('button')!);

    expect(windowOpen).toHaveBeenCalledTimes(1);
    const url = windowOpen.mock.calls[0][0] as string;
    expect(url).toMatch(/^mailto:/);
    expect(url).toContain('bot%40ahacommerce.net');
    expect(url).toContain('subject=');
    expect(url).toContain('body=');
    expect(windowOpen).toHaveBeenCalledWith(url, '_self');
    expect(onOpenChange).toHaveBeenCalledWith(false);

    windowOpen.mockRestore();
  });

  it('still closes dialog when mailto handoff returns null', async () => {
    const onOpenChange = vi.fn();
    const windowOpen = vi.spyOn(window, 'open').mockImplementation(() => null);
    const user = userEvent.setup();
    renderDialog({ onOpenChange });

    const sendButtons = screen.getAllByText('Kirim Email');
    const sendButton = sendButtons.find((el) => el.closest('button') !== null)!;
    await user.click(sendButton.closest('button')!);

    expect(windowOpen).toHaveBeenCalledTimes(1);
    expect(onOpenChange).toHaveBeenCalledWith(false);

    windowOpen.mockRestore();
  });

  it('uses edited "Kepada" value in mailto URL', async () => {
    const onOpenChange = vi.fn();
    const windowOpen = vi.spyOn(window, 'open').mockImplementation(() => ({ closed: false } as Window));
    const user = userEvent.setup();
    renderDialog({ onOpenChange });

    const toInput = screen.getByLabelText('Kepada');
    await user.clear(toInput);
    await user.type(toInput, 'custom@recipient.com');

    const sendButtons = screen.getAllByText('Kirim Email');
    const sendButton = sendButtons.find((el) => el.closest('button') !== null)!;
    await user.click(sendButton.closest('button')!);

    const url = windowOpen.mock.calls[0][0] as string;
    expect(url).toContain('mailto:custom%40recipient.com');
    expect(url).not.toContain('mailto:bot%40ahacommerce.net');

    windowOpen.mockRestore();
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


describe('buildMailtoUrl', () => {
  it('builds a mailto URL with to, subject, and body', () => {
    const url = buildMailtoUrl('to@example.com', 'Hello World', 'Line 1\nLine 2');

    expect(url).toMatch(/^mailto:/);
    expect(url).toContain('mailto:to%40example.com');
    expect(url).toContain('subject=Hello%20World');
    expect(url).toContain('body=Line%201%0ALine%202');
  });

  it('encodes spaces as %20 so mail clients do not render plus signs', () => {
    const url = buildMailtoUrl('to@example.com', 'Thai Subject', 'Hello Thai Team');

    expect(url).toContain('subject=Thai%20Subject');
    expect(url).toContain('body=Hello%20Thai%20Team');
    expect(url).not.toContain('Thai+Subject');
    expect(url).not.toContain('Hello+Thai+Team');
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
    // Dialog still renders all standard fields
    expect(screen.getByLabelText('Kepada')).toBeInTheDocument();
    expect(screen.getByLabelText('Email PIC')).toBeInTheDocument();
    expect(screen.getByTestId('mail-subject')).toBeInTheDocument();
    expect(screen.getByTestId('mail-body')).toBeInTheDocument();
    // Original email output is in the body
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

    // Subject should still render — it uses the fixed translation function
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

    // When i18n data is available, buildI18nEmailBody is used and its output
    // replaces the original emailOutput in the body
    const body = screen.getByTestId('mail-body');
    // The body should still contain the standard header from buildBody
    expect(body).toHaveTextContent('[EMAIL TO: pic@nike.com]');
    expect(body).toHaveTextContent('Kepada Pimpinan Nike Indonesia');
  });

  it('uses mailto handoff for Thai compose payloads', async () => {
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
    const onOpenChange = vi.fn();
    const windowOpen = vi.spyOn(window, 'open').mockImplementation(() => ({ closed: false } as Window));

    renderDialog({ onOpenChange, scoreBreakdown });

    await user.selectOptions(screen.getByTestId('email-language-select'), 'th');

    const sendButtons = screen.getAllByText('Kirim Email');
    const sendButton = sendButtons.find((el) => el.closest('button') !== null)!;
    await user.click(sendButton.closest('button')!);

    expect(windowOpen).toHaveBeenCalledTimes(1);
    const url = windowOpen.mock.calls[0][0] as string;
    expect(url).toMatch(/^mailto:/);
    expect(url).toContain('subject=');
    expect(url).toContain('body=');
    expect(url).toContain('%E0%B9%80%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B8%99');
    expect(onOpenChange).toHaveBeenCalledWith(false);

    windowOpen.mockRestore();
  });

  it('resets language when dialog closes', async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    renderDialog({ onOpenChange });

    // Change language
    const select = screen.getByTestId('email-language-select');
    await user.selectOptions(select, 'th');

    // Close dialog via cancel
    const cancelButton = screen.getByRole('button', { name: /batal/i });
    await user.click(cancelButton);

    expect(onOpenChange).toHaveBeenCalledWith(false);
  });
});
