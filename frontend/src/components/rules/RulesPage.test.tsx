import { render, screen } from '@testing-library/react';
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
const mockUpdateRuleMutateAsync = vi.fn();

vi.mock('../../hooks/useRules', () => ({
  useRules: () => mockUseRules(),
}));

vi.mock('../../hooks/useUpdateRule', () => ({
  useUpdateRule: () => ({
    mutateAsync: mockUpdateRuleMutateAsync,
    isPending: false,
  }),
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

// Mock toast
const mockToastSuccess = vi.fn();
vi.mock('sonner', () => ({
  toast: { error: vi.fn(), success: (...args: unknown[]) => mockToastSuccess(...args) },
}));

// Mock firebase/auth for PasswordConfirmDialog
const mockReauthenticateUser = vi.fn();
vi.mock('../../firebase/auth', () => ({
  reauthenticateUser: (...args: unknown[]) => mockReauthenticateUser(...args),
  getCurrentUserToken: vi.fn().mockResolvedValue('mock-token'),
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
  marketing: {
    floor: { value: 0.15 },
    base_subtraction: { value: 0.03 },
    upper_limit_base: { value: 0.20 },
    fashion_adjustment: { value: 0.05 },
    minimum_threshold: { value: 0.10 },
    display_max: { value: 0.25 },
    display_min: { value: 0.10 },
  },
  interpretation: {},
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
  marketing: {
    ...FASHION_RULES.marketing,
    floor: { value: 0.12 },
    fashion_adjustment: { value: 0.0 },
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
  queryClient.clear();
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

    expect(screen.getByText('Aturan Penilaian')).toBeInTheDocument();
    expect(screen.getByText('Operasional')).toBeInTheDocument();
    expect(screen.getByText('Bisnis')).toBeInTheDocument();
    expect(screen.getByText('Pengunjung')).toBeInTheDocument();
    expect(screen.getByText('Alat Promo')).toBeInTheDocument();
    expect(screen.getByText('Produk & Status')).toBeInTheDocument();
    expect(screen.getByText('Iklan')).toBeInTheDocument();
    expect(screen.getByText('Campaign')).toBeInTheDocument();
    expect(screen.getByText('Stok')).toBeInTheDocument();
    expect(screen.getByText('Diskon')).toBeInTheDocument();
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

    expect(screen.getByText(/Diperbarui/)).toBeInTheDocument();
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

    expect(screen.getByText(/gagal memuat aturan penilaian/i)).toBeInTheDocument();
    const retryButton = screen.getByRole('button', { name: /coba lagi/i });
    expect(retryButton).toBeInTheDocument();

    await userEvent.click(retryButton);
    expect(mockRefetch).toHaveBeenCalledTimes(1);
  });
});

describe('Edit mode', () => {
  it('shows Edit Rules button for leader', () => {
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    expect(screen.getByRole('button', { name: /edit aturan/i })).toBeInTheDocument();
  });

  it('shows Edit Rules button for admin', () => {
    mockUseCurrentUser.mockReturnValue({
      profile: { id: '2', email: 'admin@example.com', role: 'admin', created_at: '', last_login: '' },
      isLoading: false,
      isError: false,
    });
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    expect(screen.getByRole('button', { name: /edit aturan/i })).toBeInTheDocument();
  });

  it('hides Edit Rules button for member', () => {
    mockUseCurrentUser.mockReturnValue({
      profile: { id: '3', email: 'member@example.com', role: 'member', created_at: '', last_login: '' },
      isLoading: false,
      isError: false,
    });
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    expect(screen.queryByRole('button', { name: /edit aturan/i })).not.toBeInTheDocument();
  });

  it('enters edit mode on Edit Rules click', async () => {
    const user = userEvent.setup();
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    await user.click(screen.getByRole('button', { name: /edit aturan/i }));

    // Edit mode shows Cancel and Save Changes buttons
    expect(screen.getByRole('button', { name: /batal/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /simpan perubahan/i })).toBeInTheDocument();
    // Edit Rules button hidden in edit mode
    expect(screen.queryByRole('button', { name: /edit aturan/i })).not.toBeInTheDocument();
    // Number inputs should appear
    const inputs = screen.getAllByRole('spinbutton');
    expect(inputs.length).toBeGreaterThan(0);
  });

  it('Save Changes disabled when no changes made', async () => {
    const user = userEvent.setup();
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    await user.click(screen.getByRole('button', { name: /edit aturan/i }));

    const saveBtn = screen.getByRole('button', { name: /simpan perubahan/i });
    expect(saveBtn).toBeDisabled();
  });

  it('Save Changes enabled after modifying value', async () => {
    const user = userEvent.setup();
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    await user.click(screen.getByRole('button', { name: /edit aturan/i }));

    // Modify a threshold — find the first number input and change it
    const firstInput = screen.getAllByRole('spinbutton')[0];
    await user.clear(firstInput);
    await user.type(firstInput, '99');

    const saveBtn = screen.getByRole('button', { name: /simpan perubahan/i });
    expect(saveBtn).toBeEnabled();
  });

  it('opens password dialog on Save Changes', async () => {
    const user = userEvent.setup();
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    await user.click(screen.getByRole('button', { name: /edit aturan/i }));

    // Modify a value first
    const firstInput = screen.getAllByRole('spinbutton')[0];
    await user.clear(firstInput);
    await user.type(firstInput, '99');

    await user.click(screen.getByRole('button', { name: /simpan perubahan/i }));

    // Password dialog should appear
    expect(screen.getByText('Konfirmasi Password')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
  });

  it('successful password confirmation triggers mutation and exits edit mode', async () => {
    const user = userEvent.setup();
    mockReauthenticateUser.mockResolvedValue(undefined);
    mockUpdateRuleMutateAsync.mockResolvedValue({});

    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    // Enter edit mode
    await user.click(screen.getByRole('button', { name: /edit aturan/i }));

    // Modify a value
    const firstInput = screen.getAllByRole('spinbutton')[0];
    await user.clear(firstInput);
    await user.type(firstInput, '99');

    // Click Save Changes
    await user.click(screen.getByRole('button', { name: /simpan perubahan/i }));

    // Enter password in dialog
    const passwordInput = screen.getByLabelText('Password');
    await user.type(passwordInput, 'mypassword');

    // Click Confirm
    const confirmBtn = screen.getByRole('button', { name: /^konfirmasi$/i });
    await user.click(confirmBtn);

    // Verify mutation was called
    expect(mockUpdateRuleMutateAsync).toHaveBeenCalled();
    // Verify toast
    expect(mockToastSuccess).toHaveBeenCalledWith('Aturan berhasil diperbarui');
  });

  it('incorrect password shows error in dialog', async () => {
    const user = userEvent.setup();
    mockReauthenticateUser.mockRejectedValue(new Error('auth/wrong-password'));

    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    // Enter edit mode
    await user.click(screen.getByRole('button', { name: /edit aturan/i }));

    // Modify a value
    const firstInput = screen.getAllByRole('spinbutton')[0];
    await user.clear(firstInput);
    await user.type(firstInput, '99');

    // Click Save Changes
    await user.click(screen.getByRole('button', { name: /simpan perubahan/i }));

    // Enter wrong password
    const passwordInput = screen.getByLabelText('Password');
    await user.type(passwordInput, 'wrongpassword');

    // Click Confirm
    const confirmBtn = screen.getByRole('button', { name: /^konfirmasi$/i });
    await user.click(confirmBtn);

    // Error shown
    expect(await screen.findByText('Password salah')).toBeInTheDocument();
    // Mutation NOT called
    expect(mockUpdateRuleMutateAsync).not.toHaveBeenCalled();
  });

  it('Cancel exits edit mode without saving', async () => {
    const user = userEvent.setup();
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    // Enter edit mode
    await user.click(screen.getByRole('button', { name: /edit aturan/i }));

    // Modify a value
    const firstInput = screen.getAllByRole('spinbutton')[0];
    await user.clear(firstInput);
    await user.type(firstInput, '99');

    // Click Cancel
    await user.click(screen.getByRole('button', { name: /batal/i }));

    // Back to view mode — Edit Rules button visible again
    expect(screen.getByRole('button', { name: /edit aturan/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /simpan perubahan/i })).not.toBeInTheDocument();
    // No API call made
    expect(mockUpdateRuleMutateAsync).not.toHaveBeenCalled();
  });

  it('Save Changes disabled when field is cleared (validation error)', async () => {
    const user = userEvent.setup();
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    // Enter edit mode
    await user.click(screen.getByRole('button', { name: /edit aturan/i }));

    // Clear a value to trigger validation error
    const firstInput = screen.getAllByRole('spinbutton')[0];
    await user.clear(firstInput);

    // Save Changes should be disabled
    const saveBtn = screen.getByRole('button', { name: /simpan perubahan/i });
    expect(saveBtn).toBeDisabled();

    // Should show validation error
    expect(screen.getByText('Wajib diisi')).toBeInTheDocument();
  });

  it('shows success toast after save', async () => {
    const user = userEvent.setup();
    mockReauthenticateUser.mockResolvedValue(undefined);
    mockUpdateRuleMutateAsync.mockResolvedValue({});

    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    await user.click(screen.getByRole('button', { name: /edit aturan/i }));
    const firstInput = screen.getAllByRole('spinbutton')[0];
    await user.clear(firstInput);
    await user.type(firstInput, '99');
    await user.click(screen.getByRole('button', { name: /simpan perubahan/i }));
    const passwordInput = screen.getByLabelText('Password');
    await user.type(passwordInput, 'mypassword');
    await user.click(screen.getByRole('button', { name: /^konfirmasi$/i }));

    expect(mockToastSuccess).toHaveBeenCalledWith('Aturan berhasil diperbarui');
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

    expect(screen.getByRole('link', { name: /aturan/i })).toBeInTheDocument();
  });

  it('shows Rules nav link for admin role', () => {
    renderHeader({
      profile: { role: 'admin' },
      isLoading: false,
      isError: false,
    });

    expect(screen.getByRole('link', { name: /aturan/i })).toBeInTheDocument();
  });

  it('hides Rules nav link for member role', () => {
    renderHeader({
      profile: { role: 'member' },
      isLoading: false,
      isError: false,
    });

    const navLinks = screen.getAllByRole('link');
    const rulesLink = navLinks.find((link) => link.textContent === 'Aturan');
    expect(rulesLink).toBeUndefined();
  });
});

describe('Marketing category', () => {
  it('renders marketing category card with all fields', () => {
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    expect(screen.getByText('Marketing')).toBeInTheDocument();
    expect(screen.getByText('Config')).toBeInTheDocument();
    expect(screen.getByText('Batas Bawah')).toBeInTheDocument();
    expect(screen.getByText('Pengurangan Dasar')).toBeInTheDocument();
    expect(screen.getByText('Batas Atas Dasar')).toBeInTheDocument();
    expect(screen.getByText('Penyesuaian Fashion')).toBeInTheDocument();
    expect(screen.getByText('Ambang Minimum')).toBeInTheDocument();
    expect(screen.getByText('Tampilan Maks')).toBeInTheDocument();
    expect(screen.getByText('Tampilan Min')).toBeInTheDocument();
  });

  it('marketing fields are editable in edit mode', async () => {
    const user = userEvent.setup();
    mockUseRules.mockReturnValue({
      rules: SAMPLE_RULES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    await user.click(screen.getByRole('button', { name: /edit aturan/i }));

    // Find a marketing field input by aria-label
    const floorInput = screen.getByRole('spinbutton', { name: /floor value/i });
    expect(floorInput).toBeInTheDocument();
    expect(floorInput).toHaveValue(0.15);
  });

});

// --- Message templates tests (Story 5.5) ---

const RULES_WITH_MESSAGES: ScoringRule[] = [
  {
    id: 1,
    template: 'fashion',
    rules: {
      ...FASHION_RULES,
      operational: {
        unfulfilled_order_rate: {
          threshold: 1.0, points: 4, comparison: 'lte',
          message_pass: '✔️ UFO = {val_str} OK',
          message_fail: '❌ UFO = {val_str} NOT OK, target: <{threshold}%',
        },
        late_shipment_rate: { threshold: 1.0, points: 3, comparison: 'lte' },
        preparation_time: { threshold: 1.0, points: 3, comparison: 'lte' },
        chat_response_rate: { threshold: 95.0, comparison: 'gte', info_only: true },
        overall_rating: { threshold: 4.7, comparison: 'gte', info_only: true },
      },
      competition: {
        message_pass: '✅kompetitif',
        message_fail: '❌tidak kompetitif (harga kisaran pasaran: IDR {market_price})',
      },
      interpretation: {
        closing_messages: {
          '✔️': 'Closing pass message',
          '❌': 'Closing fail message',
          '': 'Closing neutral message',
        },
      },
    } as ScoringRule['rules'],
    version: 2,
    updated_by: null,
    updated_at: '2026-02-12T00:00:00Z',
  },
  {
    id: 2,
    template: 'non_fashion',
    rules: {
      ...NON_FASHION_RULES,
      competition: {
        message_pass: '✅kompetitif',
        message_fail: '❌tidak kompetitif',
      },
      interpretation: {
        closing_messages: {
          '✔️': 'Closing pass message NF',
          '❌': 'Closing fail message NF',
        },
      },
    } as ScoringRule['rules'],
    version: 2,
    updated_by: null,
    updated_at: '2026-02-12T00:00:00Z',
  },
];

describe('Message templates', () => {
  it('renders message toggle button when rule has message fields', () => {
    mockUseRules.mockReturnValue({
      rules: RULES_WITH_MESSAGES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    // UFO rate has 2 message fields → should show "2 msg" toggle
    const toggleBtn = screen.getByLabelText('Toggle messages for Tingkat Pesanan Tidak Terselesaikan');
    expect(toggleBtn).toBeInTheDocument();
    expect(toggleBtn).toHaveTextContent('2 msg');
  });

  it('expands message templates on toggle click', async () => {
    const user = userEvent.setup();
    mockUseRules.mockReturnValue({
      rules: RULES_WITH_MESSAGES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    // Click toggle to expand messages
    const toggleBtn = screen.getByLabelText('Toggle messages for Tingkat Pesanan Tidak Terselesaikan');
    await user.click(toggleBtn);

    // Message text should now be visible
    expect(screen.getByText(/UFO = \{val_str\} OK/)).toBeInTheDocument();
    expect(screen.getByText(/UFO = \{val_str\} NOT OK/)).toBeInTheDocument();
  });

  it('shows textareas for message templates in edit mode', async () => {
    const user = userEvent.setup();
    mockUseRules.mockReturnValue({
      rules: RULES_WITH_MESSAGES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    // Enter edit mode
    await user.click(screen.getByRole('button', { name: /edit aturan/i }));

    // Expand messages
    const toggleBtn = screen.getByLabelText('Toggle messages for Tingkat Pesanan Tidak Terselesaikan');
    await user.click(toggleBtn);

    // Should show textareas with message content
    const passTextarea = screen.getByLabelText('Tingkat Pesanan Tidak Terselesaikan Lulus');
    expect(passTextarea).toBeInTheDocument();
    expect(passTextarea).toHaveValue('✔️ UFO = {val_str} OK');

    const failTextarea = screen.getByLabelText('Tingkat Pesanan Tidak Terselesaikan Gagal');
    expect(failTextarea).toBeInTheDocument();
    expect(failTextarea).toHaveValue('❌ UFO = {val_str} NOT OK, target: <{threshold}%');
  });

  it('shows placeholder hints in edit mode', async () => {
    const user = userEvent.setup();
    mockUseRules.mockReturnValue({
      rules: RULES_WITH_MESSAGES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    // Enter edit mode
    await user.click(screen.getByRole('button', { name: /edit aturan/i }));

    // Expand messages
    const toggleBtn = screen.getByLabelText('Toggle messages for Tingkat Pesanan Tidak Terselesaikan');
    await user.click(toggleBtn);

    // Should show placeholder hints (multiple instances for pass and fail)
    const placeholderLabels = screen.getAllByText('Placeholder:');
    expect(placeholderLabels.length).toBeGreaterThan(0);
    const valStrHints = screen.getAllByText('{val_str}');
    expect(valStrHints.length).toBeGreaterThan(0);
  });

  it('message template edits trigger change detection', async () => {
    const user = userEvent.setup();
    mockUseRules.mockReturnValue({
      rules: RULES_WITH_MESSAGES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    // Enter edit mode
    await user.click(screen.getByRole('button', { name: /edit aturan/i }));

    // Expand messages
    const toggleBtn = screen.getByLabelText('Toggle messages for Tingkat Pesanan Tidak Terselesaikan');
    await user.click(toggleBtn);

    // Edit message template
    const passTextarea = screen.getByLabelText('Tingkat Pesanan Tidak Terselesaikan Lulus');
    await user.clear(passTextarea);
    await user.type(passTextarea, 'EDITED PASS MESSAGE');

    // Save Changes should be enabled now
    const saveBtn = screen.getByRole('button', { name: /simpan perubahan/i });
    expect(saveBtn).toBeEnabled();
  });

  it('renders Competition Messages section', () => {
    mockUseRules.mockReturnValue({
      rules: RULES_WITH_MESSAGES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    expect(screen.getByText('Pesan Kompetisi')).toBeInTheDocument();
    expect(screen.getByText('Kompetitif')).toBeInTheDocument();
    expect(screen.getByText('Tidak kompetitif')).toBeInTheDocument();
  });

  it('renders G75 Closing Messages section', () => {
    mockUseRules.mockReturnValue({
      rules: RULES_WITH_MESSAGES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    expect(screen.getByText('Pesan Penutup (G75)')).toBeInTheDocument();
    expect(screen.getByText('Closing pass message')).toBeInTheDocument();
    expect(screen.getByText('Closing fail message')).toBeInTheDocument();
  });

  it('closing messages have textareas in edit mode', async () => {
    const user = userEvent.setup();
    mockUseRules.mockReturnValue({
      rules: RULES_WITH_MESSAGES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    // Enter edit mode
    await user.click(screen.getByRole('button', { name: /edit aturan/i }));

    // Closing message textareas should appear
    const closingTextarea = screen.getByLabelText(/closing message for ✔️/i);
    expect(closingTextarea).toBeInTheDocument();
    expect(closingTextarea).toHaveValue('Closing pass message');
  });

  it('edited message templates are included in save payload', async () => {
    const user = userEvent.setup();
    mockReauthenticateUser.mockResolvedValue(undefined);
    mockUpdateRuleMutateAsync.mockResolvedValue({});

    mockUseRules.mockReturnValue({
      rules: RULES_WITH_MESSAGES,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    renderRulesPage();

    // Enter edit mode
    await user.click(screen.getByRole('button', { name: /edit aturan/i }));

    // Expand and edit message
    const toggleBtn = screen.getByLabelText('Toggle messages for Tingkat Pesanan Tidak Terselesaikan');
    await user.click(toggleBtn);

    const passTextarea = screen.getByLabelText('Tingkat Pesanan Tidak Terselesaikan Lulus');
    await user.clear(passTextarea);
    await user.type(passTextarea, 'NEW PASS MSG');

    // Save
    await user.click(screen.getByRole('button', { name: /simpan perubahan/i }));
    const passwordInput = screen.getByLabelText('Password');
    await user.type(passwordInput, 'mypassword');
    await user.click(screen.getByRole('button', { name: /^konfirmasi$/i }));

    // Verify the mutation was called with the edited message
    expect(mockUpdateRuleMutateAsync).toHaveBeenCalled();
    const callArgs = mockUpdateRuleMutateAsync.mock.calls[0][0];
    expect(callArgs.rules.operational.unfulfilled_order_rate.message_pass).toBe('NEW PASS MSG');
  });
});
