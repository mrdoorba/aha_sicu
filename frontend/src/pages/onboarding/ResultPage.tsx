import { useTranslation } from 'react-i18next';
import { ExternalLink, Lightbulb, TrendingUp } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { ReportMetricCard } from '../../components/onboarding/ReportMetricCard';
import { PREVIEW_BRAND } from '../../mocks/onboarding';
import {
  REPORT_CLOSING,
  REPORT_CONCLUSIONS,
  REPORT_GROUPS,
  REPORT_MARKETING_BUDGET,
  REPORT_META,
  REPORT_SCORE,
  splitClosing,
} from '../../mocks/sicuReport';

/**
 * Section numbers match the email: 01, 02, 03.
 *
 * The email read 01, 02, 05 until Oct 2026. Data Intelligence (03) and the
 * Score Breakdown radar (04) were removed from it in #53 and the later headers
 * kept their original numbers — a leftover, not a missing section. Fixed in
 * backend/app/modules/email/template.py and mirrored here.
 */
const SectionHeading = ({ n, children }: { n: string; children: React.ReactNode }) => (
  <h2 className="mb-5 flex items-baseline gap-2.5">
    <span className="text-[11px] font-bold tracking-[0.2em] text-primary-light">{n}</span>
    <span className="text-xl font-extrabold tracking-tight text-foreground">{children}</span>
  </h2>
);

export const ResultPage = () => {
  const { t } = useTranslation();
  const closing = splitClosing(t(REPORT_CLOSING.key, { store_name: PREVIEW_BRAND.name }));

  return (
    <OnboardingLayout current={6} showDeadline={false} width="max-w-4xl">
      {/* The email opens on the AHA band. Logged-out register per DESIGN.md:
          this is the one place the gradient belongs inside the flow, because it
          is reproducing a surface the brand has already received. */}
      <div className="aha-field mb-7 grid place-items-center rounded-2xl px-6 py-11 text-center">
        <img src="/aha-logo.png" alt="" aria-hidden="true" className="mb-3 size-12" />
        <p className="text-2xl font-extrabold tracking-tight text-white">AHA Commerce</p>
        <p className="text-[13px] font-semibold text-white/80">
          {t('onboarding.result.poweredBy')}
        </p>
      </div>

      <header className="mb-8">
        <h1 className="mb-1 text-2xl font-extrabold tracking-tight text-primary">
          {t('email.greeting', { brandName: PREVIEW_BRAND.name })}
        </h1>
        <p className="mb-6 text-sm text-muted-foreground">{REPORT_META.period}</p>

        <p className="mb-4 text-sm leading-relaxed text-foreground">
          {t('onboarding.result.salutation', {
            brand: PREVIEW_BRAND.name,
            pic: REPORT_META.pic,
          })}
        </p>
        <p className="mb-5 text-sm leading-relaxed text-foreground">
          <strong className="text-primary">
            {t('onboarding.result.intro', { brand: PREVIEW_BRAND.name })}
          </strong>
        </p>

        <div className="flex flex-wrap items-center gap-4">
          <a
            href={REPORT_META.storeUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-10 items-center gap-2 rounded-full border border-border px-4 text-[13px] font-bold text-foreground hover:bg-secondary"
          >
            {t('email.visit_store')}
            <ExternalLink className="size-3.5" aria-hidden="true" />
          </a>
          <p className="text-sm text-foreground">
            {t('onboarding.result.category', { category: REPORT_META.category })}
          </p>
        </div>
      </header>

      <section className="mb-10">
        <SectionHeading n="01">{t('email.brand_report')}</SectionHeading>

        <div className="rounded-2xl border border-border bg-card px-8 py-8">
          <p className="mb-5 flex items-baseline gap-1.5">
            <span className="text-6xl font-extrabold leading-none tracking-tight text-deep-navy">
              {REPORT_SCORE.value}
            </span>
            <span className="text-xl font-bold text-muted-foreground">/100</span>
          </p>

          <div className="flex flex-wrap gap-3">
            {/* Two different numbers, exactly as the email prints them: the
                headline score is the brand's, the compatibility score is AHA's
                read on the partnership. Merging them would be a lie in both
                directions. */}
            <span className="inline-flex items-center gap-2.5 rounded-full border border-border px-4 py-2 text-[13px] font-bold text-foreground">
              {t('email.compatibility')}
              <span className="text-base font-extrabold text-primary">
                {REPORT_SCORE.compatibility}
                <span className="text-[11px] text-muted-foreground">/100</span>
              </span>
            </span>
            <span className="inline-flex items-center gap-2 rounded-full border border-border px-4 py-2 text-[13px] font-bold text-primary">
              <TrendingUp className="size-4" aria-hidden="true" />
              {t(REPORT_SCORE.verdictKey)}
            </span>
          </div>
        </div>
      </section>

      <section className="mb-10">
        <SectionHeading n="02">{t('email.detailed_evaluation')}</SectionHeading>

        <div className="flex flex-col gap-9">
          {REPORT_GROUPS.map((group) => (
            <div key={group.titleKey}>
              <p className="mb-3.5 text-sm text-foreground">{t(group.titleKey)}</p>
              <div className="grid items-start gap-4 sm:grid-cols-2">
                {group.metrics.map((metric, i) => (
                  <ReportMetricCard key={`${metric.labelKey}-${i}`} metric={metric} />
                ))}
              </div>

              {group.note && (
                <div className="mt-5">
                  <p className="mb-1 text-[11px] font-bold tracking-wider text-primary">
                    {t(group.note.titleKey).toUpperCase()}
                  </p>
                  <p className="max-w-[80ch] text-[13px] leading-relaxed text-primary">
                    {t(group.note.bodyKey)}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      <section>
        <SectionHeading n="03">{t('email.kesimpulan')}</SectionHeading>

        <div className="rounded-2xl border border-border bg-card p-8">
          <ul className="mb-7 flex flex-col gap-3.5">
            {REPORT_CONCLUSIONS.map((line) => (
              <li key={line.key} className="text-sm leading-relaxed text-foreground">
                {t(line.key, line.vars)}
              </li>
            ))}
          </ul>

          <div className="mb-5 rounded-xl border border-border p-5">
            <p className="mb-1.5 text-[11px] font-bold tracking-wider text-foreground">
              {t(REPORT_MARKETING_BUDGET.labelKey).toUpperCase()}
            </p>
            <p className="flex items-start gap-2 text-[17px] font-extrabold leading-snug text-primary">
              <Lightbulb className="mt-0.5 size-5 shrink-0 text-gold" aria-hidden="true" />
              {/* The email prefixes this line with 💡; the icon beside it is
                  the same idea drawn properly, so the emoji comes off. */}
              {t(REPORT_MARKETING_BUDGET.bodyKey, REPORT_MARKETING_BUDGET.bodyVars).replace(
                /^💡\s*/u,
                '',
              )}
            </p>
          </div>

          <div className="rounded-xl border border-border p-6 text-center">
            <p className="mb-6 text-start text-sm leading-relaxed text-foreground">
              {closing.body}
            </p>
            <a
              href={`https://${closing.link}`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex h-12 items-center rounded-full bg-primary px-7 text-[15px] font-bold text-primary-foreground hover:bg-primary-dark"
            >
              {t(REPORT_CLOSING.ctaKey)}
            </a>
            <p className="mt-6 text-start text-sm leading-relaxed text-foreground">
              {closing.outro}
            </p>
          </div>
        </div>

        <p className="mt-7 text-sm leading-relaxed text-foreground">
          {t(REPORT_CLOSING.signoffKey)}
          <br />
          <span className="font-bold text-primary">AHA Commerce</span>
        </p>
      </section>
    </OnboardingLayout>
  );
};
