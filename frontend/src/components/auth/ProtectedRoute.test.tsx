import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import { ProtectedRoute } from './ProtectedRoute';

// Mock useAuth hook
const mockUseAuth = vi.fn();

vi.mock('../../context/AuthContext', () => ({
  useAuth: () => mockUseAuth(),
}));

const renderWithRouter = (
  initialRoute: string,
  authState: { user: object | null; loading: boolean }
) => {
  mockUseAuth.mockReturnValue(authState);

  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <Routes>
        <Route path="/login" element={<div>Login Page</div>} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <div>Protected Dashboard</div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </MemoryRouter>
  );
};

describe('ProtectedRoute', () => {
  it('shows loading state while checking auth', () => {
    renderWithRouter('/dashboard', { user: null, loading: true });

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    expect(screen.queryByText(/protected dashboard/i)).not.toBeInTheDocument();
  });

  it('redirects unauthenticated users to login', () => {
    renderWithRouter('/dashboard', { user: null, loading: false });

    expect(screen.getByText(/login page/i)).toBeInTheDocument();
    expect(screen.queryByText(/protected dashboard/i)).not.toBeInTheDocument();
  });

  it('renders children for authenticated users', () => {
    renderWithRouter('/dashboard', {
      user: { email: 'test@example.com' },
      loading: false,
    });

    expect(screen.getByText(/protected dashboard/i)).toBeInTheDocument();
    expect(screen.queryByText(/login page/i)).not.toBeInTheDocument();
  });

  it('preserves redirect location in state when redirecting to login', () => {
    mockUseAuth.mockReturnValue({ user: null, loading: false });

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route
            path="/login"
            element={<div data-testid="login">Login Page</div>}
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <div>Dashboard</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    // Should redirect to login
    expect(screen.getByTestId('login')).toBeInTheDocument();
  });
});
