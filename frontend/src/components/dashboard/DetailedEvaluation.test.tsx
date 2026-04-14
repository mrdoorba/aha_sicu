import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { DetailedEvaluation } from './DetailedEvaluation';

const makeRow = (metric: string, verdict = '✔️') => ({
  metric,
  value: 100,
  benchmark: '>= 50',
  verdict,
  message: '',
  score: 10,
});

const scoreBreakdown = [
  {
    category: 'Data Iklan',
    score: 30,
    max_score: 40,
    rows: [
      makeRow('Penjualan'),
      makeRow('Biaya'),
      makeRow('ROI'),
      makeRow('Iklan check up', '❌'),
    ],
  },
];

describe('DetailedEvaluation', () => {
  it('renders all provided metric cards', () => {
    render(<DetailedEvaluation scoreBreakdown={scoreBreakdown} />);
    expect(screen.getByText('Penjualan')).toBeInTheDocument();
    expect(screen.getByText('Biaya')).toBeInTheDocument();
    expect(screen.getByText('ROI')).toBeInTheDocument();
    expect(screen.getByText('Iklan check up')).toBeInTheDocument();
  });

  it('shows fallback when there are no rows', () => {
    const emptyRows = [
      {
        category: 'Data Iklan',
        score: 0,
        max_score: 10,
        rows: [],
      },
    ];
    render(<DetailedEvaluation scoreBreakdown={emptyRows} />);
    // Should render without errors
    expect(screen.getByRole('tabpanel')).toBeInTheDocument();
  });

  it('returns null when scoreBreakdown is empty', () => {
    const { container } = render(<DetailedEvaluation scoreBreakdown={[]} />);
    expect(container.innerHTML).toBe('');
  });

  it('should render separator after Rata² Penjualan in Bisnis tab', () => {
    const bisnis = [
      {
        category: 'Bisnis',
        score: 20,
        max_score: 30,
        rows: [
          makeRow('Rata² Penjualan 6 bulan terakhir'),
          makeRow('Tingkat Konversi'),
        ],
      },
    ];
    const { container } = render(<DetailedEvaluation scoreBreakdown={bisnis} />);
    const separators = container.querySelectorAll('.border-primary\\/30');
    expect(separators.length).toBe(1);
  });

  it('should render separator after Program Afiliasi in Alat Promo tab', () => {
    const alatPromo = [
      {
        category: 'Alat Promo',
        score: 15,
        max_score: 20,
        rows: [
          makeRow('Program Afiliasi'),
          makeRow('% Penggunaan alat promosi'),
        ],
      },
    ];
    const { container } = render(<DetailedEvaluation scoreBreakdown={alatPromo} />);
    const separators = container.querySelectorAll('.border-primary\\/30');
    expect(separators.length).toBe(1);
  });

  it('shows affiliate commission in the promo tab when manual inputs include it', () => {
    const alatPromo = [
      {
        category: 'Alat Promo',
        score: 15,
        max_score: 20,
        rows: [
          makeRow('Program Afiliasi'),
          makeRow('% Penggunaan alat promosi'),
        ],
      },
    ];

    render(
      <DetailedEvaluation
        scoreBreakdown={alatPromo}
        manualInputs={{ promoTools: { komisiProgramAfiliasi: 123456 } }}
      />,
    );

    expect(
      screen.getByText(/fields\.promoTools\.komisiProgramAfiliasi|Komisi dari Program Afiliasi|Commission from Affiliate Program/),
    ).toBeInTheDocument();
    expect(screen.getByText('123,456')).toBeInTheDocument();
  });

  it('shows discount affiliate commission inline before the fake discount warning in the existing discount card', () => {
    const discount = [
      {
        category: 'Discount',
        score: 5,
        max_score: 10,
        rows: [
          {
            ...makeRow('Checkup Diskon'),
            message: '',
            message_i18n: {
              key: 'scoring.discountCheckup.fail',
              vars: {
                discountPct: '11.0%',
                rangeMin: '0.1%',
                rangeMax: '38.1%',
                voucherPct: '0.0%',
                paketPct: '0.0%',
              },
            },
          },
        ],
      },
    ];

    const { container } = render(
      <DetailedEvaluation
        scoreBreakdown={discount}
        calculatorResults={{
          discount: {
            details: {
              i18n: {
                affiliateCommission: {
                  key: 'discount.output.affiliateCommission',
                  vars: { value: '1.5%' },
                },
              },
            },
          },
        }}
      />,
    );

    const card = screen.getByText('Checkup Diskon').closest('div.rounded-lg');
    expect(card).not.toBeNull();
    const cardText = (card as HTMLElement).textContent ?? '';
    expect(cardText).toContain('% Diskon TOP SKU: 11.0%');
    expect(cardText).toContain('Range: 0.1% ~ 38.1%');
    expect(cardText).toContain('Voucher 0.0%');
    expect(cardText).toContain('Paket Diskon 0.0%');
    expect(cardText).toContain('% Komisi Afiliasi: 1.5%');
    expect(cardText).toContain('📌 Berpotensi menggunakan \'fake discount\'');
    expect(cardText.indexOf('Paket Diskon 0.0%')).toBeLessThan(cardText.indexOf('% Komisi Afiliasi: 1.5%'));
    expect(cardText.indexOf('% Komisi Afiliasi: 1.5%')).toBeLessThan(cardText.indexOf('📌 Berpotensi menggunakan \'fake discount\''));

    const metricCards = container.querySelectorAll('.bg-card.p-4.space-y-3');
    expect(metricCards).toHaveLength(1);
  });

  it('merges a standalone discount affiliate row into the main discount card', () => {
    const discount = [
      {
        category: 'Discount',
        score: 5,
        max_score: 10,
        rows: [
          {
            ...makeRow('Checkup Diskon'),
            message_i18n: {
              key: 'scoring.discountCheckup.fail',
              vars: {
                discountPct: '11.0%',
                rangeMin: '0.1%',
                rangeMax: '38.1%',
                voucherPct: '0.0%',
                paketPct: '0.0%',
              },
            },
          },
          {
            ...makeRow('% Komisi Afiliasi'),
            value: '19.3%',
            message: '% Komisi Afiliasi: 19.3%',
          },
        ],
      },
    ];

    const { container } = render(<DetailedEvaluation scoreBreakdown={discount} />);

    const card = screen.getByText('Checkup Diskon').closest('div.rounded-lg');
    expect(card).not.toBeNull();
    const cardText = (card as HTMLElement).textContent ?? '';
    expect(cardText).toContain('% Komisi Afiliasi: 19.3%');
    expect(cardText.indexOf('Paket Diskon 0.0%')).toBeLessThan(cardText.indexOf('% Komisi Afiliasi: 19.3%'));
    expect(cardText.indexOf('% Komisi Afiliasi: 19.3%')).toBeLessThan(cardText.indexOf('📌 Berpotensi menggunakan \'fake discount\''));

    const metricCards = container.querySelectorAll('.bg-card.p-4.space-y-3');
    expect(metricCards).toHaveLength(1);
  });

  it('merges a standalone discount affiliate row when its percent is stored as a numeric value', () => {
    const discount = [
      {
        category: 'Discount',
        score: 5,
        max_score: 10,
        rows: [
          {
            ...makeRow('Checkup Diskon'),
            message_i18n: {
              key: 'scoring.discountCheckup.fail',
              vars: {
                discountPct: '11.0%',
                rangeMin: '0.1%',
                rangeMax: '38.1%',
                voucherPct: '0.0%',
                paketPct: '0.0%',
              },
            },
          },
          {
            ...makeRow('% Komisi Afiliasi'),
            value: 0.193,
            message: '',
          },
        ],
      },
    ];

    const { container } = render(<DetailedEvaluation scoreBreakdown={discount} />);

    const card = screen.getByText('Checkup Diskon').closest('div.rounded-lg');
    expect(card).not.toBeNull();
    const cardText = (card as HTMLElement).textContent ?? '';
    expect(cardText).toContain('% Komisi Afiliasi: 19.3%');

    const metricCards = container.querySelectorAll('.bg-card.p-4.space-y-3');
    expect(metricCards).toHaveLength(1);
  });

  it('does not hide the main discount card when the checkup message already contains affiliate commission text', () => {
    const discount = [
      {
        category: 'Discount',
        score: 5,
        max_score: 10,
        rows: [
          {
            ...makeRow('Checkup Diskon'),
            value: '% Diskon TOP SKU: 11.0%',
            message: '% Diskon TOP SKU: 11.0%\nRange: 0.1% ~ 38.1%\nVoucher 0.0%\nPaket Diskon 0.0%\n% Komisi Afiliasi: 19.3%\n📌 Berpotensi menggunakan \'fake discount\'',
          },
        ],
      },
    ];

    const { container } = render(<DetailedEvaluation scoreBreakdown={discount} />);

    expect(screen.getByText('Checkup Diskon')).toBeInTheDocument();
    expect(screen.getByText(/Komisi Afiliasi: 19.3%/)).toBeInTheDocument();
    expect(screen.queryByText('Detail metrik tidak tersedia untuk evaluasi ini.')).not.toBeInTheDocument();

    const metricCards = container.querySelectorAll('.bg-card.p-4.space-y-3');
    expect(metricCards).toHaveLength(1);
  });

  it('should render separator after ROI in Iklan tab and pair percentage metrics on same row', () => {
    const iklan = [
      {
        category: 'Data Iklan',
        score: 30,
        max_score: 40,
        rows: [
          makeRow('Penjualan'),
          makeRow('Biaya'),
          makeRow('ROI'),
          makeRow('% GMV Iklan / GMV Toko'),
          makeRow('% Biaya Iklan / GMV Toko'),
        ],
      },
    ];
    const { container } = render(<DetailedEvaluation scoreBreakdown={iklan} />);
    const separators = container.querySelectorAll('.border-primary\\/30');
    expect(separators.length).toBe(1);
    // The two percentage metrics should exist after the separator (no spacer between them)
    expect(screen.getByText('% GMV Iklan / GMV Toko')).toBeInTheDocument();
    expect(screen.getByText('% Biaya Iklan / GMV Toko')).toBeInTheDocument();
  });
});
