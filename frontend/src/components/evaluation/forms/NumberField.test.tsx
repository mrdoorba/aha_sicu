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

  describe('count field parsing', () => {
    it('strips commas from pasted numbers like 18,219', async () => {
      const onChange = vi.fn();
      const user = userEvent.setup();
      render(
        <NumberField name="test" label="Total" unit="count" value={null} onChange={onChange} />,
      );
      const input = screen.getByRole('textbox');
      await user.click(input);
      await user.paste('18,219');
      expect(onChange).toHaveBeenCalledWith(18219);
    });

    it('strips periods from numbers like 18.219', async () => {
      const onChange = vi.fn();
      const user = userEvent.setup();
      render(
        <NumberField name="test" label="Total" unit="count" value={null} onChange={onChange} />,
      );
      const input = screen.getByRole('textbox');
      await user.click(input);
      await user.paste('18.219');
      expect(onChange).toHaveBeenCalledWith(18219);
    });

    it('strips mixed separators from numbers like 1,234.567', async () => {
      const onChange = vi.fn();
      const user = userEvent.setup();
      render(
        <NumberField name="test" label="Total" unit="count" value={null} onChange={onChange} />,
      );
      const input = screen.getByRole('textbox');
      await user.click(input);
      await user.paste('1,234.567');
      expect(onChange).toHaveBeenCalledWith(1234567);
    });

    it('returns null for empty count input', async () => {
      const onChange = vi.fn();
      const user = userEvent.setup();
      render(
        <NumberField name="test" label="Total" unit="count" value={42} onChange={onChange} />,
      );
      const input = screen.getByRole('textbox');
      await user.clear(input);
      expect(onChange).toHaveBeenCalledWith(null);
    });

    it('returns null for non-numeric count input', async () => {
      const onChange = vi.fn();
      const user = userEvent.setup();
      render(
        <NumberField name="test" label="Total" unit="count" value={null} onChange={onChange} />,
      );
      const input = screen.getByRole('textbox');
      await user.click(input);
      await user.paste('abc');
      expect(onChange).toHaveBeenCalledWith(null);
    });
  });
});
