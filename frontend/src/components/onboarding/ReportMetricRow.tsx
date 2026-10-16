import { useTranslation } from 'react-i18next';
import { Check, ExternalLink, X } from 'lucide-react';
import type { ReportMetric } from '../../mocks/sicuReport';
import { cn } from '../../lib/utils';
import { verdictClause } from './verdict';

/**
 * One metric, as a row.
 *
 * It was a card, two to a grid, and that is what made the page unreadable: the
 * cards were different heights, so the grid tore holes in itself, and each one
 * restated its own name and value in the verdict underneath. A row removes
 * both problems — the column can't go ragged, and the verdict only has to
 * carry the part the row hasn't already said.
 *
 * Three shapes, and the difference carries meaning the colour alone does not:
 * a 'good' metric gets a tick, a 'bad' one a cross and a tinted rail, and an
 * 'info' metric gets neither — it is context the brand was given, not a
 * judgement they can pass or fail. Printing a tick beside "Biaya Iklan" would
 * tell them they had got something right that was never scored.
 */
export const ReportMetricRow = ({ metric }: { metric: ReportMetric }) => {
  const { t } = useTranslation();
  const { labelKey, value, benchmark, verdictKey, verdictVars, status, link, titleVar } = metric;

  const metricName = t(labelKey);
  const title = titleVar ? String(verdictVars?.[titleVar] ?? metricName) : metricName;
  const fullVerdict = verdictKey ? t(verdictKey, verdictVars) : null;

  return (
    <div
      className={cn(
        'flex flex-wrap items-start gap-x-6 gap-y-2 border-s-2 py-4 ps-4',
        status === 'bad' ? 'border-s-penalti/40' : 'border-s-transparent',
      )}
    >
      <div className="min-w-0 flex-1 basis-60">
        <div className="flex items-start gap-2">
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
          {/* An info metric gets no icon, but it still has to line up with the
              ones that do — a column of labels at two different left edges
              reads as two different lists. */}
          {status === 'info' && <span className="size-4 shrink-0" aria-hidden="true" />}
          <div className="min-w-0">
            {titleVar && (
              <p className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
                {metricName}
              </p>
            )}
            <p className="text-sm font-bold text-foreground">{title}</p>
          </div>
        </div>

        {fullVerdict && (
          // The email's exact sentence stays on `title`: BD asked the page to
          // match the email, and it still does — the row just doesn't print
          // the half of it that is already two inches to the right.
          <p
            title={fullVerdict}
            className={cn(
              'ms-6 mt-1 whitespace-pre-line text-[13px] leading-relaxed',
              status === 'good' ? 'text-success-ink' : 'text-penalti',
            )}
          >
            {verdictClause(fullVerdict)}
          </p>
        )}

        {link && (
          <a
            href="#"
            className="ms-6 mt-1.5 inline-flex items-center gap-1.5 text-[13px] font-semibold text-muted-foreground hover:text-primary"
          >
            {t('email.view_on_shopee')}
            <ExternalLink className="size-3.5" aria-hidden="true" />
          </a>
        )}
      </div>

      <div className="shrink-0 text-end">
        <p className="text-xl font-extrabold leading-none text-deep-navy tabular-nums">{value}</p>
        {benchmark && (
          <p className="mt-1.5 text-xs text-muted-foreground tabular-nums">
            {t('email.benchmark')} {benchmark}
          </p>
        )}
      </div>
    </div>
  );
};
