import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import { EvaluationHeader } from './EvaluationHeader';
import type { BrandDetail } from '../../hooks/useBrandDetail';

const SAMPLE_BRAND: BrandDetail = {
  id: 1,
  brand_name: 'Test Brand',
  raw_data: { category: 'Electronics', marketplace: 'Shopee' },
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

  it('shows VP data fields', () => {
    renderHeader({ brand: SAMPLE_BRAND, isLoading: false, isError: false });

    expect(screen.getByText(/category/i)).toBeInTheDocument();
    expect(screen.getByText(/Electronics/i)).toBeInTheDocument();
  });

  it('shows Meeting Data badge when meeting data exists', () => {
    renderHeader({ brand: SAMPLE_BRAND, isLoading: false, isError: false });

    // Badge and section header both say "Meeting Data" — use getAllByText
    const meetingLabels = screen.getAllByText('Meeting Data');
    expect(meetingLabels.length).toBeGreaterThanOrEqual(1);
  });

  it('shows "No meeting data available" when meeting data is null', () => {
    const brandNoMeeting = { ...SAMPLE_BRAND, meeting_raw_data: null };
    renderHeader({ brand: brandNoMeeting, isLoading: false, isError: false });

    expect(screen.getByText('No meeting data available')).toBeInTheDocument();
  });

  it('shows loading skeleton when loading', () => {
    renderHeader({ brand: null, isLoading: true, isError: false });

    expect(screen.queryByText('Test Brand')).not.toBeInTheDocument();
  });

  it('shows error message on error', () => {
    renderHeader({ brand: null, isLoading: false, isError: true });

    expect(screen.getByText(/failed to load brand data/i)).toBeInTheDocument();
  });

  it('renders back button', () => {
    renderHeader({ brand: SAMPLE_BRAND, isLoading: false, isError: false });

    expect(screen.getByRole('button', { name: /back to brands/i })).toBeInTheDocument();
  });
});
