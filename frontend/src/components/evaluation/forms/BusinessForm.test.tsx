import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { BusinessForm } from './BusinessForm';
import type { BusinessData } from './formConfig';

const emptyData: BusinessData = {
  salesMonth0: null,
  salesMonth1: null,
  salesMonth2: null,
  salesMonth3: null,
  salesMonth4: null,
  salesMonth5: null,
  conversionRate: null,
};

describe('BusinessForm', () => {
  it('renders all 7 business fields', () => {
    render(
      <BusinessForm data={emptyData} categoryType={null} onChange={vi.fn()} onBlur={vi.fn()} />,
    );

    expect(screen.getByLabelText(/Penjualan Bulan Ini/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan Bulan -1/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan Bulan -2/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan Bulan -3/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan Bulan -4/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Penjualan Bulan -5/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Conversion Rate/)).toBeInTheDocument();
  });

  it('shows Non-Fashion benchmark by default', () => {
    render(
      <BusinessForm data={emptyData} categoryType="non_fashion" onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByText('Benchmark: >3%')).toBeInTheDocument();
  });

  it('switches to Fashion benchmark when categoryType is fashion', () => {
    render(
      <BusinessForm data={emptyData} categoryType="fashion" onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByText('Benchmark: >2%')).toBeInTheDocument();
    expect(screen.queryByText('Benchmark: >3%')).not.toBeInTheDocument();
  });

  it('renders section title', () => {
    render(
      <BusinessForm data={emptyData} categoryType={null} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByText('Business')).toBeInTheDocument();
  });

  it('renders 6 currency fields for sales months', () => {
    render(
      <BusinessForm data={emptyData} categoryType={null} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    // 6 sales IDR labels + 1 conversion rate = 7 fields total
    const idrLabels = screen.getAllByText('(IDR)');
    expect(idrLabels).toHaveLength(6);
  });
});
