import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { CurrencyField } from './CurrencyField';

describe('CurrencyField', () => {
  it('renders label with IDR unit', () => {
    render(
      <CurrencyField name="test" label="Sales" value={null} onChange={vi.fn()} />,
    );
    expect(screen.getByLabelText(/Sales/)).toBeInTheDocument();
    expect(screen.getByText('(IDR)')).toBeInTheDocument();
  });

  it('formats value as plain number when not focused', () => {
    render(
      <CurrencyField name="test" label="Sales" value={125000000} onChange={vi.fn()} />,
    );
    expect(screen.getByRole('textbox')).toHaveValue('125000000');
  });

  it('shows raw number when focused', async () => {
    const user = userEvent.setup();
    render(
      <CurrencyField name="test" label="Sales" value={125000000} onChange={vi.fn()} />,
    );
    await user.click(screen.getByRole('textbox'));
    expect(screen.getByRole('textbox')).toHaveValue('125000000');
  });

  it('formats back to plain number on blur', async () => {
    const user = userEvent.setup();
    render(
      <CurrencyField name="test" label="Sales" value={50000} onChange={vi.fn()} />,
    );
    const input = screen.getByRole('textbox');
    await user.click(input);
    expect(input).toHaveValue('50000');
    await user.tab();
    expect(input).toHaveValue('50000');
  });

  it('calls onChange with parsed number', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(
      <CurrencyField name="test" label="Sales" value={null} onChange={onChange} />,
    );
    await user.click(screen.getByRole('textbox'));
    await user.type(screen.getByRole('textbox'), '1000');
    // onChange should be called with numeric values
    expect(onChange).toHaveBeenCalled();
    const lastCall = onChange.mock.calls[onChange.mock.calls.length - 1][0];
    expect(typeof lastCall).toBe('number');
  });

  it('renders benchmark text when provided', () => {
    render(
      <CurrencyField name="test" label="Sales" value={null} onChange={vi.fn()} benchmark=">8% dari penjualan" />,
    );
    expect(screen.getByText('Benchmark: >8% dari penjualan')).toBeInTheDocument();
  });

  it('shows empty string for null value', () => {
    render(
      <CurrencyField name="test" label="Sales" value={null} onChange={vi.fn()} />,
    );
    expect(screen.getByRole('textbox')).toHaveValue('');
  });
});
