import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { ProductsStatusForm } from './ProductsStatusForm';
import type { ProductsData } from './formConfig';

const emptyData: ProductsData = {
  productCount: null,
  storeStatus: null,
};

describe('ProductsStatusForm', () => {
  it('renders product count number field', () => {
    render(<ProductsStatusForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByLabelText(/Jumlah Produk/)).toBeInTheDocument();
  });

  it('renders status dropdown with placeholder', () => {
    render(<ProductsStatusForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('Status Toko')).toBeInTheDocument();
    expect(screen.getByText('Pilih...')).toBeInTheDocument();
  });

  it('renders benchmarks', () => {
    render(<ProductsStatusForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('Benchmark: >=35')).toBeInTheDocument();
    expect(screen.getByText('Benchmark: Shopee Mall')).toBeInTheDocument();
  });

  it('shows dropdown options when clicked', async () => {
    const user = userEvent.setup();
    render(<ProductsStatusForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);
    await user.click(screen.getByRole('combobox'));
    expect(await screen.findByRole('option', { name: 'Shopee Mall' })).toBeInTheDocument();
    expect(await screen.findByRole('option', { name: 'Star+' })).toBeInTheDocument();
    expect(await screen.findByRole('option', { name: 'Star' })).toBeInTheDocument();
    expect(await screen.findByRole('option', { name: 'Regular' })).toBeInTheDocument();
  });

  it('calls onChange when dropdown option selected', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(<ProductsStatusForm data={emptyData} onChange={onChange} onBlur={vi.fn()} />);
    await user.click(screen.getByRole('combobox'));
    await user.click(await screen.findByRole('option', { name: 'Shopee Mall' }));
    expect(onChange).toHaveBeenCalledWith('products', 'storeStatus', 'Shopee Mall');
  });

  it('renders section title', () => {
    render(<ProductsStatusForm data={emptyData} onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('Products / Status')).toBeInTheDocument();
  });
});
