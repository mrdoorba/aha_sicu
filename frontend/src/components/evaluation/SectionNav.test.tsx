import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { SectionNav } from './SectionNav';

describe('SectionNav', () => {
  it('renders all 5 section navigation items', () => {
    render(<SectionNav activeSection="section-1" onSectionClick={vi.fn()} />);

    expect(screen.getByText(/step 1/i)).toBeInTheDocument();
    expect(screen.getByText(/step 2/i)).toBeInTheDocument();
    expect(screen.getByText(/step 3/i)).toBeInTheDocument();
    expect(screen.getByText(/step 4/i)).toBeInTheDocument();
    expect(screen.getByText(/step 5/i)).toBeInTheDocument();
  });

  it('renders section labels', () => {
    render(<SectionNav activeSection="section-1" onSectionClick={vi.fn()} />);

    expect(screen.getByText(/brand info & operational/i)).toBeInTheDocument();
    expect(screen.getByText(/business, content & visitors/i)).toBeInTheDocument();
    expect(screen.getByText(/promo tools & products\/status/i)).toBeInTheDocument();
    expect(screen.getByText(/file upload/i)).toBeInTheDocument();
    expect(screen.getByText(/ads, campaign, competition, stock, discount & review/i)).toBeInTheDocument();
  });

  it('calls onSectionClick when a section is clicked', async () => {
    const user = userEvent.setup();
    const onSectionClick = vi.fn();
    render(<SectionNav activeSection="section-1" onSectionClick={onSectionClick} />);

    await user.click(screen.getByText(/step 3/i));

    expect(onSectionClick).toHaveBeenCalledWith('section-3');
  });

  it('has navigation landmark with aria-label', () => {
    render(<SectionNav activeSection="section-1" onSectionClick={vi.fn()} />);

    expect(screen.getByRole('navigation', { name: /evaluation sections/i })).toBeInTheDocument();
  });
});
