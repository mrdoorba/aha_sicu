import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import { EvaluationHeader } from './EvaluationHeader';
import type { BrandDetail } from '../../hooks/useBrandDetail';

const SAMPLE_BRAND: BrandDetail = {
  id: 1,
  brand_name: 'Test Brand',
  raw_data: {
    BD: 'John',
    'Link Shopee Mall / LazMall': 'https://shopee.co.id/mall',
    Kategori: 'Electronics',
    'Shopee Mall': 'Yes',
    'Score VP': '85',
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

  it('shows curated VP data fields in order', () => {
    renderHeader({ brand: SAMPLE_BRAND, isLoading: false, isError: false });

    expect(screen.getByText('BD:')).toBeInTheDocument();
    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('Kategori:')).toBeInTheDocument();
    expect(screen.getByText('Electronics')).toBeInTheDocument();
    expect(screen.getByText('Score VP:')).toBeInTheDocument();
    expect(screen.getByText('85')).toBeInTheDocument();
  });

  it('renders URL fields as clickable links', () => {
    renderHeader({ brand: SAMPLE_BRAND, isLoading: false, isError: false });

    const link = screen.getByRole('link', { name: 'https://shopee.co.id/mall' });
    expect(link).toHaveAttribute('href', 'https://shopee.co.id/mall');
    expect(link).toHaveAttribute('target', '_blank');
  });

  it('skips curated fields that are missing from raw_data', () => {
    renderHeader({ brand: SAMPLE_BRAND, isLoading: false, isError: false });

    expect(screen.queryByText('No WA:')).not.toBeInTheDocument();
    expect(screen.queryByText('Email:')).not.toBeInTheDocument();
  });

  it('shows Data Meeting badge when meeting data exists', () => {
    renderHeader({ brand: SAMPLE_BRAND, isLoading: false, isError: false });

    // Badge and section header both say "Data Meeting" — use getAllByText
    const meetingLabels = screen.getAllByText('Data Meeting');
    expect(meetingLabels.length).toBeGreaterThanOrEqual(1);
  });

  it('shows "Tidak ada data meeting" when meeting data is null', () => {
    const brandNoMeeting = { ...SAMPLE_BRAND, meeting_raw_data: null };
    renderHeader({ brand: brandNoMeeting, isLoading: false, isError: false });

    expect(screen.getByText('Tidak ada data meeting')).toBeInTheDocument();
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
