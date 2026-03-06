import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { DashboardHeader } from './DashboardHeader';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

function renderHeader(overrides: Record<string, unknown> = {}) {
  const defaultProps = {
    brandName: 'Test Brand',
    brandId: 1,
    verdict: 'Disetujui',
    template: 'fashion',
    period: 'Jan 2026',
    onBack: vi.fn(),
    ...overrides,
  };

  return {
    ...render(
      <MemoryRouter>
        <DashboardHeader {...defaultProps} />
      </MemoryRouter>,
    ),
    props: defaultProps,
  };
}

describe('DashboardHeader', () => {
  it('renders "Kirim Email" button when onSendEmail prop is provided', () => {
    renderHeader({ onSendEmail: vi.fn() });
    expect(screen.getByRole('button', { name: /sendEmail\.sendButton/i })).toBeInTheDocument();
  });

  it('does not render "Kirim Email" button when onSendEmail is undefined', () => {
    renderHeader();
    expect(screen.queryByRole('button', { name: /sendEmail\.sendButton/i })).not.toBeInTheDocument();
  });

  it('fires onSendEmail callback when "Kirim Email" button is clicked', () => {
    const onSendEmail = vi.fn();
    renderHeader({ onSendEmail });

    const sendButton = screen.getByRole('button', { name: /sendEmail\.sendButton/i });
    fireEvent.click(sendButton);

    expect(onSendEmail).toHaveBeenCalledTimes(1);
  });
});
