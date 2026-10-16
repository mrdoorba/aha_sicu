import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { TriangleAlert } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { PREVIEW_BRAND } from '../../mocks/onboarding';
import { cn } from '../../lib/utils';

/**
 * The two answers are mutually exclusive, so they are radios, not checkboxes:
 * a brand either used the credentials we gave them or used their own, and
 * 'both' is not a state the evaluation team can act on.
 */
type SubAccountChoice = 'given' | 'own';

export const SubAccountPage = () => {
  const { t } = useTranslation();
  // Nothing is preselected. A pre-ticked 'sudah' is the answer most brands
  // would leave untouched, and a wrong yes here costs the team a failed login
  // and a day of back-and-forth.
  const [choice, setChoice] = useState<SubAccountChoice | null>(null);
  const chosen = choice !== null;

  return (
    <OnboardingLayout current={4} width="max-w-3xl">
      <h1 className="mb-2 text-2xl font-extrabold tracking-tight text-foreground">
        {t('onboarding.sub.title')}
      </h1>
      <p className="mb-6 text-sm leading-relaxed text-muted-foreground">
        {t('onboarding.sub.subtitle')}
      </p>

      <fieldset className="mb-6">
        <legend className="sr-only">{t('onboarding.sub.legend')}</legend>

        <div className="flex flex-col gap-3">
          <Label
            className={cn(
              'flex cursor-pointer items-start gap-3.5 rounded-2xl border bg-card p-6 font-normal transition-colors',
              choice === 'given' ? 'border-primary ring-2 ring-ring/30' : 'border-border',
            )}
          >
            <input
              type="radio"
              name="sub-akun"
              value="given"
              checked={choice === 'given'}
              onChange={() => setChoice('given')}
              className="mt-0.5 size-4.5 accent-primary"
            />
            <span className="min-w-0 flex-1">
              <span className="mb-2 block text-[15px] font-bold text-foreground">
                {t('onboarding.sub.givenTitle')}
              </span>
              <span className="block break-all rounded-lg border border-border bg-secondary px-3 py-2.5 font-mono text-[13px] text-secondary-foreground">
                {PREVIEW_BRAND.subAccountEmail} · {PREVIEW_BRAND.subAccountPassword}
              </span>
            </span>
          </Label>

          <Label
            className={cn(
              'flex cursor-pointer items-start gap-3.5 rounded-2xl border bg-card p-6 font-normal transition-colors',
              choice === 'own' ? 'border-primary ring-2 ring-ring/30' : 'border-border',
            )}
          >
            <input
              type="radio"
              name="sub-akun"
              value="own"
              checked={choice === 'own'}
              onChange={() => setChoice('own')}
              className="mt-0.5 size-4.5 accent-primary"
            />
            <span className="min-w-0 flex-1">
              <span className="block text-[15px] font-bold text-foreground">
                {t('onboarding.sub.ownTitle')}
              </span>
              <span className="mt-1 block text-[13px] leading-relaxed text-muted-foreground">
                {t('onboarding.sub.ownSubtitle')}
              </span>

              {choice === 'own' && (
                <span className="mt-5 block animate-in fade-in slide-in-from-top-1 duration-200">
                  <span className="mb-5 flex gap-3 rounded-xl border border-gold/40 bg-gold/10 p-3.5">
                    <TriangleAlert
                      className="mt-0.5 size-4.5 shrink-0 text-foreground"
                      aria-hidden="true"
                    />
                    <span className="text-[13px] leading-relaxed text-foreground">
                      {t('onboarding.sub.ownWarning')}
                    </span>
                  </span>

                  <span className="mb-4 block">
                    <Label htmlFor="own-email" className="mb-1.5 block text-[13px] font-bold">
                      {t('onboarding.sub.ownEmail')}
                    </Label>
                    <Input
                      id="own-email"
                      type="email"
                      placeholder={t('onboarding.sub.ownEmailPlaceholder')}
                      className="h-11"
                    />
                  </span>
                  <span className="block">
                    <Label htmlFor="own-pw" className="mb-1.5 block text-[13px] font-bold">
                      {t('onboarding.sub.ownPassword')}
                    </Label>
                    <Input
                      id="own-pw"
                      type="password"
                      placeholder={t('onboarding.sub.ownPasswordPlaceholder')}
                      className="h-11"
                    />
                  </span>
                  <span className="mt-3 block text-xs leading-relaxed text-muted-foreground">
                    {t('onboarding.sub.encrypted')}
                  </span>
                </span>
              )}
            </span>
          </Label>
        </div>
      </fieldset>

      <Link
        to="/preview/onboarding/proses"
        aria-disabled={!chosen}
        tabIndex={chosen ? undefined : -1}
        className={cn(
          'block h-13 rounded-full text-center text-[15px] font-bold leading-[52px]',
          chosen
            ? 'bg-primary text-primary-foreground hover:bg-primary-dark'
            : 'pointer-events-none bg-muted text-muted-foreground',
        )}
      >
        {t('onboarding.sub.cta')}
      </Link>

      <p className="mt-4 text-center text-xs leading-relaxed text-muted-foreground">
        {chosen ? t('onboarding.sub.hintChosen') : t('onboarding.sub.hintPick')}
      </p>
    </OnboardingLayout>
  );
};
