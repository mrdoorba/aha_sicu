import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

import { EmailChipInput } from './EmailChipInput';

function renderChipInput(overrides: Record<string, unknown> = {}) {
  const defaultProps = {
    id: 'test-chip',
    emails: [] as string[],
    onChange: vi.fn(),
    ...overrides,
  };

  return {
    ...render(<EmailChipInput {...defaultProps} />),
    props: defaultProps,
  };
}

describe('EmailChipInput', () => {
  it('renders chips for each email in emails array', () => {
    renderChipInput({ emails: ['a@test.com', 'b@test.com'] });
    expect(screen.getByText('a@test.com')).toBeInTheDocument();
    expect(screen.getByText('b@test.com')).toBeInTheDocument();
  });

  it('adds email chip when pressing Enter with valid email', () => {
    const { props } = renderChipInput();
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'user@example.com' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(props.onChange).toHaveBeenCalledWith(['user@example.com']);
  });

  it('adds email chip when pressing comma with valid email', () => {
    const { props } = renderChipInput();
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'user@example.com' } });
    fireEvent.keyDown(input, { key: ',' });
    expect(props.onChange).toHaveBeenCalledWith(['user@example.com']);
  });

  it('removes chip when X button is clicked', () => {
    const { props } = renderChipInput({ emails: ['a@test.com', 'b@test.com'] });
    const removeButtons = screen.getAllByRole('button');
    fireEvent.click(removeButtons[0]);
    expect(props.onChange).toHaveBeenCalledWith(['b@test.com']);
  });

  it('removes last chip when Backspace is pressed on empty input', () => {
    const { props } = renderChipInput({ emails: ['a@test.com', 'b@test.com'] });
    const input = screen.getByRole('textbox');
    fireEvent.keyDown(input, { key: 'Backspace' });
    expect(props.onChange).toHaveBeenCalledWith(['a@test.com']);
  });

  it('rejects invalid email format with error message', () => {
    renderChipInput();
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'not-an-email' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(screen.getByText('sendEmail.invalidEmail')).toBeInTheDocument();
  });

  it('rejects duplicate email with error message', () => {
    renderChipInput({ emails: ['a@test.com'] });
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'a@test.com' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(screen.getByText('sendEmail.duplicateEmail')).toBeInTheDocument();
  });

  it('respects max capacity and does not add when at limit', () => {
    const { props } = renderChipInput({
      emails: ['a@test.com'],
      maxTotal: 2,
      currentTotal: 2,
    });
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'new@test.com' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(props.onChange).not.toHaveBeenCalled();
    expect(screen.getByText('sendEmail.maxRecipients')).toBeInTheDocument();
  });

  it('adds email on blur when input is non-empty and valid', () => {
    const { props } = renderChipInput();
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'blur@test.com' } });
    fireEvent.blur(input);
    expect(props.onChange).toHaveBeenCalledWith(['blur@test.com']);
  });

  it('shows placeholder only when no chips exist', () => {
    const { rerender } = renderChipInput({ placeholder: 'Type email...' });
    expect(screen.getByPlaceholderText('Type email...')).toBeInTheDocument();

    rerender(
      <EmailChipInput
        id="test-chip"
        emails={['a@test.com']}
        onChange={vi.fn()}
        placeholder="Type email..."
      />,
    );
    expect(screen.queryByPlaceholderText('Type email...')).not.toBeInTheDocument();
  });
});
