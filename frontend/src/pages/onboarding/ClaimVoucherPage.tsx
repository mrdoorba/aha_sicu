import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle2, MessageCircle, ShieldCheck } from 'lucide-react';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { VoucherStatus } from '../../components/onboarding/VoucherStatus';
import {
  AHA_WHATSAPP,
  PREVIEW_TEST_CODES,
  VOUCHER_CODE_LENGTH,
  lookupVoucher,
} from '../../mocks/onboarding';
import { useAutoFocusFirstFilter } from '../../hooks/useAutoFocusFirstFilter';
import { cn } from '../../lib/utils';

/**
 * The public sign-up page — the one logged-out surface in this flow.
 *
 * Per aha-coms DESIGN.md "Two registers", logged-out surfaces follow the Brand
 * Guidelines directly: the AHA Blue Gradient is the page field, not decoration.
 * Every screen after sign-in reverts to the flat authed register.
 *
 * The real brand mark (apps/coms/public/aha-logo.png) does not exist in this
 * repo, and DESIGN.md bans redrawing it as an SVG approximation — so the
 * wordmark stands in until the asset is copied over.
 */
export const ClaimVoucherPage = () => {
  // Starts empty on purpose: the no-voucher state is the one most visitors
  // will actually meet, so it is the one the page has to handle best.
  const [code, setCode] = useState('');
  const autoFocusRef = useAutoFocusFirstFilter<HTMLInputElement>();

  const lookup = useMemo(() => lookupVoucher(code), [code]);
  const valid = lookup.state === 'valid';
  const rejected =
    lookup.state === 'unknown' || lookup.state === 'expired' || lookup.state === 'claimed';

  return (
    <div className="aha-field min-h-screen px-4 py-10 sm:px-8">
      <div className="mx-auto w-full max-w-lg">
        <header className="mb-8 text-center">
          <p className="mb-6 text-xl font-extrabold tracking-tight text-white">AHA Commerce</p>
          <h1 className="mb-3 text-3xl font-extrabold leading-tight tracking-tight text-white">
            Store ICU
          </h1>
          <p className="mx-auto max-w-[38ch] text-sm leading-relaxed text-white/90">
            Cek kesehatan toko Shopee Anda — 8 kategori, 70+ metrik, dikerjakan tim AHA Commerce.
          </p>
        </header>

        <div className="rounded-2xl bg-card p-6 shadow-xl sm:p-8">
          <h2 className="mb-2 text-xl font-extrabold tracking-tight text-foreground">
            Klaim voucher Anda
          </h2>
          <p className="mb-6 text-sm leading-relaxed text-muted-foreground">
            Masukkan kode dari tim BD. Nama brand terisi otomatis.
          </p>

          <div className="mb-5">
            <Label htmlFor="kode" className="mb-1.5 block text-[13px] font-bold">
              Kode voucher
            </Label>
            <div className="relative">
              <Input
                id="kode"
                ref={autoFocusRef}
                value={code}
                maxLength={VOUCHER_CODE_LENGTH}
                placeholder="XXXXXXXXXXXX"
                autoComplete="off"
                spellCheck={false}
                aria-invalid={rejected}
                onChange={(e) => setCode(e.target.value.toUpperCase())}
                className={cn(
                  'h-13 border-2 pe-11 font-mono text-lg font-bold tracking-[0.14em] uppercase',
                  valid && 'border-primary bg-accent/30 text-primary',
                  rejected && 'border-penalti/50',
                )}
              />
              {valid && (
                <CheckCircle2
                  className="pointer-events-none absolute end-3.5 top-1/2 size-5 -translate-y-1/2 text-primary"
                  aria-hidden="true"
                />
              )}
            </div>
            <VoucherStatus lookup={lookup} />
          </div>

          {valid && (
            <>
              <div className="mb-5 rounded-xl border border-border bg-secondary p-4">
                <p className="mb-2.5 text-[11px] font-extrabold tracking-wider text-primary">
                  TERISI OTOMATIS DARI VOUCHER
                </p>
                <dl className="grid grid-cols-2 gap-3">
                  <div>
                    <dt className="mb-0.5 text-xs text-muted-foreground">Nama brand</dt>
                    <dd className="text-sm font-bold text-foreground">{lookup.brand.name}</dd>
                  </div>
                  <div>
                    <dt className="mb-0.5 text-xs text-muted-foreground">Marketplace</dt>
                    <dd className="text-sm font-bold text-foreground">🇮🇩 Shopee Indonesia</dd>
                  </div>
                  <div className="col-span-2">
                    <dt className="mb-0.5 text-xs text-muted-foreground">Toko</dt>
                    <dd className="text-sm font-bold text-foreground">{lookup.brand.storeUrl}</dd>
                  </div>
                </dl>
              </div>

              <div className="mb-4">
                <Label htmlFor="email" className="mb-1.5 block text-[13px] font-bold">
                  Email
                </Label>
                <Input id="email" type="email" placeholder="nama@perusahaan.com" className="h-11" />
              </div>

              <div className="mb-6 grid gap-3.5 sm:grid-cols-2">
                <div>
                  <Label htmlFor="pw" className="mb-1.5 block text-[13px] font-bold">
                    Kata sandi
                  </Label>
                  <Input id="pw" type="password" placeholder="Min. 8 karakter" className="h-11" />
                </div>
                <div>
                  <Label htmlFor="pw2" className="mb-1.5 block text-[13px] font-bold">
                    Ulangi sandi
                  </Label>
                  <Input id="pw2" type="password" placeholder="Ulangi" className="h-11" />
                </div>
              </div>
            </>
          )}

          <Link
            to="/preview/onboarding/biaya"
            aria-disabled={!valid}
            tabIndex={valid ? undefined : -1}
            className={cn(
              'block h-12 rounded-full text-center text-[15px] font-bold leading-[48px]',
              valid
                ? 'aha-field-cta text-white'
                : 'pointer-events-none bg-muted text-muted-foreground',
            )}
          >
            Buat akun SICU
          </Link>

          {/* The dead end needs an exit. A brand cannot issue itself a voucher,
              so without this the page is simply a wall. */}
          <div className="mt-6 border-t border-border pt-5">
            <p className="mb-1 text-[13px] font-bold text-foreground">Belum punya voucher?</p>
            <p className="mb-3.5 text-xs leading-relaxed text-muted-foreground">
              Voucher SICU hanya diterbitkan tim BD AHA Commerce setelah meeting pertama. Kalau
              Anda belum pernah bertemu tim kami, mulai dari sini.
            </p>
            <a
              href={AHA_WHATSAPP}
              target="_blank"
              rel="noreferrer"
              className="inline-flex h-10 items-center gap-2 rounded-full border border-border px-4 text-[13px] font-bold text-foreground hover:bg-secondary"
            >
              <MessageCircle className="size-4" aria-hidden="true" />
              Hubungi tim AHA Commerce
            </a>
          </div>
        </div>

        <div className="mt-5 text-center">
          <p className="flex items-center justify-center gap-2 text-xs text-white/85">
            <ShieldCheck className="size-4" aria-hidden="true" />
            Pratinjau — tidak ada akun yang benar-benar dibuat.
          </p>
          <p className="mt-2 text-xs text-white/70">
            Coba:{' '}
            <button
              type="button"
              onClick={() => setCode(PREVIEW_TEST_CODES.valid)}
              className="font-mono font-bold text-white underline underline-offset-2"
            >
              {PREVIEW_TEST_CODES.valid}
            </button>{' '}
            (valid) ·{' '}
            <button
              type="button"
              onClick={() => setCode(PREVIEW_TEST_CODES.expired)}
              className="font-mono font-bold text-white underline underline-offset-2"
            >
              {PREVIEW_TEST_CODES.expired}
            </button>{' '}
            ·{' '}
            <button
              type="button"
              onClick={() => setCode(PREVIEW_TEST_CODES.claimed)}
              className="font-mono font-bold text-white underline underline-offset-2"
            >
              {PREVIEW_TEST_CODES.claimed}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};
