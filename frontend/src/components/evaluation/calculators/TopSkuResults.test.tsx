import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest';
import { TopSkuResults } from './TopSkuResults';
import type { CalculatorResult } from '../../../hooks/useCalculator';

const SAMPLE_RESULT: CalculatorResult = {
  calculator_type: 'top_sku',
  output_text: '',
  details: {
    output_1: [
      { kode_variasi: 'K001', product_name: 'Product A', total_omzet: 500000, rata2_harga_jual: 100000 },
      { kode_variasi: 'K002', product_name: 'Product B', total_omzet: 300000, rata2_harga_jual: 150000 },
    ],
    output_2: [
      { kode_variasi: 'K001', nama_produk: 'Product A', varian: 'Red', stok: 50 },
      { kode_variasi: 'K002', nama_produk: 'Product B', varian: 'Blue', stok: 100 },
    ],
    average_stock: 75,
    product_count: 2,
    total_unique_products: 2,
  },
  calculated_at: '2026-02-11T10:30:00Z',
};

describe('TopSkuResults', () => {
  it('renders revenue table with IDR formatting', () => {
    render(<TopSkuResults result={SAMPLE_RESULT} />);

    expect(screen.getByText('Revenue Ranking')).toBeInTheDocument();
    // Product names appear in both tables, so use getAllByText
    expect(screen.getAllByText('Product A').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Product B').length).toBeGreaterThanOrEqual(1);
    // IDR formatted values
    expect(screen.getAllByText(/Rp/).length).toBeGreaterThanOrEqual(1);
  });

  it('renders stock table', () => {
    render(<TopSkuResults result={SAMPLE_RESULT} />);

    expect(screen.getByText('Stock Ranking')).toBeInTheDocument();
    expect(screen.getByText('Red')).toBeInTheDocument();
    expect(screen.getByText('Blue')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
  });

  it('renders average stock metric', () => {
    render(<TopSkuResults result={SAMPLE_RESULT} />);

    const avgStock = screen.getByTestId('average-stock');
    expect(avgStock).toHaveTextContent('75');
  });

  it('table sorting changes order', async () => {
    const user = userEvent.setup();
    render(<TopSkuResults result={SAMPLE_RESULT} />);

    // Revenue table rows: find all rows, revenue table is the first table
    const tables = document.querySelectorAll('[data-slot="table-container"]');
    const revenueTable = tables[0];
    const getRevenueRows = () =>
      Array.from(revenueTable.querySelectorAll('[data-slot="table-row"]')).slice(1); // skip header

    // Default sort: total_omzet desc → Product A (500k) first
    let dataRows = getRevenueRows();
    expect(dataRows[0]).toHaveTextContent('Product A');
    expect(dataRows[1]).toHaveTextContent('Product B');

    // Click Total Omzet header to toggle to asc
    const totalOmzetHeader = screen.getByText('Total Omzet');
    await user.click(totalOmzetHeader);

    // After toggling to asc, Product B (300k) should be first
    dataRows = getRevenueRows();
    expect(dataRows[0]).toHaveTextContent('Product B');
    expect(dataRows[1]).toHaveTextContent('Product A');
  });
});
