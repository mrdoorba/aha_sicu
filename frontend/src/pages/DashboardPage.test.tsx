import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { DashboardPage } from './DashboardPage';

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: { email: 'test@example.com' },
    logout: vi.fn(),
  }),
}));

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

const renderDashboardPage = () => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('DashboardPage', () => {
  it('renders search for brand heading initially', () => {
    renderDashboardPage();

    expect(screen.getByText(/cari merek/i)).toBeInTheDocument();
  });
});
