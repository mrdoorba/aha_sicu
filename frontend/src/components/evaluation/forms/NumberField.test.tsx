import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { NumberField } from './NumberField';

describe('NumberField', () => {
  it('renders label and input', () => {
    render(
      <NumberField name="test" label="Test Field" value={null} onChange={vi.fn()} />,
    );
    expect(screen.getByLabelText('Test Field')).toBeInTheDocument();
    expect(screen.getByRole('spinbutton')).toBeInTheDocument();
  });

  it('renders unit suffix in label', () => {
    render(
      <NumberField name="test" label="Rate" unit="%" value={null} onChange={vi.fn()} />,
    );
    expect(screen.getByText('(%)')).toBeInTheDocument();
  });

  it('does not render unit suffix for count type', () => {
    render(
      <NumberField name="test" label="Total" unit="count" value={null} onChange={vi.fn()} />,
    );
    expect(screen.queryByText('(count)')).not.toBeInTheDocument();
  });

  it('renders benchmark helper text', () => {
    render(
      <NumberField name="test" label="Test" benchmark=">95%" value={null} onChange={vi.fn()} />,
    );
    expect(screen.getByText('Benchmark: >95%')).toBeInTheDocument();
  });

  it('displays current value', () => {
    render(
      <NumberField name="test" label="Test" value={42} onChange={vi.fn()} />,
    );
    expect(screen.getByRole('spinbutton')).toHaveValue(42);
  });

  it('calls onChange with number when user types', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(
      <NumberField name="test" label="Test" value={null} onChange={onChange} />,
    );
    await user.type(screen.getByRole('spinbutton'), '5');
    expect(onChange).toHaveBeenCalledWith(5);
  });

  it('calls onChange with null when input is cleared', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(
      <NumberField name="test" label="Test" value={5} onChange={onChange} />,
    );
    await user.clear(screen.getByRole('spinbutton'));
    expect(onChange).toHaveBeenCalledWith(null);
  });

  it('calls onBlur when field loses focus', async () => {
    const onBlur = vi.fn();
    const user = userEvent.setup();
    render(
      <NumberField name="test" label="Test" value={null} onChange={vi.fn()} onBlur={onBlur} />,
    );
    await user.click(screen.getByRole('spinbutton'));
    await user.tab();
    expect(onBlur).toHaveBeenCalled();
  });
});
