import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Check, Copy, ExternalLink, TriangleAlert } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { TutorialVideo } from '../../components/onboarding/TutorialVideo';
import { Button } from '../../components/ui/button';
import {
  PREVIEW_BRAND,
  SHOPEE_SUBACCOUNT_URL,
  SUBACCOUNT_ROLES,
} from '../../mocks/onboarding';
import { cn } from '../../lib/utils';

const CopyField = ({
  label,
  value,
  hint,
  wide,
}: {
  /** Already translated by the caller — this is the printed label. */
  label: string;
  value: string;
  hint?: string;
  /** The sub-account email is long enough to wrap its own button off the row. */
  wide?: boolean;
}) => {
  const { t } = useTranslation();
  return (
    <div className={cn('min-w-0 flex-1', wide ? 'basis-full' : 'basis-60')}>
    <p className="mb-1.5 text-xs font-extrabold tracking-wider text-muted-foreground">{label}</p>
    <div className="flex flex-wrap items-center gap-2">
      <code className="break-all rounded-lg border border-border bg-secondary px-3 py-2.5 font-mono text-[15px] font-bold text-foreground">
        {value}
      </code>
      <Button
          variant="outline"
          size="sm"
          className="h-9.5 gap-1.5"
          aria-label={t('onboarding.tutorial.copyAria', { label })}
        >
          <Copy className="size-3.5" aria-hidden="true" />
          {t('onboarding.tutorial.copy')}
        </Button>
      </div>
      {hint && <p className="mt-2 text-xs leading-relaxed text-muted-foreground">{hint}</p>}
    </div>
  );
};

const Step = ({
  n,
  title,
  children,
}: {
  n: number;
  title: React.ReactNode;
  children?: React.ReactNode;
}) => (
  <li className="flex items-start gap-4">
    <span className="grid size-7.5 shrink-0 place-items-center rounded-full bg-primary text-sm font-extrabold text-primary-foreground">
      {n}
    </span>
    <div className="min-w-0 flex-1">
      <p className="mb-1 text-sm font-bold text-foreground">{title}</p>
      {children}
    </div>
  </li>
);

export const TutorialPage = () => {
  const { t } = useTranslation();

  return (
  <OnboardingLayout current={3} width="max-w-4xl">
    <h1 className="mb-2 text-2xl font-extrabold tracking-tight text-foreground">
      {t('onboarding.tutorial.title')}
    </h1>
    <p className="mb-6 max-w-[72ch] text-sm leading-relaxed text-muted-foreground">
      {t('onboarding.tutorial.intro', { brand: PREVIEW_BRAND.name })}
    </p>

    <div className="mb-6">
      <TutorialVideo />
    </div>

    <ol className="mb-6 flex flex-col gap-7 rounded-2xl border border-border bg-card p-7">
      <Step
        n={1}
        title={
          <>
            {t('onboarding.tutorial.step1')}{' '}
            <a
              href={SHOPEE_SUBACCOUNT_URL}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 font-bold text-primary underline underline-offset-2"
            >
              subaccount.shopee.com/member
              <ExternalLink className="size-3.5" aria-hidden="true" />
            </a>
          </>
        }
      >
        <p className="text-[13px] leading-relaxed text-muted-foreground">
          {t('onboarding.tutorial.step1Note')}
        </p>
      </Step>

      <Step n={2} title={t('onboarding.tutorial.step2')} />

      <Step n={3} title={t('onboarding.tutorial.step3')}>
        <div className="mt-3.5 rounded-xl border-2 border-primary bg-card p-5">
          <div className="flex flex-wrap gap-5">
            <CopyField
              label={t('onboarding.tutorial.memberName')}
              value={PREVIEW_BRAND.subAccountMemberName}
            />
            <CopyField
              label={t('onboarding.tutorial.loginId')}
              value={PREVIEW_BRAND.subAccountLoginId}
            />
            <CopyField
              label={t('onboarding.tutorial.password')}
              value={PREVIEW_BRAND.subAccountPassword}
            />
            <CopyField
              wide
              label={t('onboarding.tutorial.emailAddress')}
              value={PREVIEW_BRAND.subAccountEmail}
              hint={t('onboarding.tutorial.emailHint')}
            />
          </div>

          <div className="mt-5 rounded-xl border border-border bg-secondary p-4">
            <p className="mb-1 text-xs font-extrabold tracking-wider text-muted-foreground">
              {t('onboarding.tutorial.phoneLabel')}
            </p>
            <p className="text-[13px] leading-relaxed text-foreground">
              {t('onboarding.tutorial.phoneBody', {
                strong: t('onboarding.tutorial.phoneBodyStrong'),
              })}
            </p>
          </div>

          <div className="mt-4 flex gap-3 rounded-xl border border-penalti/30 bg-penalti/5 p-4">
            <TriangleAlert className="mt-0.5 size-[18px] shrink-0 text-penalti" aria-hidden="true" />
            <p className="text-[13px] leading-relaxed text-foreground">
              <strong>{t('onboarding.tutorial.exactTitle')}</strong>{' '}
              {t('onboarding.tutorial.exactBody')}
            </p>
          </div>
        </div>
      </Step>

      <Step n={4} title={t('onboarding.tutorial.step4')}>
        <p className="mb-2 text-[13px] leading-relaxed text-muted-foreground">
          {t('onboarding.tutorial.step4Note')}
        </p>
        {/* The permission names below stay in Shopee's own Indonesian: they are
            the strings the brand has to find on Shopee's screen, and a
            translated list would send them hunting for wording Shopee never
            shows. The note explains why they are not in the page's language. */}
        <p className="mb-3.5 text-[13px] leading-relaxed text-muted-foreground">
          {t('onboarding.tutorial.rolesNote')}
        </p>
        <ul lang="id" className="flex flex-col gap-2 rounded-xl border border-border bg-secondary/50 p-5">
          {SUBACCOUNT_ROLES.map((role) => (
            <li key={role.label}>
              <p className="flex items-start gap-2 text-[13px] font-semibold text-foreground">
                <Check className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
                {role.label}
              </p>
              {role.children && (
                <ul className="ms-6 mt-2 flex flex-col gap-2">
                  {role.children.map((child) => (
                    <li
                      key={child}
                      className="flex items-start gap-2 text-[13px] text-secondary-foreground"
                    >
                      <Check className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
                      {child}
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      </Step>
    </ol>

    <Link
      to="/preview/onboarding/sub-akun"
      className="block h-13 rounded-full bg-primary text-center text-[15px] font-bold leading-[52px] text-primary-foreground hover:bg-primary-dark"
    >
      {t('onboarding.tutorial.cta')}
    </Link>

    {/* Marwah's written steps ended with "konfirmasi ke kak Marwah lewat
        WhatsApp". Dropped on her and Alfiano's instruction (14 Oct): the next
        screen already confirms it in-app, so a WhatsApp round trip would be a
        second way to say the same thing — and the slower one. */}
    <p className="mt-4 text-center text-xs leading-relaxed text-muted-foreground">
      {t('onboarding.tutorial.noWhatsapp')}
    </p>
  </OnboardingLayout>
  );
};
