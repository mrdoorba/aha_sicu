import { useState } from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle2, ShieldCheck } from 'lucide-react';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { PREVIEW_BRAND } from '../../mocks/onboarding';
import { formatDeadline, previewDeadlineLabel } from '../../components/onboarding/deadline';
import { useAutoFocusFirstFilter } from '../../hooks/useAutoFocusFirstFilter';

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
  const [code, setCode] = useState(PREVIEW_BRAND.code);
  const autoFocusRef = useAutoFocusFirstFilter<HTMLInputElement>();
  const deadline = previewDeadlineLabel();

  const valid = code.trim().toUpperCase() === PREVIEW_BRAND.code;

  return (
    <div className="aha-field min-h-screen px-4 py-10 sm:px-8">
      <div className="mx-auto w-full max-w-lg">
        {/* Hero copy sits in the dark end of the ramp, where white clears AA. */}
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
            Masukkan kode 12 karakter dari tim BD. Nama brand terisi otomatis.
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
                maxLength={12}
                onChange={(e) => setCode(e.target.value.toUpperCase())}
                className={
                  valid
                    ? 'h-13 border-2 border-primary bg-accent/30 pe-11 font-mono text-lg font-bold tracking-[0.14em] text-primary'
                    : 'h-13 border-2 pe-11 font-mono text-lg font-bold tracking-[0.14em]'
                }
              />
              {valid && (
                <CheckCircle2
                  className="pointer-events-none absolute end-3.5 top-1/2 size-5 -translate-y-1/2 text-primary"
                  aria-hidden="true"
                />
              )}
            </div>
            <p className="mt-2 text-xs font-bold" aria-live="polite">
              {valid ? (
                <span className="text-primary">
                  Voucher valid · berlaku sampai {formatDeadline(deadline.date)}
                </span>
              ) : (
                <span className="text-muted-foreground">
                  Kode tidak dikenal. Di preview ini yang berlaku: {PREVIEW_BRAND.code}
                </span>
              )}
            </p>
          </div>

          {valid && (
            <div className="mb-5 rounded-xl border border-border bg-secondary p-4">
              <p className="mb-2.5 text-[11px] font-extrabold tracking-wider text-primary">
                TERISI OTOMATIS DARI VOUCHER
              </p>
              <dl className="grid grid-cols-2 gap-3">
                <div>
                  <dt className="mb-0.5 text-xs text-muted-foreground">Nama brand</dt>
                  <dd className="text-sm font-bold text-foreground">{PREVIEW_BRAND.name}</dd>
                </div>
                <div>
                  <dt className="mb-0.5 text-xs text-muted-foreground">Marketplace</dt>
                  <dd className="text-sm font-bold text-foreground">🇮🇩 Shopee Indonesia</dd>
                </div>
                <div className="col-span-2">
                  <dt className="mb-0.5 text-xs text-muted-foreground">Toko</dt>
                  <dd className="text-sm font-bold text-foreground">{PREVIEW_BRAND.storeUrl}</dd>
                </div>
              </dl>
            </div>
          )}

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

          <Link
            to="/preview/onboarding/biaya"
            aria-disabled={!valid}
            className={
              valid
                ? 'aha-field-cta block h-12 rounded-xl text-center text-[15px] font-bold leading-[48px] text-white'
                : 'pointer-events-none block h-12 rounded-xl bg-muted text-center text-[15px] font-bold leading-[48px] text-muted-foreground'
            }
          >
            Buat akun SICU
          </Link>
        </div>

        <p className="mt-5 flex items-center justify-center gap-2 text-center text-xs text-white/85">
          <ShieldCheck className="size-4" aria-hidden="true" />
          Pratinjau — tidak ada akun yang benar-benar dibuat.
        </p>
      </div>
    </div>
  );
};
