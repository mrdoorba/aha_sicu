import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { SelectField } from './SelectField';

const options = [
  { value: 'Shopee Mall', label: 'Shopee Mall' },
  { value: 'Star+', label: 'Star+' },
  { value: 'Star', label: 'Star' },
  { value: 'Regular', label: 'Regular' },
];

describe('SelectField', () => {
  it('renders label', () => {
    render(
      <SelectField name="test" label="Status Toko" options={options} value={null} onChange={vi.fn()} />,
    );
    expect(screen.getByText('Status Toko')).toBeInTheDocument();
  });

  it('renders trigger with placeholder when no value', () => {
    render(
      <SelectField name="test" label="Status Toko" options={options} value={null} onChange={vi.fn()} />,
    );
    expect(screen.getByText('Pilih...')).toBeInTheDocument();
  });

  it('renders selected value', () => {
    render(
      <SelectField name="test" label="Status Toko" options={options} value="Star+" onChange={vi.fn()} />,
    );
    expect(screen.getByText('Star+')).toBeInTheDocument();
  });

  it('renders benchmark text when provided', () => {
    render(
      <SelectField name="test" label="Status" options={options} value={null} onChange={vi.fn()} benchmark="Shopee Mall" />,
    );
    expect(screen.getByText('Benchmark: Shopee Mall')).toBeInTheDocument();
  });

  it('opens options on click and calls onChange', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(
      <SelectField name="test" label="Status" options={options} value={null} onChange={onChange} />,
    );
    // Click trigger to open
    await user.click(screen.getByRole('combobox'));
    // Options should appear
    const option = await screen.findByRole('option', { name: 'Star' });
    await user.click(option);
    expect(onChange).toHaveBeenCalledWith('Star');
  });
});
