import { render, screen } from '@testing-library/react';
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

  it('skip-to-content link targets an element with id="main-content"', () => {
    render(<App />);

    const skipLink = screen.getByRole('link', { name: /skip to main content/i });
    expect(skipLink).toHaveAttribute('href', '#main-content');

    const target = document.getElementById('main-content');
    expect(target).toBeInTheDocument();
    expect(target).toHaveAttribute('tabIndex', '-1');
  });
});
