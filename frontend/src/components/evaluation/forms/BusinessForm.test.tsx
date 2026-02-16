import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { BusinessForm } from './BusinessForm';
import type { BusinessData } from './formConfig';

const emptyData: BusinessData = {
  salesStartMonth: null,
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

    // 6 sales month currency fields + 1 conversion rate
    const salesFields = screen.getAllByLabelText(/Penjualan Bulan/);
    expect(salesFields).toHaveLength(6);
    expect(screen.getByLabelText(/Tingkat Konversi/)).toBeInTheDocument();
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

  it('renders section title with reference link', () => {
    render(
      <BusinessForm data={emptyData} categoryType={null} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByText('Bisnis Analisis')).toBeInTheDocument();
  });

  it('renders 6 currency fields for sales months', () => {
    render(
      <BusinessForm data={emptyData} categoryType={null} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    const idrLabels = screen.getAllByText('(IDR)');
    expect(idrLabels).toHaveLength(6);
  });

  it('renders month selector dropdown', () => {
    render(
      <BusinessForm data={emptyData} categoryType={null} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByLabelText(/Bulan Awal Penjualan/)).toBeInTheDocument();
  });

  it('generates dynamic labels when salesStartMonth is set', () => {
    const dataWithMonth: BusinessData = {
      ...emptyData,
      salesStartMonth: '2026-01',
    };
    render(
      <BusinessForm data={dataWithMonth} categoryType={null} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByLabelText(/Penjualan Bulan Jan 2026/)).toBeInTheDocument();
  });

  it('uses generic fallback labels when salesStartMonth is null', () => {
    render(
      <BusinessForm data={emptyData} categoryType={null} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByLabelText(/Penjualan Bulan Bulan Ini/)).toBeInTheDocument();
  });

  it('uses generic fallback labels when salesStartMonth is invalid', () => {
    const dataInvalid: BusinessData = {
      ...emptyData,
      salesStartMonth: 'abc',
    };
    render(
      <BusinessForm data={dataInvalid} categoryType={null} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByLabelText(/Penjualan Bulan Bulan Ini/)).toBeInTheDocument();
  });

  it('shows computed average when sales data is present', () => {
    const dataWithSales: BusinessData = {
      ...emptyData,
      salesMonth0: 50000000,
      salesMonth1: 48000000,
      salesMonth2: 45000000,
      salesMonth3: 40000000,
      salesMonth4: 42000000,
      salesMonth5: 44000000,
    };
    render(
      <BusinessForm data={dataWithSales} categoryType={null} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByText('Rata-rata Penjualan 6 Bulan Terakhir')).toBeInTheDocument();
    // Average = 44833333.33... → should show formatted IDR
    expect(screen.getByText(/44\.833\.333/)).toBeInTheDocument();
  });

  it('shows dash when all sales months are null', () => {
    render(
      <BusinessForm data={emptyData} categoryType={null} onChange={vi.fn()} onBlur={vi.fn()} />,
    );
    expect(screen.getByText('Rata-rata Penjualan 6 Bulan Terakhir')).toBeInTheDocument();
    expect(screen.getByText('—')).toBeInTheDocument();
  });

  it('calls onChange for month selector', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(
      <BusinessForm data={emptyData} categoryType={null} onChange={onChange} onBlur={vi.fn()} />,
    );

    const select = screen.getByLabelText(/Bulan Awal Penjualan/);
    await user.selectOptions(select, select.querySelector('option:nth-child(2)')!);
    expect(onChange).toHaveBeenCalledWith('business', 'salesStartMonth', expect.any(String));
  });
});
