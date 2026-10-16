import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { Check, ExternalLink, Info, Lightbulb, TrendingUp, X } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { ReportMetricRow } from '../../components/onboarding/ReportMetricRow';
import { PREVIEW_BRAND } from '../../mocks/onboarding';
import {
  REPORT_CLOSING,
  REPORT_CONCLUSIONS,
  REPORT_GROUPS,
  REPORT_MARKETING_BUDGET,
  REPORT_META,
  REPORT_SCORE,
  splitClosing,
  type ReportGroup,
} from '../../mocks/sicuReport';

/**
 * Section numbers match the email: 01, 02, 03.
 *
 * The email read 01, 02, 05 until Oct 2026. Data Intelligence (03) and the
 * Score Breakdown radar (04) were removed from it in #53 and the later headers
 * kept their original numbers — a leftover, not a missing section. Fixed in
 * backend/app/modules/email/template.py and mirrored here.
 */
const SectionHeading = ({ n, children }: { n: string; children: ReactNode }) => (
  <h2 className="mb-5 flex items-baseline gap-3">
    <span className="text-[11px] font-bold tracking-[0.2em] text-primary-light">{n}</span>
    <span className="text-xl font-extrabold tracking-tight text-foreground">{children}</span>
  </h2>
);

/** A labelled 0–100 bar. The number alone doesn't say whether 42 is bad. */
const ScoreBar = ({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: 'navy' | 'primary';
}) => (
  <div className="min-w-0 flex-1 basis-56">
    <p className="mb-1.5 text-xs font-bold uppercase tracking-wider text-muted-foreground">
      {label}
    </p>
    <p className="mb-2.5 flex items-baseline gap-1">
      <span className="text-5xl font-extrabold leading-none tracking-tight text-deep-navy tabular-nums">
        {value}
      </span>
      <span className="text-base font-bold text-muted-foreground">/100</span>
    </p>
    <div
      className="h-1.5 overflow-hidden rounded-full bg-secondary"
      role="img"
      aria-label={`${label}: ${value}/100`}
    >
      <div
        className={tone === 'navy' ? 'h-full bg-deep-navy' : 'h-full bg-primary'}
        style={{ width: `${value}%` }}
      />
    </div>
  </div>
);

/** How many of a group's metrics passed. An 'info' metric is in neither tally. */
const GroupTally = ({ group }: { group: ReportGroup }) => {
  const { t } = useTranslation();
  const good = group.metrics.filter((m) => m.status === 'good').length;
  const bad = group.metrics.filter((m) => m.status === 'bad').length;

  return (
    <div className="flex shrink-0 items-center gap-2">
      {good > 0 && (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-success/10 px-3 py-1 text-xs font-bold text-success-ink">
          <Check className="size-3.5" aria-hidden="true" />
          {good} {t('email.check_count')}
        </span>
      )}
      {bad > 0 && (
        <span className="inline-flex items-center gap-1.5 rounded-full bg-penalti/10 px-3 py-1 text-xs font-bold text-penalti">
          <X className="size-3.5" aria-hidden="true" />
          {bad} {t('email.cross_count')}
        </span>
      )}
    </div>
  );
};

export const ResultPage = () => {
  const { t } = useTranslation();
  const closing = splitClosing(t(REPORT_CLOSING.key, { store_name: PREVIEW_BRAND.name }));

  return (
    <OnboardingLayout current={6} showDeadline={false} width="max-w-3xl">
      {/* The email opens on the AHA band. Logged-out register per DESIGN.md:
          this is the one place the gradient belongs inside the flow, because it
          is reproducing a surface the brand has already received. */}
      <div className="aha-field mb-8 grid place-items-center rounded-2xl px-6 py-10 text-center">
        <img src="/aha-logo.png" alt="" aria-hidden="true" className="mb-3 size-11" />
        <p className="text-xl font-extrabold tracking-tight text-white">AHA Commerce</p>
        <p className="text-xs font-semibold text-white/75">{t('onboarding.result.poweredBy')}</p>
      </div>

      <header className="mb-10">
        <p className="mb-1 text-xs font-bold uppercase tracking-wider text-muted-foreground">
          {REPORT_META.period}
        </p>
        <h1 className="mb-5 text-3xl font-extrabold tracking-tight text-primary">
          {t('email.greeting', { brandName: PREVIEW_BRAND.name })}
        </h1>

        <p className="mb-2 text-sm leading-relaxed text-foreground">
          {t('onboarding.result.salutation', {
            brand: PREVIEW_BRAND.name,
            pic: REPORT_META.pic,
          })}
        </p>
        <p className="mb-5 text-sm leading-relaxed text-foreground">
          {t('onboarding.result.intro', { brand: PREVIEW_BRAND.name })}
        </p>

        <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
          <a
            href={REPORT_META.storeUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-9 items-center gap-2 rounded-full border border-border px-4 text-[13px] font-bold text-foreground hover:bg-secondary"
          >
            {t('email.visit_store')}
            <ExternalLink className="size-3.5" aria-hidden="true" />
          </a>
          <p className="text-[13px] text-muted-foreground">
            {t('onboarding.result.category', { category: REPORT_META.category })}
          </p>
        </div>
      </header>

      <section className="mb-12">
        <SectionHeading n="01">{t('email.brand_report')}</SectionHeading>

        <div className="rounded-2xl border border-border bg-card p-7">
          {/* Two different numbers, exactly as the email prints them: the
              headline score is the brand's, the compatibility score is AHA's
              read on the partnership. Merging them would be a lie in both
              directions — so they get equal weight and separate bars. */}
          <div className="flex flex-wrap gap-8">
            <ScoreBar label={t('email.score')} value={REPORT_SCORE.value} tone="navy" />
            <ScoreBar
              label={t('email.compatibility')}
              value={REPORT_SCORE.compatibility}
              tone="primary"
            />
          </div>

          <p className="mt-7 border-t border-border pt-5">
            <span className="inline-flex items-center gap-2 rounded-full bg-accent/40 px-4 py-2 text-sm font-extrabold text-primary">
              <TrendingUp className="size-4" aria-hidden="true" />
              {t(REPORT_SCORE.verdictKey)}
            </span>
          </p>
        </div>
      </section>

      <section className="mb-12">
        <SectionHeading n="02">{t('email.detailed_evaluation')}</SectionHeading>

        <div className="flex flex-col gap-4">
          {REPORT_GROUPS.map((group) => (
            <div key={group.titleKey} className="rounded-2xl border border-border bg-card">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-6 py-4">
                <h3 className="text-[15px] font-extrabold tracking-tight text-foreground">
                  {t(group.titleKey)}
                </h3>
                <GroupTally group={group} />
              </div>

              <div className="divide-y divide-border px-4 py-1">
                {group.metrics.map((metric, i) => (
                  <ReportMetricRow key={`${metric.labelKey}-${i}`} metric={metric} />
                ))}
              </div>

              {group.note && (
                <div className="flex gap-3 border-t border-border bg-secondary px-6 py-4">
                  <Info className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
                  <div className="min-w-0">
                    <p className="mb-0.5 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
                      {t(group.note.titleKey)}
                    </p>
                    <p className="text-[13px] leading-relaxed text-secondary-foreground">
                      {t(group.note.bodyKey)}
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      <section>
        <SectionHeading n="03">{t('email.kesimpulan')}</SectionHeading>

        <ul className="mb-4 flex flex-col gap-px overflow-hidden rounded-2xl border border-border bg-border">
          {REPORT_CONCLUSIONS.map((line) => (
            <li
              key={line.key}
              className="flex items-start gap-3 bg-card px-6 py-4 text-sm leading-relaxed text-foreground"
            >
              <span
                aria-hidden="true"
                className="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary"
              />
              {t(line.key, line.vars)}
            </li>
          ))}
        </ul>

        <div className="mb-4 flex gap-3.5 rounded-2xl border border-gold/50 bg-gold/10 px-6 py-5">
          <Lightbulb className="mt-0.5 size-5 shrink-0 text-deep-navy" aria-hidden="true" />
          <div className="min-w-0">
            <p className="mb-0.5 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
              {t(REPORT_MARKETING_BUDGET.labelKey)}
            </p>
            {/* The email prefixes this line with 💡; the icon beside it is the
                same idea drawn properly, so the emoji comes off. */}
            <p className="text-[15px] font-extrabold leading-snug text-deep-navy">
              {t(REPORT_MARKETING_BUDGET.bodyKey, REPORT_MARKETING_BUDGET.bodyVars).replace(
                /^💡\s*/u,
                '',
              )}
            </p>
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-card px-7 py-7">
          <p className="mb-6 text-sm leading-relaxed text-foreground">{closing.body}</p>
          <a
            href={`https://${closing.link}`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-12 items-center rounded-full bg-primary px-7 text-[15px] font-bold text-primary-foreground hover:bg-primary-dark"
          >
            {t(REPORT_CLOSING.ctaKey)}
          </a>
          <p className="mt-6 text-sm leading-relaxed text-foreground">{closing.outro}</p>
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
