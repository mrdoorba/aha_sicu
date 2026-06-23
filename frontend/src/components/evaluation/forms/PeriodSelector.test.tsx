import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { PeriodSelector } from './PeriodSelector';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'id' },
  }),
}));

describe('PeriodSelector', () => {
  it('renders month selector dropdown', () => {
    render(<PeriodSelector value={null} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByLabelText(/forms\.business\.startMonth/)).toBeInTheDocument();
  });

  it('calls onChange for month selector', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<PeriodSelector value={null} onChange={onChange} onBlur={vi.fn()} />);

    const select = screen.getByLabelText(/forms\.business\.startMonth/);
    await user.selectOptions(select, select.querySelector('option:nth-child(2)')!);
    expect(onChange).toHaveBeenCalledWith('business', 'salesStartMonth', expect.any(String));
  });
});
