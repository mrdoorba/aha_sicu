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
  // ---------------------------------------------------------------------------
  // BDD Scenario: No icons next to scores
  //   Given a metric card with any verdict
  //   When rendering the score area
  //   Then no SVG icons (CheckCircle2/XCircle) should appear
  // ---------------------------------------------------------------------------

  it('renders NO SVG icons next to score for passing verdict', () => {
    const { container } = render(
      <CategoryMetricCard {...baseProps} verdict="✔️" />,
    );
    // No SVG icons should exist
    expect(container.querySelectorAll('svg')).toHaveLength(0);
  });

  it('renders NO SVG icons next to score for failing verdict', () => {
    const { container } = render(
      <CategoryMetricCard {...baseProps} verdict="❌" />,
    );
    // No SVG icons should exist
    expect(container.querySelectorAll('svg')).toHaveLength(0);
  });

  it('shows no icon when verdict is -', () => {
    const { container } = render(
      <CategoryMetricCard {...baseProps} verdict="-" />,
    );
    const icons = container.querySelectorAll('svg');
    expect(icons).toHaveLength(0);
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

  // ---------------------------------------------------------------------------
  // BDD Scenario: Message lines color-coded by verdict
  //   Given a message starting with ✔️
  //   When the card renders
  //   Then the entire message line is green (text-green-600)
  //
  //   Given a message starting with ❌
  //   When the card renders
  //   Then the entire message line is orange (text-orange-600)
  // ---------------------------------------------------------------------------

  it('renders ✔️ message with green color on entire line', () => {
    const { container } = render(
      <CategoryMetricCard
        {...baseProps}
        verdict="✔️"
        message="✔️ Rating Toko = 4.8 [Sudah Baik]"
      />,
    );
    const greenLine = container.querySelector('.text-green-600');
    expect(greenLine).toBeInTheDocument();
  });

  it('renders ❌ message with orange color on entire line', () => {
    const { container } = render(
      <CategoryMetricCard
        {...baseProps}
        verdict="❌"
        message="❌ Rating Toko = 3.0 [Di Bawah Target]"
      />,
    );
    const orangeLine = container.querySelector('.text-orange-600');
    expect(orangeLine).toBeInTheDocument();
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
  // ---------------------------------------------------------------------------
  // BDD Acceptance Tests: Percentage metrics display as formatted percentages
  //
  //   Scenario: GMV ratio displays as percentage
  //     Given a scoring result with "% GMV Iklan / GMV Toko" value of 1.11
  //     When the dashboard renders the metric card
  //     Then the displayed value should be "111.0%"
  //
  //   Scenario: Cost ratio displays as percentage
  //     Given a scoring result with "% Biaya Iklan / GMV Toko" value of 0.153
  //     When the dashboard renders the metric card
  //     Then the displayed value should be "15.3%"
  //
  //   Scenario: Non-percentage metrics remain unchanged
  //     Given a scoring result with "ROI" value of 7.245
  //     When the dashboard renders the metric card
  //     Then the displayed value should be "7.245"
  // ---------------------------------------------------------------------------

  it('displays GMV ratio as formatted percentage (111.0%)', () => {
    // Arrange
    render(
      <CategoryMetricCard
        metric="% GMV Iklan / GMV Toko"
        value={1.11}
        verdict="❌"
        score={0}
        benchmark="<84%"
        message=""
      />,
    );

    // Act (implicit — component renders on mount)

    // Assert
    expect(screen.getByText('111.0%')).toBeInTheDocument();
  });

  it('displays cost ratio as formatted percentage (15.3%)', () => {
    // Arrange
    render(
      <CategoryMetricCard
        metric="% Biaya Iklan / GMV Toko"
        value={0.153}
        verdict="❌"
        score={0}
        benchmark="<10%"
        message=""
      />,
    );

    // Act (implicit — component renders on mount)

    // Assert
    expect(screen.getByText('15.3%')).toBeInTheDocument();
  });

  it('should hide benchmark line when benchmark is dash', () => {
    // Arrange
    render(
      <CategoryMetricCard
        metric="Sesi dinominasikan"
        value={4}
        verdict="-"
        score={0}
        benchmark="-"
        message=""
      />,
    );

    // Assert
    expect(screen.queryByText('Benchmark: -')).not.toBeInTheDocument();
  });

  it('should show benchmark line when benchmark has real value', () => {
    // Arrange
    render(
      <CategoryMetricCard
        metric="Rating Toko"
        value={4.8}
        verdict="✔️"
        score={10}
        benchmark=">= 4.7"
        message=""
      />,
    );

    // Assert
    expect(screen.getByText('Benchmark: >= 4.7')).toBeInTheDocument();
  });

  it('does not apply percentage formatting to non-% metric (ROI)', () => {
    // Arrange
    render(
      <CategoryMetricCard
        metric="ROI"
        value={7.245}
        verdict="❌"
        score={5}
        benchmark=">9"
        message=""
      />,
    );

    // Act (implicit — component renders on mount)

    // Assert
    expect(screen.getByText('7.245')).toBeInTheDocument();
  });
});
