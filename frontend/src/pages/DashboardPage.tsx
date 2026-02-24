import { useTranslation } from 'react-i18next';
import { Header } from '../components/layout/Header';
import { useAuth } from '../context/AuthContext';

export const DashboardPage = () => {
  const { t } = useTranslation();
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-muted">
      <Header />
      <main id="main-content" tabIndex={-1} className="mx-auto max-w-7xl py-6 px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">
            {t('dashboard.welcome')}
          </h2>
          <p className="text-muted-foreground mb-4">
            {t('dashboard.loggedInAs')}{' '}
            <span className="font-medium text-foreground">{user?.email}</span>
          </p>
          <div className="rounded-lg border-4 border-dashed border-border p-8 text-center">
            <p className="text-muted-foreground">
              {t('dashboard.placeholder')}
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};
