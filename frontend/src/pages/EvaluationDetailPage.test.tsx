import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { EvaluationDetailPage } from './EvaluationDetailPage';

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
    expect(screen.getByText('1.500.000')).toBeInTheDocument();
    expect(screen.getByText('500.000')).toBeInTheDocument();
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
    expect(screen.getByText('250.000')).toBeInTheDocument();
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
});
