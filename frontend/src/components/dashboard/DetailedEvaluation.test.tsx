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
