import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Check, Clock, Loader2 } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { PREVIEW_BRAND } from '../../mocks/onboarding';
import { cn } from '../../lib/utils';

type StageState = 'done' | 'running' | 'waiting';

interface Stage {
  titleKey: string;
  detailKey: string;
  detailVars?: Record<string, string>;
  state: StageState;
}

const STAGES: Stage[] = [
  {
    titleKey: 'onboarding.wait.stage1',
    detailKey: 'onboarding.wait.stage1Detail',
    detailVars: { time: '09.41' },
    state: 'done',
  },
  {
    titleKey: 'onboarding.wait.stage2',
    detailKey: 'onboarding.wait.stage2Detail',
    state: 'running',
  },
  {
    titleKey: 'onboarding.wait.stage3',
    detailKey: 'onboarding.wait.notStarted',
    state: 'waiting',
  },
  {
    titleKey: 'onboarding.wait.stage4',
    detailKey: 'onboarding.wait.notStarted',
    state: 'waiting',
  },
];

export const WaitingPage = () => {
  const { t } = useTranslation();

  return (
  // The deadline pill is hidden here: the clock is AHA's now, not the brand's.
  <OnboardingLayout current={5} showDeadline={false} width="max-w-2xl">
    <div className="rounded-2xl border border-border bg-card px-6 py-11 text-center sm:px-11">
      <span className="mb-5 inline-grid size-16 place-items-center rounded-full bg-secondary">
        <Loader2 className="size-7 animate-spin text-primary" aria-hidden="true" />
      </span>

      <h1 className="mb-2.5 text-2xl font-extrabold tracking-tight text-foreground">
        {t('onboarding.wait.title')}
      </h1>
      <p className="mx-auto mb-9 max-w-[54ch] text-sm leading-relaxed text-muted-foreground">
        {t('onboarding.wait.body', { email: PREVIEW_BRAND.email })}
      </p>

      <ol className="mb-8 flex flex-col text-left">
        {STAGES.map((stage, i) => {
          const last = i === STAGES.length - 1;
          return (
            <li key={stage.titleKey} className="relative flex items-start gap-4 pb-5.5">
              {!last && (
                <span
                  aria-hidden="true"
                  className={cn(
                    'absolute bottom-0 left-[13px] top-7 w-0.5',
                    stage.state === 'done' ? 'bg-primary' : 'bg-border',
                  )}
                />
              )}
              <span
                className={cn(
                  'relative z-10 grid size-7 shrink-0 place-items-center rounded-full',
                  stage.state === 'done' && 'bg-primary',
                  stage.state === 'running' && 'bg-primary',
                  stage.state === 'waiting' && 'border-2 border-border bg-card',
                )}
              >
                {stage.state === 'done' && (
                  <Check className="size-4 text-primary-foreground" aria-hidden="true" />
                )}
                {stage.state === 'running' && (
                  <span className="size-2.5 animate-pulse rounded-full bg-primary-foreground" />
                )}
              </span>
              <div className="min-w-0">
                <p
                  className={cn(
                    'mb-0.5 text-sm font-bold',
                    stage.state === 'waiting' ? 'text-muted-foreground' : 'text-foreground',
                  )}
                >
                  {t(stage.titleKey)}
                </p>
                <p className="text-[13px] text-muted-foreground">
                  {t(stage.detailKey, stage.detailVars)}
                </p>
              </div>
            </li>
          );
        })}
      </ol>

      <p className="inline-flex items-center gap-2 rounded-xl border border-border bg-secondary px-4 py-2.5 text-[13px] font-bold text-secondary-foreground">
        <Clock className="size-4" aria-hidden="true" />
        {t('onboarding.wait.eta')}
      </p>

      <Link
        to="/preview/onboarding/hasil"
        className="mt-7 block text-sm font-bold text-primary underline underline-offset-4"
      >
        {t('onboarding.wait.jump')}
      </Link>
    </div>

    <p className="mx-auto mt-5 max-w-[60ch] text-center text-xs leading-relaxed text-muted-foreground">
      {t('onboarding.wait.footnote')}
    </p>
  </OnboardingLayout>
  );
};
