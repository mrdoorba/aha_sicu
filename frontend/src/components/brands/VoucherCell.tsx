import { Check, Copy, MessageCircle } from 'lucide-react';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import type { PreviewVoucher } from '../../mocks/onboarding';
import { formatDeadline, workdaysBetween } from '../../lib/workdays';

/**
 * The Voucher column on the Brands table.
 *
 * Expiry is derived here, from `expiresAt` against the clock — never read from
 * a stored "expired" flag. A sweeper that fails to run must not leave a dead
 * voucher looking live.
 */
export const VoucherCell = ({ voucher }: { voucher: PreviewVoucher }) => {
  const now = new Date();
  const expired =
    voucher.status === 'expired' || (voucher.expiresAt !== null && voucher.expiresAt <= now);

  if (voucher.status === 'none') {
    return <span className="text-sm text-muted-foreground">— Butuh 1st meeting</span>;
  }

  if (voucher.status === 'claimed') {
    return (
      <div className="flex flex-col gap-1">
        <span className="flex items-center gap-1.5 text-[13px] font-bold text-primary">
          <Check className="size-4" aria-hidden="true" />
          Diklaim
        </span>
        <span className="text-xs text-muted-foreground">
          {voucher.claimedAt ? formatDeadline(voucher.claimedAt) : '—'}
          {voucher.step !== null && ` · sedang di langkah ${voucher.step}`}
        </span>
      </div>
    );
  }

  if (expired) {
    return (
      <div className="flex flex-wrap items-center gap-2">
        <Badge className="bg-penalti/15 text-penalti hover:bg-penalti/15">
          Kedaluwarsa {voucher.expiresAt ? formatDeadline(voucher.expiresAt) : ''}
        </Badge>
        <Button variant="outline" size="sm">
          Buat ulang
        </Button>
      </div>
    );
  }

  if (voucher.status === 'pending') {
    return (
      <div className="flex flex-wrap items-center gap-2">
        {/* Gold = the action that moves the deal forward. Dark ink, per DESIGN.md. */}
        <Badge className="bg-gold text-deep-navy hover:bg-gold">Belum aktif</Badge>
        <Button size="sm" className="gap-1.5 bg-gold text-deep-navy hover:bg-gold/85">
          <Check className="size-3.5" aria-hidden="true" />
          Aktifkan
        </Button>
      </div>
    );
  }

  const daysLeft = voucher.expiresAt ? workdaysBetween(now, voucher.expiresAt) : 0;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <code className="rounded-md border border-border bg-secondary px-2 py-1 font-mono text-[13px] font-semibold tracking-wider text-foreground">
          {voucher.code}
        </code>
        <Button
          variant="outline"
          size="sm"
          className="h-7.5 gap-1.5 px-2.5"
          aria-label={`Salin kode voucher ${voucher.brandName}`}
        >
          <Copy className="size-3.5" aria-hidden="true" />
          Salin
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="h-7.5 gap-1.5 px-2.5"
          aria-label={`Kirim voucher ${voucher.brandName} ke WhatsApp`}
          asChild
        >
          <a
            href={`https://wa.me/?text=${encodeURIComponent(
              `Halo ${voucher.brandName}, ini kode voucher SICU gratis Anda: ${voucher.code}. ` +
                `Klaim di https://sicu.ahabot.ai sebelum ${
                  voucher.expiresAt ? formatDeadline(voucher.expiresAt) : ''
                }.`,
            )}`}
            target="_blank"
            rel="noreferrer"
          >
            <MessageCircle className="size-3.5" aria-hidden="true" />
            WA
          </a>
        </Button>
      </div>
      <span className="text-xs font-semibold text-muted-foreground">
        Berakhir {voucher.expiresAt ? formatDeadline(voucher.expiresAt) : '—'} · {daysLeft} hari
        kerja lagi
      </span>
    </div>
  );
};
