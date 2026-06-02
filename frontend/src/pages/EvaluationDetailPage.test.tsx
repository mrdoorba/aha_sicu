import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { EvaluationDetailPage } from './EvaluationDetailPage';

vi.mock('../hooks/useSendPlainEmail', () => ({
  useSendPlainEmail: () => ({ mutate: vi.fn(), isPending: false }),
}));

const mockRefetch = vi.fn();

const MOCK_EVALUATION = {
  id: 42,
  brand_id: 10,
  brand_name: 'Nike Indonesia',
  final_score: 78.5,
  verdict: '\u2714\uFE0F',
  template: 'fashion',
  score_breakdown: [
    { category: 'Operational', score: 10.0, max_score: 10.0, rows: [], available: true },
    { category: 'Business', score: 18.0, max_score: 20.0, rows: [], available: true },
    { category: 'Promo Tools', score: -5.0, max_score: 0, rows: [], available: true },
  ],
  calculator_results: {
    ads_keyword: { details: {}, output_text: 'AK analysis text output' },
    top_sku: {
      details: {
        output_1: [{ kode_variasi: 'V001', product_name: 'Shoe A', total_omzet: 50000000, rata2_harga_jual: 250000 }],
        output_2: [{ kode_variasi: 'V002', nama_produk: 'Shoe B', varian: 'Red', stok: 120 }],
        average_stock: 150,
      },
      output_text: 'Top SKU text',
    },
    discount: { details: {}, output_text: '% Diskon TOP SKU: 2.7%' },
  },
  manual_inputs: {
    operational: { pesanan_tidak_terselesaikan: 0.5, keterlambatan: 0.3 },
    business: { monthly_sales: [100000000, 120000000], conversion_rate: 2.5 },
  },
  email_output: 'Dear Team,\n\nBrand evaluation for Nike Indonesia is complete.',
  evaluator_email: 'rina@company.com',
  created_at: '2026-02-10T10:30:00Z',
  rule_version: 1,
  brand_raw_data: {
    email: 'pic@nike.com',
    pic_name: 'Budi Santoso',
    store_link: 'https://shopee.co.id/nike',
    kategori: 'Fashion',
  },
};

let mockHookReturn = {
  evaluation: MOCK_EVALUATION as typeof MOCK_EVALUATION | null,
  isLoading: false,
  isError: false,
  isNotFound: false,
  error: null as Error | null,
  refetch: mockRefetch,
};

const mockUseEvaluationDetail = vi.fn(() => mockHookReturn);

vi.mock('../hooks/useEvaluationDetail', () => ({
  useEvaluationDetail: (...args: unknown[]) => mockUseEvaluationDetail(...args),
}));

// Mock Header to avoid auth context issues
vi.mock('../components/layout/Header', () => ({
  Header: () => <header data-testid="mock-header">Header</header>,
}));

// Mock useCurrentUser
let mockProfile: { id: string; email: string; role: string; created_at: string; last_login: string } | null = {
  id: '1',
  email: 'member@company.com',
  role: 'member',
  created_at: '2026-01-01T00:00:00Z',
  last_login: '2026-02-20T00:00:00Z',
};

vi.mock('../hooks/useCurrentUser', () => ({
  useCurrentUser: () => ({
    profile: mockProfile,
    isLoading: false,
    isError: false,
  }),
}));

// Mock useDeleteEvaluation
const mockMutate = vi.fn();

vi.mock('../hooks/useDeleteEvaluation', () => ({
  useDeleteEvaluation: () => ({
    mutate: mockMutate,
    isPending: false,
  }),
}));

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: { error: vi.fn(), success: vi.fn() },
}));

function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location">{location.pathname}</div>;
}

const renderPage = (path = '/history/42') => {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/history/:id" element={<EvaluationDetailPage />} />
        <Route path="/history" element={<div data-testid="history-page">History</div>} />
      </Routes>
      <LocationDisplay />
    </MemoryRouter>,
  );
};

beforeEach(() => {
  mockHookReturn = {
    evaluation: MOCK_EVALUATION,
    isLoading: false,
    isError: false,
    isNotFound: false,
    error: null,
    refetch: mockRefetch,
  };
  mockProfile = {
    id: '3',
    email: 'member@company.com',
    role: 'member',
    created_at: '2026-01-01T00:00:00Z',
    last_login: '2026-02-20T00:00:00Z',
  };
  mockUseEvaluationDetail.mockImplementation(() => mockHookReturn);
  vi.clearAllMocks();
});

describe('EvaluationDetailPage', () => {
  it('renders brand info header with name, template badge, evaluator, and date', () => {
    renderPage();

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Nike Indonesia');
    expect(screen.getAllByText('Fashion').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/rina@company\.com/)).toBeInTheDocument();
    expect(screen.getByText(/2026/)).toBeInTheDocument();
  });

  it('renders score breakdown table with per-category scores', () => {
    renderPage();

    expect(screen.getByText('Rincian Skor')).toBeInTheDocument();
    expect(screen.getByText('Operational')).toBeInTheDocument();
    expect(screen.getByText('10.0/10')).toBeInTheDocument();
    expect(screen.getByText('Business')).toBeInTheDocument();
    expect(screen.getByText('18.0/20')).toBeInTheDocument();
    expect(screen.getByText('Promo Tools')).toBeInTheDocument();
  });

  it('renders calculator results (ads keyword text, top SKU tables, discount values)', async () => {
    const user = userEvent.setup();
    renderPage();

    expect(screen.getByText('Hasil Kalkulator')).toBeInTheDocument();
    // Ads Keyword
    expect(screen.getByText('Analisis Ads Keyword')).toBeInTheDocument();
    expect(screen.getByText('AK analysis text output')).toBeInTheDocument();
    // Top SKU — section heading and average stock visible before expanding
    expect(screen.getByText('Analisis Top SKU')).toBeInTheDocument();
    expect(screen.getByText('150')).toBeInTheDocument();
    // Expand the collapsible to see table rows
    await user.click(screen.getByText('Lihat Detail'));
    expect(screen.getByText('V001')).toBeInTheDocument();
    expect(screen.getByText('Shoe A')).toBeInTheDocument();
    // Discount
    expect(screen.getByText('Cek Diskon')).toBeInTheDocument();
    expect(screen.getByText(/Diskon TOP SKU/)).toBeInTheDocument();
  });

  it('renders manual inputs organized by category', () => {
    renderPage();

    expect(screen.getByText('Input Manual')).toBeInTheDocument();
    expect(screen.getByText('Kesehatan Operasional Toko')).toBeInTheDocument();
    expect(screen.getByText('Bisnis Analisis')).toBeInTheDocument();
    expect(screen.getByText('pesanan tidak terselesaikan')).toBeInTheDocument();
  });

  it('renders Indonesian labels and benchmarks for known formConfig fields', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluation: {
        ...MOCK_EVALUATION,
        manual_inputs: {
          operational: { unfulfilledOrderRate: 0.5, chatResponseRate: 96 },
        },
      },
    };
    renderPage();

    // Indonesian labels from OPERATIONAL_FIELDS
    expect(screen.getByText('Tingkat Pesanan Tidak Terselesaikan')).toBeInTheDocument();
    expect(screen.getByText('Persentase Chat Dibalas')).toBeInTheDocument();
    // Benchmark display in muted text
    expect(screen.getByText('(<1%)')).toBeInTheDocument();
    expect(screen.getByText('(>95%)')).toBeInTheDocument();
    // Percentage formatting via inputType + unit
    expect(screen.getByText(/0\.5%/)).toBeInTheDocument();
    expect(screen.getByText(/96%/)).toBeInTheDocument();
  });

  it('preserves decimals for non-currency manual numeric inputs on the detail page', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluation: {
        ...MOCK_EVALUATION,
        manual_inputs: {
          operational: { preparationTime: 1.82, overallRating: 4.88 },
        },
      },
    };
    renderPage();

    expect(screen.getByText('Masa Pengemasan')).toBeInTheDocument();
    expect(screen.getByText('Keseluruhan Penilaian')).toBeInTheDocument();
    expect(screen.getByText('1.82')).toBeInTheDocument();
    expect(screen.getByText('4.88')).toBeInTheDocument();
  });

  it('formats currency fields using Indonesian locale', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluation: {
        ...MOCK_EVALUATION,
        manual_inputs: {
          ads: { adSales: 1500000, adCost: 500000 },
        },
      },
    };
    renderPage();

    expect(screen.getByText('Data Iklan')).toBeInTheDocument();
    expect(screen.getByText('Penjualan Iklan')).toBeInTheDocument();
    expect(screen.getByText('Biaya Iklan')).toBeInTheDocument();
    expect(screen.getByText('1,500,000')).toBeInTheDocument();
    expect(screen.getByText('500,000')).toBeInTheDocument();
  });

  it('renders competition fields with dot-notation key resolution', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluation: {
        ...MOCK_EVALUATION,
        manual_inputs: {
          competition: {
            product1: { productName: 'Sepatu A', sellingPrice: 250000, keyword: null, link: null, marketPrice: null },
            product2: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
            product3: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
          },
        },
      },
    };
    renderPage();

    expect(screen.getByText('Kompetisi TOP Produk')).toBeInTheDocument();
    expect(screen.getByText('Produk Kompetitor 1')).toBeInTheDocument();
    expect(screen.getAllByText('Nama Produk').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Sepatu A')).toBeInTheDocument();
    expect(screen.getAllByText('Harga Jual').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('250,000')).toBeInTheDocument();
  });

  it('renders dynamic month labels when salesStartMonth is present', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluation: {
        ...MOCK_EVALUATION,
        manual_inputs: {
          business: {
            salesStartMonth: '2026-02',
            salesMonth0: 5000000,
            salesMonth1: 4000000,
            conversionRate: 3.5,
          },
        },
      },
    };
    renderPage();

    expect(screen.getByText('Bisnis Analisis')).toBeInTheDocument();
    // Dynamic month labels from generateMonthLabels('2026-02')
    expect(screen.getByText('Penjualan Feb 2026')).toBeInTheDocument();
    expect(screen.getByText('Penjualan Jan 2026')).toBeInTheDocument();
    // Conversion rate with benchmark
    expect(screen.getByText('Tingkat Konversi')).toBeInTheDocument();
    expect(screen.getByText(/3\.5%/)).toBeInTheDocument();
    expect(screen.getByText('(>3%)')).toBeInTheDocument();
  });

  it('renders email output section with copy button when email_output present', () => {
    renderPage();

    expect(screen.getByText('Email Output')).toBeInTheDocument();
    expect(screen.getByText(/Brand evaluation for Nike Indonesia/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /email output/i })).toBeInTheDocument();
  });

  it('hides email section when email_output is null', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluation: { ...MOCK_EVALUATION, email_output: null },
    };

    renderPage();

    expect(screen.queryByText('Email Output')).not.toBeInTheDocument();
  });

  it('copies email output to clipboard on copy button click', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText },
      writable: true,
      configurable: true,
    });

    renderPage();

    const copyBtn = screen.getByRole('button', { name: /email output/i });
    await userEvent.click(copyBtn);

    expect(writeText).toHaveBeenCalledWith(MOCK_EVALUATION.email_output);
  });

  it('shows loading skeleton', () => {
    mockHookReturn = {
      evaluation: null,
      isLoading: true,
      isError: false,
      isNotFound: false,
      error: null,
      refetch: mockRefetch,
    };

    renderPage();

    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();
  });

  it('shows error state with retry button', async () => {
    mockHookReturn = {
      evaluation: null,
      isLoading: false,
      isError: true,
      isNotFound: false,
      error: new Error('Network error'),
      refetch: mockRefetch,
    };

    renderPage();

    expect(screen.getByText('Gagal memuat detail evaluasi')).toBeInTheDocument();
    const retryBtn = screen.getByRole('button', { name: /coba lagi/i });
    expect(retryBtn).toBeInTheDocument();

    await userEvent.click(retryBtn);
    expect(mockRefetch).toHaveBeenCalledTimes(1);
  });

  it('shows 404 not found state for invalid ID', () => {
    mockHookReturn = {
      evaluation: null,
      isLoading: false,
      isError: false,
      isNotFound: false,
      error: null,
      refetch: mockRefetch,
    };

    renderPage('/history/invalid');

    expect(screen.getByText('Evaluasi tidak ditemukan')).toBeInTheDocument();
    const backButtons = screen.getAllByRole('button', { name: /kembali ke riwayat/i });
    expect(backButtons.length).toBeGreaterThanOrEqual(2);
  });

  it('shows 404 not found when API returns EVAL_NOT_FOUND', () => {
    mockHookReturn = {
      evaluation: null,
      isLoading: false,
      isError: true,
      isNotFound: true,
      error: new Error('Evaluation not found'),
      refetch: mockRefetch,
    };

    renderPage('/history/99999');

    expect(screen.getByText('Evaluasi tidak ditemukan')).toBeInTheDocument();
    const backButtons = screen.getAllByRole('button', { name: /kembali ke riwayat/i });
    expect(backButtons.length).toBeGreaterThanOrEqual(2);
  });

  it('back to history button navigates to /history', async () => {
    renderPage();

    const backBtn = screen.getByRole('button', { name: /kembali ke riwayat/i });
    await userEvent.click(backBtn);

    await waitFor(() => {
      expect(screen.getByTestId('location')).toHaveTextContent('/history');
    });
  });

  // --- Delete button visibility by role (Task 7.3) ---

  it('shows delete button for leader role', () => {
    mockProfile = {
      id: '1',
      email: 'leader@company.com',
      role: 'leader',
      created_at: '2026-01-01T00:00:00Z',
      last_login: '2026-02-20T00:00:00Z',
    };
    renderPage();

    expect(screen.getByRole('button', { name: /hapus evaluasi/i })).toBeInTheDocument();
  });

  it('shows delete button for admin role', () => {
    mockProfile = {
      id: '2',
      email: 'admin@company.com',
      role: 'admin',
      created_at: '2026-01-01T00:00:00Z',
      last_login: '2026-02-20T00:00:00Z',
    };
    renderPage();

    expect(screen.getByRole('button', { name: /hapus evaluasi/i })).toBeInTheDocument();
  });

  it('does not show delete button for member role', () => {
    mockProfile = {
      id: '3',
      email: 'member@company.com',
      role: 'member',
      created_at: '2026-01-01T00:00:00Z',
      last_login: '2026-02-20T00:00:00Z',
    };
    renderPage();

    expect(screen.queryByRole('button', { name: /hapus evaluasi/i })).not.toBeInTheDocument();
  });

  it('opens delete dialog when delete button is clicked', async () => {
    mockProfile = {
      id: '1',
      email: 'leader@company.com',
      role: 'leader',
      created_at: '2026-01-01T00:00:00Z',
      last_login: '2026-02-20T00:00:00Z',
    };
    renderPage();

    const deleteBtn = screen.getByRole('button', { name: /hapus evaluasi/i });
    await userEvent.click(deleteBtn);

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText(/permanen dan tidak dapat dibatalkan/)).toBeInTheDocument();
    });
  });

  // --- Category translation tests (CATEGORY_MAP + t()) ---

  it('translates Indonesian backend category names via CATEGORY_MAP', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluation: {
        ...MOCK_EVALUATION,
        score_breakdown: [
          { category: 'Kesehatan Operasional Toko', score: 10.0, max_score: 10.0, rows: [], available: true },
          { category: 'Bisnis Analisis', score: 18.0, max_score: 20.0, rows: [], available: true },
          { category: 'Promo Toko', score: 5.0, max_score: 10.0, rows: [], available: true },
        ],
      },
    };
    renderPage();

    // Default test locale is 'id', so t('rules.category.operational') → 'Operasional'
    expect(screen.getByText('Operasional')).toBeInTheDocument();
    expect(screen.getByText('Bisnis')).toBeInTheDocument();
    expect(screen.getByText('Alat Promo')).toBeInTheDocument();
  });

  it('renders unknown category names as-is (raw fallback)', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluation: {
        ...MOCK_EVALUATION,
        score_breakdown: [
          { category: 'Custom Category XYZ', score: 7.0, max_score: 10.0, rows: [], available: true },
          { category: 'Operational', score: 10.0, max_score: 10.0, rows: [], available: true },
        ],
      },
    };
    renderPage();

    // Unknown category renders as-is
    expect(screen.getByText('Custom Category XYZ')).toBeInTheDocument();
    // 'Operational' is not in CATEGORY_MAP (map uses Indonesian names), so also renders as-is
    expect(screen.getByText('Operational')).toBeInTheDocument();
  });

  // --- ScoringConclusionSection tests ---

  it('renders scoring conclusion section with i18n fields when scoring_summary present', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluation: {
        ...MOCK_EVALUATION,
        calculator_results: {
          ...MOCK_EVALUATION.calculator_results,
          scoring_summary: {
            conclusion: 'Toko Anda memiliki performa yang baik',
            conclusion_i18n: [
              { key: 'scoring.conclusion.good', vars: { score: '78.5' } },
              { key: 'scoring.conclusion.improvement', vars: { area: 'ads' } },
            ],
            marketing_budget: 'Rp 5,000,000',
            marketing_budget_i18n: { key: 'scoring.marketingBudget', vars: { amount: '5,000,000', currency: 'IDR' } },
            closing_message: 'Terima kasih atas kerjasamanya',
            closing_message_i18n: { key: 'scoring.closingMessage.standard', vars: { brand: 'Nike' } },
          },
        },
      },
    };
    renderPage();

    // Section heading (id locale: "Kesimpulan")
    expect(screen.getByText('Kesimpulan')).toBeInTheDocument();

    // conclusion_i18n items render via t() — keys not in locale file return the key itself
    expect(screen.getByText('scoring.conclusion.good')).toBeInTheDocument();
    expect(screen.getByText('scoring.conclusion.improvement')).toBeInTheDocument();

    // Marketing budget label and value via renderTranslatable (i18n key returned as-is)
    expect(screen.getByText('Min. Anggaran Marketing')).toBeInTheDocument();
    expect(screen.getByText('scoring.marketingBudget')).toBeInTheDocument();

    // Closing message via renderTranslatable (i18n key returned as-is)
    expect(screen.getByText('scoring.closingMessage.standard')).toBeInTheDocument();
  });

  it('renders scoring conclusion with raw fallback when i18n fields are absent', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluation: {
        ...MOCK_EVALUATION,
        calculator_results: {
          ...MOCK_EVALUATION.calculator_results,
          scoring_summary: {
            conclusion: '- Toko bagus\n- Perlu perbaikan iklan',
            marketing_budget: 'Rp 5,000,000',
            closing_message: 'Terima kasih',
          },
        },
      },
    };
    renderPage();

    // Section heading
    expect(screen.getByText('Kesimpulan')).toBeInTheDocument();

    // Raw conclusion parsed into bullet points
    expect(screen.getByText('Toko bagus')).toBeInTheDocument();
    expect(screen.getByText('Perlu perbaikan iklan')).toBeInTheDocument();

    // Marketing budget label and raw value
    expect(screen.getByText('Min. Anggaran Marketing')).toBeInTheDocument();
    expect(screen.getByText('Rp 5,000,000')).toBeInTheDocument();

    // Closing message raw text
    expect(screen.getByText('Terima kasih')).toBeInTheDocument();
  });

  // --- AdsKeywordSection i18n tests ---

  it('renders translated ads keyword text when i18n fields present in details', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluation: {
        ...MOCK_EVALUATION,
        calculator_results: {
          ...MOCK_EVALUATION.calculator_results,
          ads_keyword: {
            output_text: 'AK analysis text output',
            details: {
              ak2_i18n: { key: 'ads.summary', vars: { active: '10', paused: '5', ended: '3', unique_count: '20', product_pct: '40%', total_products: '50' } },
              ak3_i18n: { key: 'ads.typeBreakdown', vars: { semua_total: '8', toko_total: '4', toko_auto: '2', toko_manual: '2' } },
              ak4_i18n: [
                { key: 'ads.flag.activeGood', vars: {} },
              ],
              al2_i18n: {
                header: { key: 'ads.topHeader', vars: {} },
                ads: [{ key: 'ads.topAd', vars: { name: 'Ad1', gmv: '100', roas: '5', biddingKey: 'ads.value.biddingOtomatis', jenisKey: 'ads.value.iklanProduk', penempatanKey: 'ads.value.semuaPenempatan', keyword: 'shoes' } }],
              },
              al3_i18n: { key: 'ads.topRecommendation.auto', vars: {} },
              al5_i18n: {
                header: { key: 'ads.bottomHeader', vars: {} },
                ads: [{ key: 'ads.bottomAd', vars: { name: 'Ad2', cost: '50', roas: '1', biddingKey: 'ads.value.biddingManual', jenisKey: 'ads.value.iklanToko', penempatanKey: 'ads.value.halamanPencarian', keyword: 'sandals' } }],
              },
            },
          },
        },
      },
    };
    renderPage();

    // Should NOT show the raw output_text
    expect(screen.queryByText('AK analysis text output')).not.toBeInTheDocument();
    // Should show translated ads summary (i18n key with vars rendered by i18next)
    expect(screen.getByText(/Total Iklan/)).toBeInTheDocument();
  });

  it('renders raw output_text for ads keyword when i18n fields absent', () => {
    // Default MOCK_EVALUATION has details: {} — no i18n fields
    renderPage();

    expect(screen.getByText('AK analysis text output')).toBeInTheDocument();
  });

  // --- DiscountSection i18n tests ---

  it('renders translated discount text when i18n dict present in details', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluation: {
        ...MOCK_EVALUATION,
        calculator_results: {
          ...MOCK_EVALUATION.calculator_results,
          discount: {
            output_text: '% Diskon TOP SKU: 2.7%',
            details: {
              i18n: {
                topSkuDiscount: { key: 'discount.output.topSkuDiscount', vars: { value: '2.7%' } },
                range: { key: 'discount.output.range', vars: { min: '0%', max: '10%' } },
                voucher: { key: 'discount.output.voucher', vars: { value: '5%' } },
                packageDiscount: { key: 'discount.output.packageDiscount', vars: { value: '3%' } },
                affiliateCommission: { key: 'discount.output.affiliateCommission', vars: { value: '1.5%' } },
              },
            },
          },
        },
      },
    };
    renderPage();

    // Should NOT show the raw output_text as a standalone pre block
    // Instead should show translated discount lines
    // i18n renders: "% Diskon TOP SKU: 2.7%" from discount.output.topSkuDiscount key
    expect(screen.getByText(/Diskon TOP SKU.*2\.7%/)).toBeInTheDocument();
    expect(screen.getByText(/Voucher.*5%/)).toBeInTheDocument();
    expect(screen.getByText(/Komisi Afiliasi.*1\.5%/)).toBeInTheDocument();
  });

  it('renders raw output_text for discount when i18n dict absent', () => {
    // Default MOCK_EVALUATION has details: {} — no i18n
    renderPage();

    expect(screen.getByText(/Diskon TOP SKU/)).toBeInTheDocument();
  });

  it('renders nothing for scoring conclusion when scoring_summary is missing', () => {
    // MOCK_EVALUATION.calculator_results has no scoring_summary by default
    renderPage();

    // The section heading "Kesimpulan" should not appear in the calculator results area
    // (it would only appear if ScoringConclusionSection rendered)
    expect(screen.queryByText('Kesimpulan')).not.toBeInTheDocument();
  });

  // --- EmailOutputSection i18n tests ---

  it('renders translated email sections when score_breakdown has message_i18n', () => {
    mockHookReturn = {
      ...mockHookReturn,
      evaluation: {
        ...MOCK_EVALUATION,
        score_breakdown: [
          {
            category: 'Kesehatan Operasional Toko',
            score: 10.0,
            max_score: 10.0,
            available: true,
            rows: [
              { row: 1, metric: 'unfulfilled', value: '0.5%', benchmark: '<1%', verdict: 'pass', message: 'OK', score: 2, message_i18n: { key: 'scoring.unfulfilledOrderRate.pass', vars: { value: '0.5%' } } },
            ],
          },
        ],
      },
    };
    renderPage();

    // Should show translated content from buildI18nEmailBody
    // The i18n key resolves via test i18n setup — check that the section header appears
    expect(screen.getByText(/Performa Operasional Toko/)).toBeInTheDocument();
    // Should NOT show the raw email_output text
    expect(screen.queryByText('Brand evaluation for Nike Indonesia')).not.toBeInTheDocument();
  });

  it('renders raw email output when score_breakdown lacks message_i18n', () => {
    // Default MOCK_EVALUATION score_breakdown has rows: [] — no message_i18n
    renderPage();

    expect(screen.getByText(/Brand evaluation for Nike Indonesia/)).toBeInTheDocument();
  });

  it('copies translated email text when i18n available', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText },
      writable: true,
      configurable: true,
    });

    mockHookReturn = {
      ...mockHookReturn,
      evaluation: {
        ...MOCK_EVALUATION,
        score_breakdown: [
          {
            category: 'Kesehatan Operasional Toko',
            score: 10.0,
            max_score: 10.0,
            available: true,
            rows: [
              { row: 1, metric: 'unfulfilled', value: '0.5%', benchmark: '<1%', verdict: 'pass', message: 'OK', score: 2, message_i18n: { key: 'scoring.unfulfilledOrderRate.pass', vars: { value: '0.5%' } } },
            ],
          },
        ],
      },
    };
    renderPage();

    const copyBtn = screen.getByRole('button', { name: /email output/i });
    await userEvent.click(copyBtn);

    // Should NOT copy the raw emailOutput, but the translated body
    expect(writeText).not.toHaveBeenCalledWith(MOCK_EVALUATION.email_output);
    // Should copy some text that includes the translated section
    expect(writeText).toHaveBeenCalledTimes(1);
    const copiedText = writeText.mock.calls[0][0] as string;
    expect(copiedText).toContain('Performa Operasional Toko');
  });
});
