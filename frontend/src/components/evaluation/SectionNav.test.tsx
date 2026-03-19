import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { SectionNav } from './SectionNav';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'id', changeLanguage: vi.fn() },
  }),
}));

describe('SectionNav', () => {
  it('renders all 6 section navigation items', () => {
    render(<SectionNav activeSection="section-1" onSectionClick={vi.fn()} />);

    expect(screen.getByText(/step 1/i)).toBeInTheDocument();
    expect(screen.getByText(/step 2/i)).toBeInTheDocument();
    expect(screen.getByText(/step 3/i)).toBeInTheDocument();
    expect(screen.getByText(/step 4/i)).toBeInTheDocument();
    expect(screen.getByText(/step 5/i)).toBeInTheDocument();
    expect(screen.getByText(/step 6/i)).toBeInTheDocument();
  });

  it('renders section labels via i18n keys', () => {
    render(<SectionNav activeSection="section-1" onSectionClick={vi.fn()} />);

    expect(screen.getByText('sectionNav.brandInfoOperational')).toBeInTheDocument();
    expect(screen.getByText('sectionNav.businessVisitors')).toBeInTheDocument();
    expect(screen.getByText('sectionNav.promoProducts')).toBeInTheDocument();
    expect(screen.getByText('sectionNav.fileUpload')).toBeInTheDocument();
    expect(screen.getByText('sectionNav.adsCompetition')).toBeInTheDocument();
    expect(screen.getByText('sectionNav.finalScore')).toBeInTheDocument();
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
