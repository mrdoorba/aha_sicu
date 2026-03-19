import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { DowntimeWarningDialog } from './DowntimeWarningDialog';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'id', changeLanguage: vi.fn() },
  }),
  Trans: ({ i18nKey }: { i18nKey: string }) => i18nKey,
}));

const defaultProps = {
  open: true,
  onDismiss: vi.fn(),
};

describe('DowntimeWarningDialog', () => {
  it('should render downtime title when open', () => {
    render(<DowntimeWarningDialog {...defaultProps} />);

    expect(screen.getByText('downtime.title')).toBeInTheDocument();
  });

  it('should render downtime description when open', () => {
    render(<DowntimeWarningDialog {...defaultProps} />);

    expect(screen.getByText('downtime.description')).toBeInTheDocument();
  });

  it('should render dismiss button when open', () => {
    render(<DowntimeWarningDialog {...defaultProps} />);

    expect(screen.getByRole('button', { name: 'downtime.dismiss' })).toBeInTheDocument();
  });

  it('should call onDismiss when dismiss button clicked', async () => {
    const onDismiss = vi.fn();
    const user = userEvent.setup();
    render(<DowntimeWarningDialog open onDismiss={onDismiss} />);

    await user.click(screen.getByRole('button', { name: 'downtime.dismiss' }));

    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it('should not render when closed', () => {
    render(<DowntimeWarningDialog open={false} onDismiss={vi.fn()} />);

    expect(screen.queryByText('downtime.title')).not.toBeInTheDocument();
  });
});
