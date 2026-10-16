import { useTranslation } from 'react-i18next';
import { CheckCircle2, CircleAlert, Clock, Info } from 'lucide-react';
import type { VoucherLookup } from '../../mocks/onboarding';
import { getIntlLocale } from '../../lib/languages';
import { formatDeadline } from '../../lib/workdays';

/**
 * The line under the voucher field.
 *
 * Every non-valid state says what to DO next, not just what went wrong — a
 * brand that reaches a dead end here has no other way into the product, so
 * "kode tidak ditemukan" on its own would simply lose them.
 */
export const VoucherStatus = ({ lookup }: { lookup: VoucherLookup }) => {
  const { t, i18n } = useTranslation();
  const locale = getIntlLocale(i18n.language);

  if (lookup.state === 'idle') {
    return (
      <p className="mt-2 flex items-start gap-1.5 text-xs text-muted-foreground">
        <Info className="mt-px size-3.5 shrink-0" aria-hidden="true" />
        {t('onboarding.voucher.hint')}
      </p>
    );
  }

  if (lookup.state === 'typing') {
    return (
      <p className="mt-2 text-xs text-muted-foreground" aria-live="polite">
        {/* `remaining`, not `count`: a `count` option switches i18next into
            plural resolution, which is not what this sentence wants. */}
        {t('onboarding.voucher.typing', { remaining: lookup.remaining })}
      </p>
    );
  }

  if (lookup.state === 'valid') {
    return (
      <p
        className="mt-2 flex items-start gap-1.5 text-xs font-bold text-primary"
        aria-live="polite"
      >
        <CheckCircle2 className="mt-px size-3.5 shrink-0" aria-hidden="true" />
        {t('onboarding.voucher.valid', {
          date: formatDeadline(lookup.expiresAt, locale),
        })}
      </p>
    );
  }

  if (lookup.state === 'expired') {
    return (
      <div
        className="mt-2 flex gap-2 rounded-lg border border-gold/40 bg-gold/10 p-3"
        aria-live="polite"
      >
        <Clock className="mt-px size-4 shrink-0 text-foreground" aria-hidden="true" />
        <p className="text-xs leading-relaxed text-foreground">
          <strong>{t('onboarding.voucher.expiredTitle')}</strong>{' '}
          {t('onboarding.voucher.expiredBody', {
            date: formatDeadline(lookup.expiredOn, locale),
          })}
        </p>
      </div>
    );
  }

  if (lookup.state === 'claimed') {
    return (
      <div
        className="mt-2 flex gap-2 rounded-lg border border-border bg-secondary p-3"
        aria-live="polite"
      >
        <Info className="mt-px size-4 shrink-0 text-primary" aria-hidden="true" />
        <p className="text-xs leading-relaxed text-secondary-foreground">
          <strong>{t('onboarding.voucher.claimedTitle')}</strong>{' '}
          {t('onboarding.voucher.claimedBody', {
            date: formatDeadline(lookup.claimedOn, locale),
          })}{' '}
          <a href="#" className="font-bold text-primary underline underline-offset-2">
            {t('onboarding.voucher.claimedLink')}
          </a>{' '}
          {t('onboarding.voucher.claimedTail')}
        </p>
      </div>
    );
  }

  return (
    <div
      className="mt-2 flex gap-2 rounded-lg border border-penalti/30 bg-penalti/5 p-3"
      aria-live="polite"
    >
      <CircleAlert className="mt-px size-4 shrink-0 text-penalti" aria-hidden="true" />
      <p className="text-xs leading-relaxed text-foreground">
        <strong>{t('onboarding.voucher.unknownTitle')}</strong>{' '}
        {t('onboarding.voucher.unknownBody')}
      </p>
    </div>
  );
};
