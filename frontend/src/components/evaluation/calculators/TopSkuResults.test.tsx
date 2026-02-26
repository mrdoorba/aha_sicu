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

function makeLargeResult(): CalculatorResult {
  return {
    ...SAMPLE_RESULT,
    details: {
      output_1: Array.from({ length: 8 }, (_, i) => ({
        kode_variasi: `K${String(i + 1).padStart(3, '0')}`,
        product_name: `Product ${i + 1}`,
        total_omzet: (8 - i) * 100000,
        rata2_harga_jual: 50000,
      })),
      output_2: Array.from({ length: 8 }, (_, i) => ({
        kode_variasi: `K${String(i + 1).padStart(3, '0')}`,
        nama_produk: `Product ${i + 1}`,
        varian: `Var ${i + 1}`,
        stok: (8 - i) * 10,
      })),
      average_stock: 100,
      product_count: 8,
      total_unique_products: 8,
    },
  };
}

async function expandDetails() {
  const user = userEvent.setup();
  const toggle = screen.getByTestId('detail-toggle');
  await user.click(toggle);
  return user;
}

describe('TopSkuResults', () => {
  it('shows average stock but hides tables by default', () => {
    render(<TopSkuResults result={SAMPLE_RESULT} />);

    expect(screen.getByTestId('average-stock')).toHaveTextContent('75');
    expect(screen.getByTestId('detail-toggle')).toHaveTextContent('Lihat Detail');
    expect(screen.queryByTestId('revenue-table')).not.toBeInTheDocument();
    expect(screen.queryByTestId('stock-table')).not.toBeInTheDocument();
  });

  it('expands tables when toggle is clicked', async () => {
    render(<TopSkuResults result={SAMPLE_RESULT} />);
    await expandDetails();

    expect(screen.getByTestId('detail-toggle')).toHaveTextContent('Sembunyikan Detail');
    expect(screen.getByTestId('revenue-table')).toBeInTheDocument();
    expect(screen.getByTestId('stock-table')).toBeInTheDocument();
  });

  it('collapses tables when toggle is clicked again', async () => {
    render(<TopSkuResults result={SAMPLE_RESULT} />);
    const user = await expandDetails();

    await user.click(screen.getByTestId('detail-toggle'));

    expect(screen.getByTestId('detail-toggle')).toHaveTextContent('Lihat Detail');
    expect(screen.queryByTestId('revenue-table')).not.toBeInTheDocument();
    expect(screen.queryByTestId('stock-table')).not.toBeInTheDocument();
  });

  it('renders revenue table with IDR formatting when expanded', async () => {
    render(<TopSkuResults result={SAMPLE_RESULT} />);
    await expandDetails();

    expect(screen.getByText('Peringkat Omzet')).toBeInTheDocument();
    expect(screen.getAllByText('Product A').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Product B').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Rp\s/).length).toBeGreaterThanOrEqual(1);
  });

  it('renders stock table when expanded', async () => {
    render(<TopSkuResults result={SAMPLE_RESULT} />);
    await expandDetails();

    expect(screen.getByText('Peringkat Stok')).toBeInTheDocument();
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
    render(<TopSkuResults result={SAMPLE_RESULT} />);
    const user = await expandDetails();

    const revenueTable = screen.getByTestId('revenue-table');
    const getRevenueRows = () =>
      Array.from(revenueTable.querySelectorAll('tbody tr'));

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

  it('limits revenue table to top 5 rows', async () => {
    render(<TopSkuResults result={makeLargeResult()} />);
    await expandDetails();

    const revenueTable = screen.getByTestId('revenue-table');
    const rows = revenueTable.querySelectorAll('tbody tr');
    expect(rows).toHaveLength(5);
  });

  it('limits stock table to top 5 rows', async () => {
    render(<TopSkuResults result={makeLargeResult()} />);
    await expandDetails();

    const stockTable = screen.getByTestId('stock-table');
    const rows = stockTable.querySelectorAll('tbody tr');
    expect(rows).toHaveLength(5);
  });
});
