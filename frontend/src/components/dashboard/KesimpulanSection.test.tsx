import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { KesimpulanSection } from './KesimpulanSection';

describe('KesimpulanSection', () => {
  it('should render conclusion bullets, budget card, and closing message when full data provided', () => {
    const calculatorResults = {
      scoring_summary: {
        conclusion: '- Finding A\n- Finding B\n- Finding C',
        marketing_estimation: '22.4% ~ 26.2%',
        marketing_budget: '23%',
        closing_message: 'Kami melihat bahwa potensi dari Toko Test masih belum maksimal.',
      },
    };

    render(<KesimpulanSection calculatorResults={calculatorResults} />);

    expect(screen.getByText('Kesimpulan')).toBeInTheDocument();
    expect(screen.getByText('Finding A')).toBeInTheDocument();
    expect(screen.getByText('Finding B')).toBeInTheDocument();
    expect(screen.getByText('Finding C')).toBeInTheDocument();
    expect(screen.getByText('Estimasi persentase biaya marketing sekarang:')).toBeInTheDocument();
    expect(screen.getByText('22.4% ~ 26.2%')).toBeInTheDocument();
    expect(screen.getByText('Min. Anggaran Marketing')).toBeInTheDocument();
    expect(screen.getByText('23%')).toBeInTheDocument();
    expect(screen.getByText('Kami melihat bahwa potensi dari Toko Test masih belum maksimal.')).toBeInTheDocument();
  });

  it('should show no data message when scoring_summary is missing', () => {
    const calculatorResults = {
      ads_keyword: { output_text: 'some data' },
    };

    render(<KesimpulanSection calculatorResults={calculatorResults} />);

    expect(screen.getByText('Kesimpulan')).toBeInTheDocument();
    expect(screen.getByText('Tidak ada data')).toBeInTheDocument();
  });



  it('should render updated Indonesian conclusion copy from i18n keys', () => {
    const calculatorResults = {
      scoring_summary: {
        conclusion_i18n: [
          { key: 'conclusion.operationalChatIssue', vars: {} },
          { key: 'conclusion.productNaming', vars: {} },
          { key: 'conclusion.photoBackground', vars: {} },
          { key: 'conclusion.promoUnderutilized', vars: {} },
          { key: 'conclusion.campaignLow', vars: {} },
          { key: 'conclusion.stockNotArchived', vars: {} },
          { key: 'conclusion.discountRange', vars: { range: '12.0% ~ 18.0%' } },
        ],
      },
    };

    render(<KesimpulanSection calculatorResults={calculatorResults} />);

    expect(screen.getByText('Kualitas operasional toko sudah cukup baik, hanya tingkat response chat masih dapat ditingkatkan.')).toBeInTheDocument();
    expect(screen.getByText('Nama produk disarankan untuk dimulai dengan nama brand dan mencantumkan FAB produk (Feature, Advantage, & Benefit).')).toBeInTheDocument();
    expect(screen.getByText('Gambar produk utama sebaiknya menampilkan logo brand termasuk FAB (Features, Advantage, Benefit).')).toBeInTheDocument();
    expect(screen.getByText('Beberapa fitur promosi masih belum optimal.')).toBeInTheDocument();
    expect(screen.getByText('Partisipasi Campaign Shopee belum maksimal.')).toBeInTheDocument();
    expect(screen.getByText('Pastikan produk yang stoknya habis diarsipkan')).toBeInTheDocument();
    expect(screen.getByText('Range diskon: 12.0% ~ 18.0%')).toBeInTheDocument();
  });

  it('should hide budget card when marketing_budget is empty', () => {
    const calculatorResults = {
      scoring_summary: {
        conclusion: '- Finding A',
        marketing_estimation: '22.4% ~ 26.2%',
        marketing_budget: '',
        closing_message: 'Some closing message.',
      },
    };

    render(<KesimpulanSection calculatorResults={calculatorResults} />);

    expect(screen.getByText('Finding A')).toBeInTheDocument();
    expect(screen.getByText('Estimasi persentase biaya marketing sekarang:')).toBeInTheDocument();
    expect(screen.getByText('22.4% ~ 26.2%')).toBeInTheDocument();
    expect(screen.queryByText('Min. Anggaran Marketing')).not.toBeInTheDocument();
    expect(screen.getByText('Some closing message.')).toBeInTheDocument();
  });
});
