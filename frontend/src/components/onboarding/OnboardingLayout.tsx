import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { Check, Clock } from 'lucide-react';
import { cn } from '../../lib/utils';
import { formatDeadline, previewDeadlineLabel } from './deadline';

export const ONBOARDING_STEPS = [
  { n: 1, label: 'Biaya', path: '/preview/onboarding/biaya' },
  { n: 2, label: 'NDA', path: '/preview/onboarding/nda' },
  { n: 3, label: 'Tutorial', path: '/preview/onboarding/tutorial' },
  { n: 4, label: 'Sub akun', path: '/preview/onboarding/sub-akun' },
  { n: 5, label: 'Proses', path: '/preview/onboarding/proses' },
  { n: 6, label: 'Hasil', path: '/preview/onboarding/hasil' },
] as const;

interface OnboardingLayoutProps {
  /** 1–6. Steps below this render as done, this one as current. */
  current: number;
  /** The remaining-time pill is meaningless once the work is with AHA. */
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
  const deadline = previewDeadlineLabel();

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-8 sm:px-8">
      <div className={cn('mx-auto', width)}>
        <nav aria-label="Langkah onboarding" className="mb-7">
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
                      active && 'bg-blue-600 text-white',
                      done && 'text-green-700 hover:bg-green-50',
                      !active && !done && 'text-slate-400 hover:bg-slate-100',
                    )}
                  >
                    {done && <Check className="size-3.5" aria-hidden="true" />}
                    <span>
                      {step.n}
                      <span className="hidden sm:inline"> · {step.label}</span>
                    </span>
                  </Link>
                </li>
              );
            })}

            {showDeadline && (
              <li className="ms-auto">
                <span className="flex items-center gap-1.5 rounded-full border border-orange-200 bg-orange-50 px-3 py-1.5 text-xs font-bold text-orange-800">
                  <Clock className="size-3.5" aria-hidden="true" />
                  Sisa {deadline.workdays} hari kerja · sampai {formatDeadline(deadline.date)}
                </span>
              </li>
            )}
          </ol>
        </nav>

        {children}
      </div>
    </div>
  );
};
