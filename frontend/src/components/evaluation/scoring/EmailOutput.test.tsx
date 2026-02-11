import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { EmailOutput } from './EmailOutput';

describe('EmailOutput', () => {
  it('renders subject and body', () => {
    render(<EmailOutput subject="Test Subject" body="Test body content" />);
    expect(screen.getByText('Test Subject')).toBeInTheDocument();
    expect(screen.getByText('Test body content')).toBeInTheDocument();
  });

  it('renders Email Output heading', () => {
    render(<EmailOutput subject="Sub" body="Body" />);
    expect(screen.getByText('Email Output')).toBeInTheDocument();
  });

  it('has a Copy button', () => {
    render(<EmailOutput subject="Sub" body="Body" />);
    expect(screen.getByRole('button', { name: /copy/i })).toBeInTheDocument();
  });

  it('copies text to clipboard on click', async () => {
    const user = userEvent.setup();
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText },
      writable: true,
      configurable: true,
    });

    render(<EmailOutput subject="My Subject" body="My Body" />);
    await user.click(screen.getByRole('button', { name: /copy/i }));

    expect(writeText).toHaveBeenCalledWith('Subject: My Subject\n\nMy Body');
  });
});
