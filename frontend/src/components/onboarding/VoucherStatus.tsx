import { CheckCircle2, CircleAlert, Clock, Info } from 'lucide-react';
import type { VoucherLookup } from '../../mocks/onboarding';
import { formatDeadline } from '../../lib/workdays';

/**
 * The line under the voucher field.
 *
 * Every non-valid state says what to DO next, not just what went wrong — a
 * brand that reaches a dead end here has no other way into the product, so
 * "kode tidak ditemukan" on its own would simply lose them.
 */
export const VoucherStatus = ({ lookup }: { lookup: VoucherLookup }) => {
  if (lookup.state === 'idle') {
    return (
      <p className="mt-2 flex items-start gap-1.5 text-xs text-muted-foreground">
        <Info className="mt-px size-3.5 shrink-0" aria-hidden="true" />
        12 karakter, dikirim tim BD lewat WhatsApp.
      </p>
    );
  }

  if (lookup.state === 'typing') {
    return (
      <p className="mt-2 text-xs text-muted-foreground" aria-live="polite">
        Kurang {lookup.remaining} karakter lagi.
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
        Voucher valid · klaim sebelum {formatDeadline(lookup.expiresAt)}
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
          <strong>Voucher ini sudah kedaluwarsa</strong> pada{' '}
          {formatDeadline(lookup.expiredOn)}. Hubungi tim BD Anda — mereka bisa menerbitkan kode
          baru tanpa biaya.
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
          <strong>Voucher ini sudah dipakai</strong> pada {formatDeadline(lookup.claimedOn)}. Kalau
          itu Anda, silakan{' '}
          <a href="#" className="font-bold text-primary underline underline-offset-2">
            masuk ke akun Anda
          </a>{' '}
          — tidak perlu voucher lagi.
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
        <strong>Kode tidak dikenal.</strong> Periksa lagi penulisannya, atau minta tim BD Anda
        mengirim ulang kodenya.
      </p>
    </div>
  );
};
