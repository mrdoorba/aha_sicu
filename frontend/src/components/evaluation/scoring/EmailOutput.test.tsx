import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { EmailOutput } from './EmailOutput';
import type { ScoringResult, CategoryScore } from '../../../hooks/useScoring';

// Mock buildI18nEmailBody to return predictable content
vi.mock('../../../utils/buildI18nEmailBody', () => ({
  buildI18nEmailBody: vi.fn(
    (
      _scores: CategoryScore[],
      _summary: unknown,
      t: (key: string, vars?: Record<string, unknown>) => string,
    ) => {
      // Return translated body based on the language function
      return t('mock.emailBody', {});
    },
  ),
}));

/**
 * Build a minimal ScoringResult fixture with i18n fields.
 */
function makeScoringResult(overrides: Partial<ScoringResult> = {}): ScoringResult {
  return {
    total_score: 85,
    verdict: '✔️',
    conclusion: 'Layak',
    conclusion_i18n: [{ key: 'scoring.conclusion.pass', vars: {} }],
    marketing_estimation: 'Estimasi pemasaran',
    marketing_percentage: '3%',
    marketing_budget: 'IDR 10.000.000',
    marketing_budget_i18n: {
      key: 'scoring.marketingBudget',
      vars: { amount: '10.000.000', currency: 'IDR' },
    },
    closing_message: 'Terima kasih',
    closing_message_i18n: { key: 'scoring.closingMessage', vars: {} },
    email_subject: 'Test Subject',
    email_body: 'Original body from backend',
    template: 'fashion',
    rule_version: 1,
    category_scores: [
      {
        category: 'Kesehatan Operasional Toko',
        score: 10,
        max_score: 15,
        available: true,
        rows: [
          {
            row: 1,
            metric: 'Test metric',
            value: 100,
            benchmark: '>50',
            verdict: '✔️',
            message: 'Operasional baik',
            message_i18n: { key: 'scoring.operational.good', vars: {} },
            score: 5,
          },
        ],
      },
    ],
    ...overrides,
  };
}

describe('EmailOutput', () => {
  it('renders subject and body', () => {
    render(<EmailOutput subject="Test Subject" body="Test body content" />);
    expect(screen.getByText('Test Subject')).toBeInTheDocument();
    expect(screen.getByText('Test body content')).toBeInTheDocument();
  });

  it('renders Email Output heading', () => {
    render(<EmailOutput subject="Sub" body="Body" />);
    expect(screen.getByText('Email Output')).toBeInTheDocument();
  });

  it('has a Salin button', () => {
    render(<EmailOutput subject="Sub" body="Body" />);
    expect(screen.getByRole('button', { name: /salin/i })).toBeInTheDocument();
  });

  it('copies text to clipboard on click', async () => {
    const user = userEvent.setup();
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText },
      writable: true,
      configurable: true,
    });

    render(<EmailOutput subject="My Subject" body="My Body" />);
    await user.click(screen.getByRole('button', { name: /salin/i }));

    expect(writeText).toHaveBeenCalledWith('Subject: My Subject\n\nMy Body');
  });

  it('renders language selector when scoringResult is provided', () => {
    const scoringResult = makeScoringResult();
    render(
      <EmailOutput
        subject="Subject"
        body="Original body"
        scoringResult={scoringResult}
      />,
    );
    expect(screen.getByTestId('email-language-select')).toBeInTheDocument();
  });

  it('does NOT render language selector when scoringResult is absent', () => {
    render(<EmailOutput subject="Subject" body="Original body" />);
    expect(screen.queryByTestId('email-language-select')).not.toBeInTheDocument();
  });

  it('does NOT render language selector when scoringResult is null', () => {
    render(
      <EmailOutput subject="Subject" body="Original body" scoringResult={null} />,
    );
    expect(screen.queryByTestId('email-language-select')).not.toBeInTheDocument();
  });

  it('uses buildI18nEmailBody output when scoringResult is present', () => {
    const scoringResult = makeScoringResult();
    render(
      <EmailOutput
        subject="Subject"
        body="Original body that should NOT appear"
        scoringResult={scoringResult}
      />,
    );
    // The mock buildI18nEmailBody returns t('mock.emailBody') which resolves to the key
    // since we don't have a real translator in the test — the pre element should not
    // contain the original body
    const preElement = screen.getByText((_, el) => {
      return el?.tagName === 'PRE' && !el.textContent?.includes('Original body that should NOT appear');
    }, { selector: 'pre' });
    expect(preElement).toBeInTheDocument();
  });

  it('falls back to original body prop when scoringResult is absent', () => {
    render(<EmailOutput subject="Subject" body="Fallback body text" />);
    expect(screen.getByText('Fallback body text')).toBeInTheDocument();
  });

  it('copies dynamically-rendered text (not original props) when scoringResult present', async () => {
    const user = userEvent.setup();
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText },
      writable: true,
      configurable: true,
    });

    const scoringResult = makeScoringResult();
    render(
      <EmailOutput
        subject="My Subject"
        body="Original body"
        scoringResult={scoringResult}
      />,
    );
    await user.click(screen.getByRole('button', { name: /salin/i }));

    // The copied text should use the dynamic body, not the original body prop
    const copiedText = writeText.mock.calls[0][0] as string;
    expect(copiedText).toContain('Subject: My Subject');
    expect(copiedText).not.toContain('Original body');
  });

  it('changing language updates the displayed body text', async () => {
    const user = userEvent.setup();
    const scoringResult = makeScoringResult();

    const { buildI18nEmailBody } = await import('../../../utils/buildI18nEmailBody');
    const mockFn = vi.mocked(buildI18nEmailBody);
    // First call (initial language) returns Indonesian body
    mockFn.mockReturnValueOnce('Body Indonesia');
    // After language change, returns Thai body
    mockFn.mockReturnValueOnce('Body Thai');

    render(
      <EmailOutput
        subject="Subject"
        body="Original body"
        scoringResult={scoringResult}
      />,
    );

    // Verify initial body
    expect(screen.getByText('Body Indonesia')).toBeInTheDocument();

    // Change language to Thai
    const select = screen.getByTestId('email-language-select');
    await user.selectOptions(select, 'th');

    // Verify body updated
    expect(screen.getByText('Body Thai')).toBeInTheDocument();
  });
});
