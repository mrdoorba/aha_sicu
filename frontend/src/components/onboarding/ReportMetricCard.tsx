import { useTranslation } from 'react-i18next';
import { Check, ExternalLink, X } from 'lucide-react';
import type { ReportMetric } from '../../mocks/sicuReport';
import { cn } from '../../lib/utils';

/**
 * The email's verdict strings start with ✔️ or ❌. The card already draws a
 * tick or a cross of its own, so printing the glyph too would say it twice —
 * and the second one is the ugly one. Only a LEADING glyph is removed: the
 * competition verdicts carry theirs mid-sentence, where it is the sentence.
 */
function stripLeadingVerdictGlyph(text: string): string {
  return text.replace(/^[✔✅❌✗×]️?\s*/u, '');
}

/**
 * One metric card, as the SICU email draws it.
 *
 * Three shapes, and the difference carries meaning the colour alone does not:
 * a 'good' metric gets a tick and a green verdict, a 'bad' one a cross and an
 * amber card, and an 'info' metric gets neither — it is context the brand was
 * given, not a judgement they can pass or fail. Printing a tick beside
 * "Biaya Iklan" would tell them they had got something right that was never
 * scored.
 */
export const ReportMetricCard = ({ metric }: { metric: ReportMetric }) => {
  const { t } = useTranslation();
  const { labelKey, value, benchmark, verdictKey, verdictVars, status, wide, link } = metric;
  const verdict = verdictKey ? stripLeadingVerdictGlyph(t(verdictKey, verdictVars)) : null;

  return (
    <div
      className={cn(
        'min-w-0 rounded-xl border bg-card px-5 py-4',
        // The email lays its cards out two to a row, full width for competition
        // rows. Matching that is the point of the exercise, so the grid is
        // fixed at two rather than packing in a third on a wide screen.
        wide && 'sm:col-span-2',
        status === 'bad' ? 'border-gold/50' : 'border-border',
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <p className="flex min-w-0 items-start gap-2 text-sm font-bold text-primary">
          {status === 'good' && (
            <Check
              className="mt-0.5 size-4 shrink-0 text-success-ink"
              aria-label={t('onboarding.result.good')}
            />
          )}
          {status === 'bad' && (
            <X
              className="mt-0.5 size-4 shrink-0 text-penalti"
              aria-label={t('onboarding.result.bad')}
            />
          )}
          {t(labelKey)}
        </p>
        <p className="shrink-0 text-lg font-extrabold text-primary tabular-nums">{value}</p>
      </div>

      {(benchmark || verdict) && (
        <>
          <div className="my-3 h-px bg-border" aria-hidden="true" />
          {benchmark && (
            <p className="mb-1 text-[13px] text-foreground">
              {t('email.benchmark')}: {benchmark}
            </p>
          )}
          {verdict && (
            <p
              className={cn(
                'text-[13px] font-bold leading-relaxed',
                status === 'good' ? 'text-success-ink' : 'text-penalti',
              )}
            >
              {verdict}
            </p>
          )}
        </>
      )}

      {link && (
        <a
          href="#"
          className="mt-3 inline-flex items-center gap-1.5 text-[13px] font-semibold text-muted-foreground hover:text-primary"
        >
          {t('email.view_on_shopee')}
          <ExternalLink className="size-3.5" aria-hidden="true" />
        </a>
      )}
    </div>
  );
};
