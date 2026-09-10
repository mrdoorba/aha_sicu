import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import { EvaluationHeader } from './EvaluationHeader';
import type { BrandDetail } from '../../hooks/useBrandDetail';

const SAMPLE_BRAND: BrandDetail = {
  id: 1,
  brand_name: 'Test Brand',
  raw_data: {
    PIC: 'John',
    Phones: '081234567890',
    Emails: 'john@example.com',
    Category: 'Electronics',
    'Store Link': 'https://shopee.co.id/mall',
  },
  updated_at: '2026-02-05T10:00:00Z',
  meeting_raw_data: { notes: 'Good meeting', score: '8' },
  package_fit: { package: 'New Star', vp: 65, bar: 65, adjustment: 0, met: true },
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
    expect(screen.getByText('Category:')).toBeInTheDocument();
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
      raw_data: { Category: 'Electronics' },
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

  it('shows the package and how VP sits against its bar', () => {
    renderHeader({ brand: SAMPLE_BRAND, isLoading: false, isError: false });

    expect(screen.getByText('New Star')).toBeInTheDocument();
    expect(screen.getByText(/VP 65 \/ min\. 65/)).toBeInTheDocument();
    expect(screen.getByText(/\u2713/)).toBeInTheDocument();
  });

  it('marks a VP that falls short of its bar', () => {
    renderHeader({
      brand: {
        ...SAMPLE_BRAND,
        package_fit: { package: 'Rising Star', vp: 65, bar: 80, adjustment: -10, met: false },
      },
      isLoading: false,
      isError: false,
    });

    expect(screen.getByText('Rising Star')).toBeInTheDocument();
    expect(screen.getByText(/VP 65 \/ min\. 80/)).toBeInTheDocument();
    expect(screen.getByText(/\u2717/)).toBeInTheDocument();
  });

  it('says VP is unjudged rather than showing a bar it never met', () => {
    renderHeader({
      brand: {
        ...SAMPLE_BRAND,
        package_fit: { package: 'New Star', vp: null, bar: 65, adjustment: 0, met: null },
      },
      isLoading: false,
      isError: false,
    });

    expect(screen.getByText('VP belum dinilai')).toBeInTheDocument();
    expect(screen.queryByText(/min\./)).not.toBeInTheDocument();
  });

  it('names an unrecognised package instead of leaving the badge blank', () => {
    renderHeader({
      brand: {
        ...SAMPLE_BRAND,
        package_fit: { package: 'Platinum', vp: 90, bar: null, adjustment: 0, met: null },
      },
      isLoading: false,
      isError: false,
    });

    expect(screen.getByText('Platinum')).toBeInTheDocument();
    expect(screen.getByText('VP belum dinilai')).toBeInTheDocument();
  });
});
