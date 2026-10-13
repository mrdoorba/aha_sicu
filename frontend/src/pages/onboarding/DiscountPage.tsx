import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Check, Info } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { PREVIEW_BRAND } from '../../mocks/onboarding';

const IDR = new Intl.NumberFormat('id-ID');
const COUNT_MS = 1500;
const HOLD_MS = 450;

function prefersReducedMotion(): boolean {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false;
}

/** Eased count from the full price down to zero — the "gift" beat of the flow. */
function useDiscountCountdown(from: number) {
  // Read once at mount and seed state from it, rather than setting state inside
  // the effect: a viewer who asked for reduced motion gets the final frame on
  // the very first render, with no flash of the full price.
  const [reduced] = useState(prefersReducedMotion);
  const [amount, setAmount] = useState(() => (reduced ? 0 : from));
  const [done, setDone] = useState(() => reduced);
  const raf = useRef<number | undefined>(undefined);

  useEffect(() => {
    if (reduced) return;

    let start: number | null = null;
    const step = (now: number) => {
      if (start === null) start = now;
      const t = Math.min((now - start) / COUNT_MS, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      setAmount(Math.round((from * (1 - eased)) / 1000) * 1000);
      if (t < 1) {
        raf.current = requestAnimationFrame(step);
      } else {
        setAmount(0);
        setDone(true);
      }
    };

    const hold = setTimeout(() => {
      raf.current = requestAnimationFrame(step);
    }, HOLD_MS);

    return () => {
      clearTimeout(hold);
      if (raf.current) cancelAnimationFrame(raf.current);
    };
  }, [from, reduced]);

  return { amount, done };
}

export const DiscountPage = () => {
  const { amount, done } = useDiscountCountdown(PREVIEW_BRAND.priceIdr);

  return (
    <OnboardingLayout current={1} width="max-w-2xl">
      <div className="overflow-hidden rounded-2xl border border-border bg-card">
        <div className="border-b border-dashed border-border px-6 py-10 text-center sm:px-11">
          <p className="mb-1.5 text-[11px] font-bold tracking-wider text-muted-foreground">
            EVALUASI STORE ICU
          </p>
          <h1 className="mb-7 text-2xl font-extrabold tracking-tight text-foreground">
            {PREVIEW_BRAND.name}
          </h1>

          {/* The normal price stays put and stays struck through. Only the big
              figure below it moves — an earlier version animated this line too
              and left it reading "Biaya normal Rp 0", contradicting itself. */}
          <p className="mb-1 text-[13px] text-muted-foreground">Biaya normal</p>
          <p className="mb-6 font-mono text-2xl font-bold text-muted-foreground line-through decoration-2">
            Rp {IDR.format(PREVIEW_BRAND.priceIdr)}
          </p>

          <p
            className="text-6xl font-extrabold leading-none tracking-tight text-primary tabular-nums"
            aria-live="polite"
            aria-atomic="true"
          >
            Rp {IDR.format(amount)}
          </p>

          {done && (
            <div className="mt-5">
              {/* Gold is the reserved win colour and needs dark ink (DESIGN.md). */}
              <span className="inline-flex items-center gap-2 rounded-full bg-gold px-4 py-2 text-[13px] font-extrabold text-deep-navy">
                <Check className="size-4" aria-hidden="true" />
                DISKON 100% DITERAPKAN
              </span>
              <p className="mt-3 text-[15px] font-bold text-foreground">
                Ditanggung penuh oleh AHA Commerce
              </p>
            </div>
          )}
        </div>

        <div className="px-6 pb-9 pt-7 sm:px-11">
          <dl className="mb-6 flex flex-col gap-3">
            <div className="flex justify-between gap-4 text-sm">
              <dt className="text-muted-foreground">Evaluasi SICU — 8 kategori</dt>
              <dd className="font-mono font-semibold text-foreground">
                Rp {IDR.format(PREVIEW_BRAND.priceIdr)}
              </dd>
            </div>
            <div className="flex justify-between gap-4 text-sm">
              <dt className="text-muted-foreground">
                Voucher{' '}
                <code className="rounded-md border border-border bg-secondary px-1.5 py-0.5 font-mono text-xs">
                  {PREVIEW_BRAND.code}
                </code>
              </dt>
              <dd className="font-mono font-bold text-primary">
                − Rp {IDR.format(PREVIEW_BRAND.priceIdr)}
              </dd>
            </div>
            <div className="h-px bg-border" />
            <div className="flex justify-between gap-4 text-[17px] font-extrabold">
              <dt className="text-foreground">Total dibayar</dt>
              <dd className="font-mono text-primary">Rp 0</dd>
            </div>
          </dl>

          <div className="mb-6 flex gap-3 rounded-xl border border-border bg-secondary p-4">
            <Info className="mt-0.5 size-[18px] shrink-0 text-primary" aria-hidden="true" />
            <p className="text-[13px] leading-relaxed text-secondary-foreground">
              Karena total menjadi <strong>Rp 0</strong>, tidak ada transaksi pembayaran sama
              sekali — tidak ada tagihan, tidak ada kartu, tidak ada faktur. Anda langsung lanjut
              ke penandatanganan NDA.
            </p>
          </div>

          <Link
            to="/preview/onboarding/nda"
            className="block h-13 rounded-xl bg-primary text-center text-[15px] font-bold leading-[52px] text-primary-foreground hover:bg-primary-dark"
          >
            Lanjut ke NDA →
          </Link>
        </div>
      </div>

      <p className="mx-auto mt-5 max-w-[68ch] text-center text-xs leading-relaxed text-muted-foreground">
        Layar ini murni presentasi — tidak ada uang bergerak dan tidak ada panggilan ke payment
        gateway. Jika suatu saat voucher bukan 100%, layar inilah yang diganti.
      </p>
    </OnboardingLayout>
  );
};
