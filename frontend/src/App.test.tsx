import { render, screen, act, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import App from './App';

vi.mock('./context/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useAuth: () => ({
    user: null,
    loading: false,
    login: vi.fn(),
    logout: vi.fn(),
  }),
}));

vi.mock('./components/auth/ProtectedRoute', () => ({
  ProtectedRoute: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('./components/auth/RoleProtectedRoute', () => ({
  RoleProtectedRoute: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock('./pages/RulesPage', () => ({
  RulesPage: () => <main id="main-content" tabIndex={-1}>Rules</main>,
}));

vi.mock('./pages/EvaluationPage', () => ({
  EvaluationPage: () => <main id="main-content" tabIndex={-1}>Evaluation</main>,
}));

vi.mock('./pages/HistoryPage', () => ({
  HistoryPage: () => <main id="main-content" tabIndex={-1}>History</main>,
}));

vi.mock('./pages/EvaluationDetailPage', () => ({
  EvaluationDetailPage: () => <main id="main-content" tabIndex={-1}>Detail</main>,
}));

vi.mock('./components/ui/sonner', () => ({
  Toaster: () => null,
}));

vi.mock('./pages/LoginPage', () => ({
  LoginPage: () => <div>Login Page</div>,
}));

vi.mock('./pages/DashboardPage', () => ({
  DashboardPage: () => <main id="main-content" tabIndex={-1}>Dashboard</main>,
}));

vi.mock('./pages/BrandsPage', () => ({
  BrandsPage: () => <main id="main-content" tabIndex={-1}>Brands</main>,
}));

describe('App', () => {
  it('renders skip-to-content link with correct href', () => {
    render(<App />);

    const skipLink = screen.getByRole('link', { name: /skip to main content/i });
    expect(skipLink).toBeInTheDocument();
    expect(skipLink).toHaveAttribute('href', '#main-content');
  });

  it('skip-to-content link targets an element with id="main-content"', async () => {
    render(<App />);

    const skipLink = screen.getByRole('link', { name: /skip to main content/i });
    expect(skipLink).toHaveAttribute('href', '#main-content');

    await waitFor(() => {
      expect(document.getElementById('main-content')).toBeInTheDocument();
    });

    const target = document.getElementById('main-content');
    expect(target).toBeInTheDocument();
    expect(target).toHaveAttribute('tabIndex', '-1');
  });

  describe('downtime warning dialog', () => {
    it('does not show the dialog initially', () => {
      render(<App />);

      expect(screen.queryByText('Sistem Tidak Tersedia')).not.toBeInTheDocument();
    });

    it('shows the dialog when api-server-error event is dispatched', () => {
      render(<App />);

      act(() => {
        window.dispatchEvent(new CustomEvent('api-server-error'));
      });

      expect(screen.getByText('Sistem Tidak Tersedia')).toBeInTheDocument();
      expect(screen.getByText('Mengerti')).toBeInTheDocument();
    });

    it('dismisses the dialog when Mengerti is clicked', async () => {
      const user = userEvent.setup();
      render(<App />);

      act(() => {
        window.dispatchEvent(new CustomEvent('api-server-error'));
      });

      expect(screen.getByText('Sistem Tidak Tersedia')).toBeInTheDocument();

      await user.click(screen.getByText('Mengerti'));

      expect(screen.queryByText('Sistem Tidak Tersedia')).not.toBeInTheDocument();
    });

    it('does not reappear after dismissal on subsequent server-error events', async () => {
      const user = userEvent.setup();
      render(<App />);

      act(() => {
        window.dispatchEvent(new CustomEvent('api-server-error'));
      });

      await user.click(screen.getByText('Mengerti'));

      act(() => {
        window.dispatchEvent(new CustomEvent('api-server-error'));
      });

      expect(screen.queryByText('Sistem Tidak Tersedia')).not.toBeInTheDocument();
    });
  });
});
