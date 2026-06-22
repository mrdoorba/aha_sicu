import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { EmailOutput } from './EmailOutput';
import type { ScoringResult } from '../../../hooks/useScoring';

// The per-language re-render POSTs the in-memory result to /email/preview. The
// hook is mocked to return language-tagged text so the selector behaviour is
// observable without a backend.
vi.mock('../../../hooks/usePreviewEmailTextFromResult', () => ({
  usePreviewEmailTextFromResult: (
    _result: ScoringResult | null | undefined,
    language: string,
  ) => ({ data: language === 'id' ? undefined : `BODY[${language}]` }),
}));

/**
 * Build a minimal ScoringResult fixture. The email body/subject now come from
 * the unified backend renderer and are surfaced verbatim on the scoring result.
 */
function makeScoringResult(overrides: Partial<ScoringResult> = {}): ScoringResult {
  return {
    total_score: 85,
    verdict: '✔️',
    conclusion: 'Layak',
    marketing_estimation: 'Estimasi pemasaran',
    marketing_percentage: '3%',
    marketing_budget: 'IDR 10.000.000',
    closing_message: 'Terima kasih',
    email_subject: 'Backend Subject',
    email_body: 'Backend rendered body',
    template: 'fashion',
    rule_version: 1,
    category_scores: [],
    ...overrides,
  };
}

describe('EmailOutput', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders subject and body from props when no scoringResult', () => {
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

  it('copies prop text to clipboard on click', async () => {
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

  it('prefers the backend-rendered subject and body from scoringResult', () => {
    const scoringResult = makeScoringResult();
    render(
      <EmailOutput
        subject="Prop subject that should NOT appear"
        body="Prop body that should NOT appear"
        scoringResult={scoringResult}
      />,
    );
    expect(screen.getByText('Backend Subject')).toBeInTheDocument();
    expect(screen.getByText('Backend rendered body')).toBeInTheDocument();
    expect(screen.queryByText('Prop body that should NOT appear')).not.toBeInTheDocument();
  });

  it('renders the language selector when scoringResult is present', () => {
    const scoringResult = makeScoringResult();
    render(
      <EmailOutput subject="Subject" body="Body" scoringResult={scoringResult} />,
    );
    expect(screen.getByTestId('email-language-select')).toBeInTheDocument();
  });

  it('does NOT render the language selector without scoringResult', () => {
    render(<EmailOutput subject="Subject" body="Body" />);
    expect(screen.queryByTestId('email-language-select')).not.toBeInTheDocument();
  });

  it('shows the scoring email_body initially (id default, no flash)', () => {
    const scoringResult = makeScoringResult();
    render(
      <EmailOutput subject="Subject" body="Body" scoringResult={scoringResult} />,
    );
    // Default language is id → hook returns undefined → fall back to email_body.
    expect(screen.getByText('Backend rendered body')).toBeInTheDocument();
  });

  it('switching language re-renders the displayed body from the preview', async () => {
    const user = userEvent.setup();
    const scoringResult = makeScoringResult();
    render(
      <EmailOutput subject="Subject" body="Body" scoringResult={scoringResult} />,
    );

    await user.selectOptions(screen.getByTestId('email-language-select'), 'th');
    expect(screen.getByText('BODY[th]')).toBeInTheDocument();
    expect(screen.queryByText('Backend rendered body')).not.toBeInTheDocument();
  });

  it('falls back to prop body when scoringResult is null', () => {
    render(
      <EmailOutput subject="Subject" body="Fallback body text" scoringResult={null} />,
    );
    expect(screen.getByText('Fallback body text')).toBeInTheDocument();
  });

  it('copies the backend-rendered text when scoringResult present', async () => {
    const user = userEvent.setup();
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText },
      writable: true,
      configurable: true,
    });

    const scoringResult = makeScoringResult();
    render(
      <EmailOutput subject="Prop subject" body="Prop body" scoringResult={scoringResult} />,
    );
    await user.click(screen.getByRole('button', { name: /salin/i }));

    expect(writeText).toHaveBeenCalledWith('Subject: Backend Subject\n\nBackend rendered body');
  });
});
