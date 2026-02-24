import { useState, useRef, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Toaster } from './components/ui/sonner';
import { DowntimeWarningDialog } from './components/DowntimeWarningDialog';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { BrandsPage } from './pages/BrandsPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { HistoryPage } from './pages/HistoryPage';
import { EvaluationDetailPage } from './pages/EvaluationDetailPage';
import { RulesPage } from './pages/RulesPage';
import { AccountsPage } from './pages/AccountsPage';
import { RoleProtectedRoute } from './components/auth/RoleProtectedRoute';

const queryClient = new QueryClient();

function App() {
  const [showDowntimeWarning, setShowDowntimeWarning] = useState(false);
  const downtimeDismissedRef = useRef(false);

  const handleDismiss = useCallback(() => {
    setShowDowntimeWarning(false);
    downtimeDismissedRef.current = true;
  }, []);

  useEffect(() => {
    const handler = () => {
      if (!downtimeDismissedRef.current) {
        setShowDowntimeWarning(true);
      }
    };
    window.addEventListener('api-server-error', handler);
    return () => window.removeEventListener('api-server-error', handler);
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-[100] focus:bg-background focus:text-foreground focus:px-4 focus:py-2 focus:rounded-md focus:ring-2 focus:ring-ring focus:outline-none"
        >
          Skip to main content
        </a>
        <AuthProvider>
          <DowntimeWarningDialog open={showDowntimeWarning} onDismiss={handleDismiss} />
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/brands"
              element={
                <ProtectedRoute>
                  <BrandsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/evaluation/:brandId"
              element={
                <ProtectedRoute>
                  <EvaluationPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/history/:id"
              element={
                <ProtectedRoute>
                  <EvaluationDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <HistoryPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/rules"
              element={
                <RoleProtectedRoute allowedRoles={['leader', 'admin']}>
                  <RulesPage />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="/accounts"
              element={
                <RoleProtectedRoute
                  allowedRoles={['admin']}
                  accessDeniedMessage="Akses ditolak — halaman akun hanya untuk admin"
                >
                  <AccountsPage />
                </RoleProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
          <Toaster />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
