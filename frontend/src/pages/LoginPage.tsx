import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { FirebaseError } from 'firebase/app';

interface LoginForm {
  email: string;
  password: string;
}

export const LoginPage = () => {
  const { t } = useTranslation();
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>();

  // Get the intended destination or default to /dashboard
  const from =
    (location.state as { from?: Location })?.from?.pathname || '/dashboard';

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      navigate(from, { replace: true });
    }
  }, [user, navigate, from]);

  const onSubmit = async (data: LoginForm) => {
    setError(null);
    setIsSubmitting(true);
    try {
      await login(data.email, data.password);
      navigate(from, { replace: true });
    } catch (err) {
      if (err instanceof FirebaseError) {
        setError(getFirebaseErrorMessage(t, err.code));
      } else {
        setError(t('login.error.unexpected'));
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Don't render form while redirecting (user is logged in)
  if (user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted">
        <div className="text-muted-foreground">{t('login.redirecting')}</div>
      </div>
    );
  }

  return (
    <main id="main-content" tabIndex={-1} className="min-h-screen flex items-center justify-center bg-muted">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-semibold text-foreground mb-6 text-center">
          {t('login.title')}
        </h1>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-destructive text-sm">{error}</p>
            </div>
          )}

          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-foreground mb-1"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              aria-describedby={errors.email ? 'email-error' : undefined}
              aria-invalid={errors.email ? 'true' : 'false'}
              className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent text-foreground"
              {...register('email', {
                required: t('login.emailRequired'),
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: t('login.emailInvalid'),
                },
              })}
            />
            {errors.email && (
              <p id="email-error" role="alert" className="mt-1 text-sm text-destructive">
                {errors.email.message}
              </p>
            )}
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-foreground mb-1"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              aria-describedby={errors.password ? 'password-error' : undefined}
              aria-invalid={errors.password ? 'true' : 'false'}
              className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent text-foreground"
              {...register('password', {
                required: t('login.passwordRequired'),
              })}
            />
            {errors.password && (
              <p id="password-error" role="alert" className="mt-1 text-sm text-destructive">
                {errors.password.message}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-2 px-4 bg-primary text-white font-medium rounded-lg hover:bg-primary/85 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSubmitting ? t('login.loggingIn') : 'Login'}
          </button>
        </form>
      </div>
    </main>
  );
};

const getFirebaseErrorMessage = (t: (key: string) => string, code: string): string => {
  switch (code) {
    case 'auth/user-not-found':
    case 'auth/wrong-password':
    case 'auth/invalid-credential':
      return t('login.error.invalidCredential');
    case 'auth/too-many-requests':
      return t('login.error.tooManyRequests');
    case 'auth/user-disabled':
      return t('login.error.accountDisabled');
    default:
      return t('login.error.loginFailed');
  }
};
