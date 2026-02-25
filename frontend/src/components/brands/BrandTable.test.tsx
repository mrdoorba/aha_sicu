import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import { BrandTable } from './BrandTable';
import type { BrandListItem } from '../../hooks/useBrands';

const SAMPLE_BRANDS: BrandListItem[] = [
  {
    id: 1,
    brand_name: 'Brand ABC',
    raw_data: { Kategori: 'Electronics', 'Signed up': 'Yes' },
    updated_at: '2026-02-05T10:00:00Z',
    meeting_raw_data: { notes: 'Good meeting' },
  },
  {
    id: 2,
    brand_name: 'Brand DEF',
    raw_data: { Kategori: 'Fashion' },
    updated_at: '2026-02-05T11:00:00Z',
    meeting_raw_data: null,
  },
];

const renderBrandTable = (props: { brands: BrandListItem[]; isLoading: boolean }) => {
  return render(
    <BrowserRouter>
      <BrandTable {...props} />
    </BrowserRouter>
  );
};

describe('BrandTable', () => {
  it('renders brand rows from data', () => {
    renderBrandTable({ brands: SAMPLE_BRANDS, isLoading: false });

    expect(screen.getByText('Brand ABC')).toBeInTheDocument();
    expect(screen.getByText('Brand DEF')).toBeInTheDocument();
  });

  it('renders table headers including Action column', () => {
    renderBrandTable({ brands: SAMPLE_BRANDS, isLoading: false });

    expect(screen.getByText('Nama Brand')).toBeInTheDocument();
    expect(screen.getByText('Info Utama')).toBeInTheDocument();
    expect(screen.getByText('Data Meeting')).toBeInTheDocument();
    expect(screen.getByText('Aksi')).toBeInTheDocument();
  });

  it('shows "Available" badge when meeting data exists', () => {
    renderBrandTable({ brands: SAMPLE_BRANDS, isLoading: false });

    expect(screen.getByText('Tersedia')).toBeInTheDocument();
  });

  it('shows "Tidak tersedia" when meeting data is null', () => {
    renderBrandTable({ brands: SAMPLE_BRANDS, isLoading: false });

    expect(screen.getByText(/tidak tersedia/i)).toBeInTheDocument();
  });

  it('displays raw_data summary for each brand', () => {
    renderBrandTable({ brands: SAMPLE_BRANDS, isLoading: false });

    expect(screen.getByText(/Kategori: Electronics/)).toBeInTheDocument();
    expect(screen.getByText(/Kategori: Fashion/)).toBeInTheDocument();
  });

  it('shows skeleton loading state', () => {
    renderBrandTable({ brands: [], isLoading: true });

    // Should show skeleton rows, not brand data
    expect(screen.queryByText('Brand ABC')).not.toBeInTheDocument();
    // But should have the table structure
    expect(screen.getByText('Nama Brand')).toBeInTheDocument();
  });

  it('has aria-busy="true" when loading', () => {
    renderBrandTable({ brands: [], isLoading: true });

    const table = screen.getByRole('table', { name: /brand list/i });
    expect(table).toHaveAttribute('aria-busy', 'true');
  });

  it('has aria-busy="false" when loaded', () => {
    renderBrandTable({ brands: SAMPLE_BRANDS, isLoading: false });

    const table = screen.getByRole('table', { name: /brand list/i });
    expect(table).toHaveAttribute('aria-busy', 'false');
  });

  it('has aria-label="Brand list"', () => {
    renderBrandTable({ brands: SAMPLE_BRANDS, isLoading: false });

    const table = screen.getByRole('table', { name: /brand list/i });
    expect(table).toBeInTheDocument();
  });

  it('renders "Evaluasi" button for each brand row', () => {
    renderBrandTable({ brands: SAMPLE_BRANDS, isLoading: false });

    const evaluateButtons = screen.getAllByRole('button', { name: /evaluasi/i });
    expect(evaluateButtons).toHaveLength(2);
  });
});
