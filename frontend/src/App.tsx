import { lazy, Suspense, useState, useRef, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Toaster } from './components/ui/sonner';
import { DowntimeWarningDialog } from './components/DowntimeWarningDialog';
import { RoleProtectedRoute } from './components/auth/RoleProtectedRoute';

const LoginPage = lazy(() => import('./pages/LoginPage').then((module) => ({ default: module.LoginPage })));
const DashboardPage = lazy(() => import('./pages/DashboardPage').then((module) => ({ default: module.DashboardPage })));
const BrandsPage = lazy(() => import('./pages/BrandsPage').then((module) => ({ default: module.BrandsPage })));
const EvaluationPage = lazy(() => import('./pages/EvaluationPage').then((module) => ({ default: module.EvaluationPage })));
const HistoryPage = lazy(() => import('./pages/HistoryPage').then((module) => ({ default: module.HistoryPage })));
const EvaluationDetailPage = lazy(() => import('./pages/EvaluationDetailPage').then((module) => ({ default: module.EvaluationDetailPage })));
const RulesPage = lazy(() => import('./pages/RulesPage').then((module) => ({ default: module.RulesPage })));
const AccountsPage = lazy(() => import('./pages/AccountsPage').then((module) => ({ default: module.AccountsPage })));
const EmailHistoryPage = lazy(() => import('./pages/EmailHistoryPage').then((module) => ({ default: module.EmailHistoryPage })));
const MainLayout = lazy(() => import('./components/layout/MainLayout').then((module) => ({ default: module.MainLayout })));

const queryClient = new QueryClient();

function App() {
  const { t } = useTranslation();
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
          <Suspense fallback={null}>
            <Routes>
              <Route path="/login" element={<LoginPage />} />

              <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/brands" element={<BrandsPage />} />
                <Route path="/evaluation/:brandId" element={<EvaluationPage />} />
                <Route
                  path="/history/:id"
                  element={
                    <RoleProtectedRoute allowedRoles={['leader', 'admin']}>
                      <EvaluationDetailPage />
                    </RoleProtectedRoute>
                  }
                />
                <Route
                  path="/history"
                  element={
                    <RoleProtectedRoute allowedRoles={['leader', 'admin']}>
                      <HistoryPage />
                    </RoleProtectedRoute>
                  }
                />

                <Route
                  path="/email-history"
                  element={
                    <RoleProtectedRoute
                      allowedRoles={['leader', 'admin']}
                      accessDeniedMessage={t('auth.accessDeniedEmailHistory')}
                    >
                      <EmailHistoryPage />
                    </RoleProtectedRoute>
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
                      accessDeniedMessage={t('auth.accessDeniedAccounts')}
                    >
                      <AccountsPage />
                    </RoleProtectedRoute>
                  }
                />
              </Route>

              <Route path="/" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Suspense>
          <Toaster />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
