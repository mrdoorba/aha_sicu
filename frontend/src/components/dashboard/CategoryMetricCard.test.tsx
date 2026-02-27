import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { CategoryMetricCard } from './CategoryMetricCard';

const baseProps = {
  metric: 'Rating Toko',
  value: 4.8,
  score: 10,
  benchmark: '>= 4.7',
  message: '',
};

describe('CategoryMetricCard', () => {
  it('shows green check icon when verdict is ✔️', () => {
    const { container } = render(
      <CategoryMetricCard {...baseProps} verdict="✔️" />,
    );
    // CheckCircle2 renders, XCircle does not
    expect(container.querySelector('.text-success')).toBeInTheDocument();
    expect(container.querySelector('.text-destructive')).not.toBeInTheDocument();
  });

  it('shows red X icon when verdict is ❌', () => {
    const { container } = render(
      <CategoryMetricCard {...baseProps} verdict="❌" />,
    );
    expect(container.querySelector('.text-destructive')).toBeInTheDocument();
    // No green check
    expect(container.querySelectorAll('.text-success')).toHaveLength(0);
  });

  it('shows no icon and muted score when verdict is -', () => {
    const { container } = render(
      <CategoryMetricCard {...baseProps} verdict="-" />,
    );
    // No check or X icons (neither success nor destructive SVG icons)
    const icons = container.querySelectorAll('svg');
    expect(icons).toHaveLength(0);
    // Score span should have muted color
    expect(screen.getByText('10')).toHaveClass('text-muted-foreground');
  });

  it('applies break-all class to message text', () => {
    render(
      <CategoryMetricCard
        {...baseProps}
        verdict="❌"
        message="https://shopee.co.id/search?keyword=very-long-url-that-overflows"
      />,
    );
    const messageEl = screen.getByText(/very-long-url/);
    expect(messageEl).toHaveClass('break-all');
  });

  it('applies orange color to message when verdict is failing', () => {
    render(
      <CategoryMetricCard
        {...baseProps}
        verdict="❌"
        message="Below benchmark"
      />,
    );
    expect(screen.getByText('Below benchmark')).toHaveClass('text-orange-500');
  });

  it('does not apply orange color to message when verdict is neutral', () => {
    render(
      <CategoryMetricCard
        {...baseProps}
        verdict="-"
        message="Informational note"
      />,
    );
    expect(screen.getByText('Informational note')).not.toHaveClass('text-orange-500');
  });
});
