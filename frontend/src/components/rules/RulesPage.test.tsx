import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { RulesPage } from '../../pages/RulesPage';
import { RoleProtectedRoute } from '../auth/RoleProtectedRoute';
import { Header } from '../layout/Header';
import type { ScoringRule } from '../../hooks/useRules';

// Mock hooks
const mockUseRules = vi.fn();
const mockUseAuth = vi.fn();
const mockUseCurrentUser = vi.fn();

vi.mock('../../hooks/useRules', () => ({
  useRules: () => mockUseRules(),
}));

vi.mock('../../context/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useAuth: () => mockUseAuth(),
}));

vi.mock('../../hooks/useCurrentUser', () => ({
  useCurrentUser: () => mockUseCurrentUser(),
}));

vi.mock('../../components/ui/sonner', () => ({
  Toaster: () => null,
}));

// Suppress toast.error in tests
vi.mock('sonner', () => ({
  toast: { error: vi.fn(), success: vi.fn() },
}));

const FASHION_RULES = {
  operational: {
    unfulfilled_order_rate: { threshold: 1.0, points: 4, comparison: 'lte' },
    late_shipment_rate: { threshold: 1.0, points: 3, comparison: 'lte' },
    preparation_time: { threshold: 1.0, points: 3, comparison: 'lte' },
    chat_response_rate: { threshold: 95.0, comparison: 'gte', info_only: true },
    overall_rating: { threshold: 4.7, comparison: 'gte', info_only: true },
  },
  business: {
    monthly_sales_trend: { threshold_pct: 90.0, points: 10, comparison: 'gte' },
    six_month_avg_threshold: { threshold: 100000000, points: 10, comparison: 'gte' },
    conversion_rate: { threshold: 2.0, comparison: 'gte', info_only: true },
  },
  content: {
    quality_ratio: { threshold: 95.0, comparison: 'gte', info_only: true },
  },
  visitors: {
    returning_visitors_pct: { threshold: 23.0, points: 3, comparison: 'gte' },
    followers: { threshold: 50000, points: 2, comparison: 'gte' },
  },
  promo_tools: {
    usage_pct_threshold: { threshold: 80.0, opportunity_points: 5 },
    effectiveness_pct_threshold: { threshold: 90.0, opportunity_points: 10 },
  },
  products_status: {
    product_count: { threshold: 35, points: 5, comparison: 'gte' },
    store_status_points: { mall: 10, star_plus: 5, star: 0, regular: 0 },
  },
  ads: {
    roi_threshold: { threshold: 8.0, opportunity_points: 5, comparison: 'gt' },
    gmv_ratio_threshold: { threshold: 84.0, points: 5, comparison: 'lt' },
    cost_ratio_range: { min: 5.0, max: 10.0, info_only: true },
  },
  campaign: {
    participation_pct_threshold: { threshold: 90.0, opportunity_points: 10, comparison: 'gte' },
  },
  stock: {
    high_threshold: { threshold: 24, points: 10, comparison: 'gte' },
    mid_threshold: { threshold: 12, points: 5, comparison: 'gte' },
    low_penalty: { threshold: 12, points: -5, comparison: 'lt' },
  },
  discount: {
    fake_discount_flag: { points_no_flag: 5, points_flag: 0 },
  },
  interpretation: {
    ranges: [
      { min: 71, max: null, label: 'Good Candidate', verdict: '\u2714\ufe0f' },
      { min: 41, max: 70, label: 'Needs Review', verdict: '\u2b55\ufe0f' },
      { min: null, max: 40, label: 'Not Recommended', verdict: '\u274c' },
    ],
  },
};

const NON_FASHION_RULES = {
  ...FASHION_RULES,
  business: {
    ...FASHION_RULES.business,
    conversion_rate: { threshold: 3.0, comparison: 'gte', info_only: true },
  },
  ads: {
    ...FASHION_RULES.ads,
    roi_threshold: { threshold: 9.0, opportunity_points: 5, comparison: 'gt' },
  },
};

const SAMPLE_RULES: ScoringRule[] = [
  {
    id: 1,
    template: 'fashion',
    rules: FASHION_RULES as ScoringRule['rules'],
    version: 1,
    updated_by: null,
    updated_at: '2026-02-12T00:00:00Z',
  },
  {
    id: 2,
    template: 'non_fashion',
    rules: NON_FASHION_RULES as ScoringRule['rules'],
    version: 1,
    updated_by: null,
    updated_at: '2026-02-12T00:00:00Z',
  },
];

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const renderRulesPage = () => {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/rules']}>
        <Routes>
          <Route path="/rules" element={<RulesPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
};

const renderWithRoleGate = (
  authState: { user: object | null; loading: boolean },
  profileState: { profile: { role: string } | null; isLoading: boolean; isError: boolean },
) => {
  mockUseAuth.mockReturnValue(authState);
  mockUseCurrentUser.mockReturnValue(profileState);

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/rules']}>
        <Routes>
          <Route path="/login" element={<div>Login Page</div>} />
          <Route path="/dashboard" element={<div>Dashboard Page</div>} />
          <Route
            path="/rules"
            element={
              <RoleProtectedRoute allowedRoles={['leader', 'admin']}>
                <div>Rules Content</div>
              </RoleProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
};

const renderHeader = (
  profileState: { profile: { role: string } | null; isLoading: boolean; isError: boolean },
) => {
  mockUseAuth.mockReturnValue({
    user: { email: 'test@example.com' },
    loading: false,
    login: vi.fn(),
    logout: vi.fn(),
  });
  mockUseCurrentUser.mockReturnValue(profileState);

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <Header />
      </MemoryRouter>
    </QueryClientProvider>,
  );
};

beforeEach(() => {
  vi.clearAllMocks();
  // Default: authenticated leader
  mockUseAuth.mockReturnValue({
    user: { email: 'leader@example.com' },
    loading: false,
    login: vi.fn(),
    logout: vi.fn(),
  });
  mockUseCurrentUser.mockReturnValue({
    profile: { id: '1', email: 'leader@example.com', role: 'leader', created_at: '', last_login: '' },
    isLoading: false,
    isError: false,
  });
});

describe('RulesPage', () => {
  it('renders rules page with category sections', () => {
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    expect(screen.getByText('Scoring Rules')).toBeInTheDocument();
    expect(screen.getByText('Operational')).toBeInTheDocument();
    expect(screen.getByText('Business')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
    expect(screen.getByText('Visitors')).toBeInTheDocument();
    expect(screen.getByText('Promo Tools')).toBeInTheDocument();
    expect(screen.getByText('Products & Status')).toBeInTheDocument();
    expect(screen.getByText('Ads')).toBeInTheDocument();
    expect(screen.getByText('Campaign')).toBeInTheDocument();
    expect(screen.getByText('Stock')).toBeInTheDocument();
    expect(screen.getByText('Discount')).toBeInTheDocument();
    expect(screen.getByText('Score Interpretation')).toBeInTheDocument();
  });

  it('switches between fashion and non-fashion tabs', async () => {
    const user = userEvent.setup();
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    // Fashion tab is active by default — conversion_rate threshold shows "≥ 2"
    expect(screen.getByText(/\u2265 2(?![\d.])/)).toBeInTheDocument();

    // Click Non-Fashion tab
    const nonFashionTab = screen.getByRole('tab', { name: /non-fashion/i });
    await user.click(nonFashionTab);

    // Non-fashion conversion_rate threshold = 3.0 → shows "≥ 3"
    expect(screen.getByText('\u2265 3')).toBeInTheDocument();
    // ROI threshold changes from 8.0 to 9.0 → shows "> 9"
    expect(screen.getByText('> 9')).toBeInTheDocument();
  });

  it('highlights differing values between templates', async () => {
    const user = userEvent.setup();
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    // Check that "differs" badges exist for conversion_rate and roi_threshold
    const differsBadges = screen.getAllByText('differs');
    expect(differsBadges.length).toBeGreaterThan(0);
  });

  it('shows version and updated timestamp', () => {
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    expect(screen.getByText(/v1/)).toBeInTheDocument();
    expect(screen.getByText(/Updated/)).toBeInTheDocument();
  });

  it('shows loading state', () => {
    mockUseRules.mockReturnValue({
      rules: [],
      isLoading: true,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    // Loading skeleton should be present (animated pulse divs)
    const main = document.querySelector('.animate-pulse');
    expect(main).toBeInTheDocument();
  });

  it('shows error state with retry button', async () => {
    const mockRefetch = vi.fn();
    mockUseRules.mockReturnValue({
      rules: [],
      isLoading: false,
      isError: true,
      error: new Error('Failed'),
      refetch: mockRefetch,
    });

    renderRulesPage();

    expect(screen.getByText(/failed to load scoring rules/i)).toBeInTheDocument();
    const retryButton = screen.getByRole('button', { name: /retry/i });
    expect(retryButton).toBeInTheDocument();

    await userEvent.click(retryButton);
    expect(mockRefetch).toHaveBeenCalledTimes(1);
  });
});

describe('RoleProtectedRoute', () => {
  it('redirects member role to dashboard', () => {
    renderWithRoleGate(
      { user: { email: 'member@example.com' }, loading: false },
      { profile: { role: 'member' }, isLoading: false, isError: false },
    );

    expect(screen.getByText('Dashboard Page')).toBeInTheDocument();
    expect(screen.queryByText('Rules Content')).not.toBeInTheDocument();
  });

  it('allows leader role to access rules', () => {
    renderWithRoleGate(
      { user: { email: 'leader@example.com' }, loading: false },
      { profile: { role: 'leader' }, isLoading: false, isError: false },
    );

    expect(screen.getByText('Rules Content')).toBeInTheDocument();
  });

  it('allows admin role to access rules', () => {
    renderWithRoleGate(
      { user: { email: 'admin@example.com' }, loading: false },
      { profile: { role: 'admin' }, isLoading: false, isError: false },
    );

    expect(screen.getByText('Rules Content')).toBeInTheDocument();
  });

  it('redirects to login if not authenticated', () => {
    renderWithRoleGate(
      { user: null, loading: false },
      { profile: null, isLoading: false, isError: false },
    );

    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });
});

describe('Header navigation', () => {
  it('shows Rules nav link for leader role', () => {
    renderHeader({
      profile: { role: 'leader' },
      isLoading: false,
      isError: false,
    });

    expect(screen.getByRole('link', { name: /rules/i })).toBeInTheDocument();
  });

  it('shows Rules nav link for admin role', () => {
    renderHeader({
      profile: { role: 'admin' },
      isLoading: false,
      isError: false,
    });

    expect(screen.getByRole('link', { name: /rules/i })).toBeInTheDocument();
  });

  it('hides Rules nav link for member role', () => {
    renderHeader({
      profile: { role: 'member' },
      isLoading: false,
      isError: false,
    });

    const navLinks = screen.getAllByRole('link');
    const rulesLink = navLinks.find((link) => link.textContent === 'Rules');
    expect(rulesLink).toBeUndefined();
  });
});
