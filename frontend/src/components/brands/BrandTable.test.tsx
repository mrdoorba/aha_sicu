import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BrandTable } from './BrandTable';
import type { BrandListItem } from '../../hooks/useBrands';

const SAMPLE_BRANDS: BrandListItem[] = [
  {
    id: 1,
    brand_name: 'Brand ABC',
    raw_data: { category: 'Electronics', status: 'Active' },
    updated_at: '2026-02-05T10:00:00Z',
    meeting_raw_data: { notes: 'Good meeting' },
  },
  {
    id: 2,
    brand_name: 'Brand DEF',
    raw_data: { category: 'Fashion' },
    updated_at: '2026-02-05T11:00:00Z',
    meeting_raw_data: null,
  },
];

describe('BrandTable', () => {
  it('renders brand rows from data', () => {
    render(<BrandTable brands={SAMPLE_BRANDS} isLoading={false} />);

    expect(screen.getByText('Brand ABC')).toBeInTheDocument();
    expect(screen.getByText('Brand DEF')).toBeInTheDocument();
  });

  it('renders table headers', () => {
    render(<BrandTable brands={SAMPLE_BRANDS} isLoading={false} />);

    expect(screen.getByText('Brand Name')).toBeInTheDocument();
    expect(screen.getByText('Key Info')).toBeInTheDocument();
    expect(screen.getByText('Meeting Data')).toBeInTheDocument();
  });

  it('shows "Available" badge when meeting data exists', () => {
    render(<BrandTable brands={SAMPLE_BRANDS} isLoading={false} />);

    expect(screen.getByText('Available')).toBeInTheDocument();
  });

  it('shows "Not available" when meeting data is null', () => {
    render(<BrandTable brands={SAMPLE_BRANDS} isLoading={false} />);

    expect(screen.getByText(/not available/i)).toBeInTheDocument();
  });

  it('displays raw_data summary for each brand', () => {
    render(<BrandTable brands={SAMPLE_BRANDS} isLoading={false} />);

    expect(screen.getByText(/category: electronics/i)).toBeInTheDocument();
    expect(screen.getByText(/category: fashion/i)).toBeInTheDocument();
  });

  it('shows skeleton loading state', () => {
    render(<BrandTable brands={[]} isLoading={true} />);

    // Should show skeleton rows, not brand data
    expect(screen.queryByText('Brand ABC')).not.toBeInTheDocument();
    // But should have the table structure
    expect(screen.getByText('Brand Name')).toBeInTheDocument();
  });
});
