import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import { EvaluationHeader } from './EvaluationHeader';
import type { BrandDetail } from '../../hooks/useBrandDetail';

const SAMPLE_BRAND: BrandDetail = {
  id: 1,
  brand_name: 'Test Brand',
  raw_data: {
    'Nama PIC/ Jabatan*': 'John',
    'No WA*': '081234567890',
    Email: 'john@example.com',
    Kategori: 'Electronics',
    'Link Shopee Mall / LazMall': 'https://shopee.co.id/mall',
  },
  updated_at: '2026-02-05T10:00:00Z',
  meeting_raw_data: { notes: 'Good meeting', score: '8' },
};

const renderHeader = (props: {
  brand: BrandDetail | null;
  isLoading: boolean;
  isError: boolean;
}) => {
  return render(
    <BrowserRouter>
      <EvaluationHeader {...props} />
    </BrowserRouter>
  );
};

describe('EvaluationHeader', () => {
  it('renders brand name prominently', () => {
    renderHeader({ brand: SAMPLE_BRAND, isLoading: false, isError: false });

    expect(screen.getByText('Test Brand')).toBeInTheDocument();
  });

  it('shows curated VP data fields with mapped labels', () => {
    renderHeader({ brand: SAMPLE_BRAND, isLoading: false, isError: false });

    expect(screen.getByText('Nama PIC:')).toBeInTheDocument();
    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('No WA:')).toBeInTheDocument();
    expect(screen.getByText('081234567890')).toBeInTheDocument();
    expect(screen.getByText('Kategori:')).toBeInTheDocument();
    expect(screen.getByText('Electronics')).toBeInTheDocument();
    expect(screen.getByText('Link Toko:')).toBeInTheDocument();
  });

  it('renders URL fields as clickable links', () => {
    renderHeader({ brand: SAMPLE_BRAND, isLoading: false, isError: false });

    const link = screen.getByRole('link', { name: 'https://shopee.co.id/mall' });
    expect(link).toHaveAttribute('href', 'https://shopee.co.id/mall');
    expect(link).toHaveAttribute('target', '_blank');
  });

  it('skips curated fields that are missing from raw_data', () => {
    const brandMissing = {
      ...SAMPLE_BRAND,
      raw_data: { Kategori: 'Electronics' },
    };
    renderHeader({ brand: brandMissing, isLoading: false, isError: false });

    expect(screen.queryByText('Nama PIC:')).not.toBeInTheDocument();
    expect(screen.queryByText('No WA:')).not.toBeInTheDocument();
  });

  it('shows Data M1 badge when meeting data exists', () => {
    renderHeader({ brand: SAMPLE_BRAND, isLoading: false, isError: false });

    // Badge and section header both say "Data M1" — use getAllByText
    const meetingLabels = screen.getAllByText('Data M1');
    expect(meetingLabels.length).toBeGreaterThanOrEqual(1);
  });

  it('shows "Tidak ada data M1" when meeting data is null', () => {
    const brandNoMeeting = { ...SAMPLE_BRAND, meeting_raw_data: null };
    renderHeader({ brand: brandNoMeeting, isLoading: false, isError: false });

    expect(screen.getByText('Tidak ada data M1')).toBeInTheDocument();
  });

  it('shows loading skeleton when loading', () => {
    renderHeader({ brand: null, isLoading: true, isError: false });

    expect(screen.queryByText('Test Brand')).not.toBeInTheDocument();
  });

  it('shows error message on error', () => {
    renderHeader({ brand: null, isLoading: false, isError: true });

    expect(screen.getByText(/gagal memuat data brand/i)).toBeInTheDocument();
  });

  it('renders back button', () => {
    renderHeader({ brand: SAMPLE_BRAND, isLoading: false, isError: false });

    expect(screen.getByRole('button', { name: /kembali ke brand/i })).toBeInTheDocument();
  });
});
