import type { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Check } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useOnboardingLanguage } from '../../lib/onboardingLanguage';
import { DeadlineMeter } from './DeadlineMeter';
import { LanguagePicker } from './LanguagePicker';
import { previewDeadlineLabel } from './deadline';

export const ONBOARDING_STEPS = [
  { n: 1, labelKey: 'onboarding.steps.cost', path: '/preview/onboarding/biaya' },
  { n: 2, labelKey: 'onboarding.steps.nda', path: '/preview/onboarding/nda' },
  { n: 3, labelKey: 'onboarding.steps.tutorial', path: '/preview/onboarding/tutorial' },
  { n: 4, labelKey: 'onboarding.steps.subAccount', path: '/preview/onboarding/sub-akun' },
  { n: 5, labelKey: 'onboarding.steps.process', path: '/preview/onboarding/proses' },
  { n: 6, labelKey: 'onboarding.steps.result', path: '/preview/onboarding/hasil' },
] as const;

interface OnboardingLayoutProps {
  /** 1–6. Steps below this render as done, this one as current. */
  current: number;
  /** The remaining-time meter is meaningless once the work is with AHA. */
  showDeadline?: boolean;
  children: ReactNode;
  /** Tailwind max-width for the content column; screens differ a lot in density. */
  width?: string;
}

export const OnboardingLayout = ({
  current,
  showDeadline = true,
  children,
  width = 'max-w-5xl',
}: OnboardingLayoutProps) => {
  const { t } = useTranslation();
  // Every step restores the choice, not just the first screen: a brand who
  // picks English on the claim page and reloads on step 4 has already told us.
  useOnboardingLanguage();
  const { search } = useLocation();
  const deadline = previewDeadlineLabel(search);

  return (
    <div className="min-h-screen bg-background px-4 py-8 sm:px-8">
      <div className={cn('mx-auto', width)}>
        <nav aria-label={t('onboarding.nav.label')} className="mb-7">
          <ol className="flex flex-wrap items-center gap-2">
            {ONBOARDING_STEPS.map((step) => {
              const done = step.n < current;
              const active = step.n === current;
              return (
                <li key={step.n}>
                  <Link
                    to={step.path}
                    aria-current={active ? 'step' : undefined}
                    className={cn(
                      'flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold transition-colors',
                      active && 'bg-primary text-primary-foreground',
                      done && 'text-primary hover:bg-accent',
                      !active &&
                        !done &&
                        'text-muted-foreground hover:bg-secondary',
                    )}
                  >
                    {done && <Check className="size-3.5" aria-hidden="true" />}
                    <span>
                      {step.n}
                      <span className="hidden sm:inline"> · {t(step.labelKey)}</span>
                    </span>
                  </Link>
                </li>
              );
            })}

            <li className="ms-auto">
              <LanguagePicker />
            </li>
          </ol>
        </nav>

        {showDeadline && (
          <div className="mb-6">
            <DeadlineMeter
              remaining={deadline.workdays}
              hours={deadline.hours}
              date={deadline.date}
            />
          </div>
        )}

        {children}
      </div>
    </div>
  );
};
