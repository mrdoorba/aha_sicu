import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MainLayout } from './MainLayout';

const mockLogout = vi.fn();
vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({ user: { email: 'x@example.com' }, logout: mockLogout }),
}));

let mockError: { code?: string } | null = null;
vi.mock('../../hooks/useCurrentUser', () => ({
  useCurrentUser: () => ({ profile: null, isLoading: false, isError: !!mockError, error: mockError }),
}));

// Sidebar pulls in i18n/router chrome we don't care about here.
vi.mock('./Sidebar', () => ({ Sidebar: () => <div data-testid="sidebar" /> }));

const renderLayout = () =>
  render(
    <BrowserRouter>
      <MainLayout />
    </BrowserRouter>
  );

describe('MainLayout provisioning gate', () => {
  beforeEach(() => {
    mockError = null;
  });

  it('shows the not-provisioned dead-end on AUTH_USER_NOT_PROVISIONED', () => {
    mockError = { code: 'AUTH_USER_NOT_PROVISIONED' };
    renderLayout();
    expect(screen.getByText('Account not provisioned')).toBeInTheDocument();
    expect(screen.queryByTestId('sidebar')).not.toBeInTheDocument();
  });

  it('renders the normal shell when provisioned', () => {
    renderLayout();
    expect(screen.queryByText('Account not provisioned')).not.toBeInTheDocument();
    expect(screen.getAllByTestId('sidebar').length).toBeGreaterThan(0);
  });
});
