import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { VerdictSelector } from './VerdictSelector';

describe('VerdictSelector', () => {
  it('renders Verdict label', () => {
    render(<VerdictSelector value="✔️" onChange={vi.fn()} />);
    expect(screen.getByText('Verdict')).toBeInTheDocument();
  });

  it('renders the select trigger', () => {
    render(<VerdictSelector value="✔️" onChange={vi.fn()} />);
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });
});
