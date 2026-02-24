import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { VerdictSelector, VERDICT_OPTIONS } from './VerdictSelector';
import i18n from '../../../i18n';

describe('VerdictSelector', () => {
  it('renders Keputusan label', () => {
    render(<VerdictSelector value="✔️" onChange={vi.fn()} />);
    expect(screen.getByText('Keputusan')).toBeInTheDocument();
  });

  it('renders the select trigger', () => {
    render(<VerdictSelector value="✔️" onChange={vi.fn()} />);
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('shows all verdict options when opened', async () => {
    const user = userEvent.setup();
    render(<VerdictSelector value="✔️" onChange={vi.fn()} />);

    await user.click(screen.getByRole('combobox'));

    for (const opt of VERDICT_OPTIONS) {
      const label = i18n.t(opt.labelKey);
      // Use getAllByText since the selected option appears in both trigger and dropdown
      const matches = screen.getAllByText(label);
      expect(matches.length).toBeGreaterThanOrEqual(1);
    }
  });

  it('has exactly 5 verdict options', () => {
    expect(VERDICT_OPTIONS).toHaveLength(5);
  });

  it('calls onChange when an option is selected', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<VerdictSelector value="✔️" onChange={onChange} />);

    await user.click(screen.getByRole('combobox'));
    await user.click(screen.getByText('❌ Ditolak'));

    expect(onChange).toHaveBeenCalledWith('❌');
  });

  it('displays the current value in the trigger', () => {
    render(<VerdictSelector value="✔️" onChange={vi.fn()} />);
    expect(screen.getByRole('combobox')).toHaveTextContent('✔️ Disetujui');
  });
});
