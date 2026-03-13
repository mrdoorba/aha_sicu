import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { FirebaseError } from 'firebase/app';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { ArrowRight, Loader2 } from 'lucide-react';

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

  const from = (location.state as { from?: Location })?.from?.pathname || '/dashboard';

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

  if (user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="size-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-background overflow-hidden">
      {/* Branding Pane (60%) */}
      <div className="hidden lg:flex lg:w-3/5 bg-foreground relative overflow-hidden items-center justify-center p-16">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_20%_20%,#325FEC_0%,transparent_40%)]" />
          <div className="absolute bottom-0 right-0 w-full h-full bg-[radial-gradient(circle_at_80%_80%,#325FEC_0%,transparent_40%)]" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-[radial-gradient(circle_at_center,#325FEC_0%,transparent_70%)] opacity-10" />
        </div>

        {/* Abstract shapes for premium feel */}
        <div className="absolute top-1/4 -left-20 w-64 h-64 bg-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 -right-20 w-80 h-80 bg-primary/10 rounded-full blur-3xl" />

        {/* Top Centered AHA Logo */}
        <div className="absolute top-16 left-0 w-full flex justify-center z-20 px-8">
          <img src="/images/aha-logo-color.webp" alt="AHA Commerce" className="h-24 md:h-32 w-fit drop-shadow-md brightness-0 invert" />
        </div>

        <div className="relative z-10 max-w-xl space-y-8 w-full">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-2xl bg-white flex items-center justify-center shadow-lg shadow-white/20">
              <img src="/images/aha-logo-icon.webp" alt="Store ICU Logo" className="size-8 object-contain" />
            </div>
            <span className="text-3xl font-black tracking-tighter text-white">Store ICU</span>
          </div>

          <h2 className="text-5xl font-black tracking-tight text-white leading-[1.1]">
            Elevating E-commerce <br />
            <span className="text-sidebar-accent">Operations Intelligence</span>
          </h2>
        </div>
      </div>

      {/* Login Form Pane (40%) */}
      <main className="w-full lg:w-2/5 flex flex-col items-center justify-between p-8 bg-background relative py-12">
        {/* Background decorative element */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/5 rounded-full blur-3xl pointer-events-none" />

        {/* Center Content */}
        <div className="w-full max-w-md space-y-10 relative z-10 flex-1 flex flex-col justify-center my-8">
          <div className="text-center lg:text-left space-y-2">
            <h1 className="text-3xl font-black tracking-tight text-foreground">
              {t('login.title')}
            </h1>
            <p className="text-muted-foreground font-medium">
              {t('login.subtitle')}
            </p>
          </div>

          {/* Form container with glassmorphism */}
          <div className="p-10 space-y-8 bg-card/30 backdrop-blur-2xl border border-border/50 shadow-2xl rounded-[2.5rem]">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {error && (
                <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-2xl flex items-center gap-3">
                  <div className="h-2 w-2 rounded-full bg-destructive animate-pulse" />
                  <p className="text-destructive text-sm font-semibold">{error}</p>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-bold tracking-wide uppercase text-muted-foreground ml-1">
                  {t('login.emailLabel')}
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@company.com"
                  autoComplete="email"
                  className="h-12 px-4 rounded-xl border-border/60 bg-background/50 focus-visible:ring-primary/20 transition-all"
                  {...register('email', {
                    required: t('login.emailRequired'),
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: t('login.emailInvalid'),
                    },
                  })}
                />
                {errors.email && (
                  <p className="mt-1 text-xs font-bold text-destructive ml-1">
                    {errors.email.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-bold tracking-wide uppercase text-muted-foreground ml-1">
                  {t('login.passwordLabel')}
                </Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  autoComplete="current-password"
                  className="h-12 px-4 rounded-xl border-border/60 bg-background/50 focus-visible:ring-primary/20 transition-all"
                  {...register('password', {
                    required: t('login.passwordRequired'),
                  })}
                />
                {errors.password && (
                  <p className="mt-1 text-xs font-bold text-destructive ml-1">
                    {errors.password.message}
                  </p>
                )}
              </div>

              <Button
                type="submit"
                disabled={isSubmitting}
                aria-label={t('login.signIn')}
                className="w-full h-12 rounded-xl text-base font-bold tracking-tight shadow-xl shadow-primary/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                {isSubmitting ? (
                  <Loader2 className="size-5 animate-spin" />
                ) : (
                  <>
                    {t('login.signIn')}
                    <ArrowRight className="ml-2 size-5" />
                  </>
                )}
              </Button>
            </form>
          </div>

        </div>

        {/* Bottom Image */}
        <div className="w-full flex justify-center relative z-10 mt-auto">
          <img src="/images/gopn-banner.webp" alt="Garansi Omzet dan Profit Naik" className="h-20 md:h-28 object-contain drop-shadow-sm" />
        </div>
      </main>
    </div>
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
