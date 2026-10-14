import { Link } from 'react-router-dom';
import { Check, Clock, Loader2 } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { PREVIEW_BRAND } from '../../mocks/onboarding';
import { cn } from '../../lib/utils';

type StageState = 'done' | 'running' | 'waiting';

const STAGES: { title: string; detail: string; state: StageState }[] = [
  { title: 'Sub akun diterima', detail: 'Hari ini 09:41', state: 'done' },
  {
    title: 'Menarik data toko dari Seller Centre',
    detail: 'Sedang berjalan · pesanan, produk, iklan, stok',
    state: 'running',
  },
  { title: 'Evaluasi 8 kategori SICU', detail: 'Belum mulai', state: 'waiting' },
  { title: 'Laporan & rekomendasi disiapkan', detail: 'Belum mulai', state: 'waiting' },
];

export const WaitingPage = () => (
  // The deadline pill is hidden here: the clock is AHA's now, not the brand's.
  <OnboardingLayout current={5} showDeadline={false} width="max-w-2xl">
    <div className="rounded-2xl border border-border bg-card px-6 py-11 text-center sm:px-11">
      <span className="mb-5 inline-grid size-16 place-items-center rounded-full bg-secondary">
        <Loader2 className="size-7 animate-spin text-primary" aria-hidden="true" />
      </span>

      <h1 className="mb-2.5 text-2xl font-extrabold tracking-tight text-foreground">
        Tim AHA sedang mengerjakan evaluasi Anda
      </h1>
      <p className="mx-auto mb-9 max-w-[54ch] text-sm leading-relaxed text-muted-foreground">
        Tidak ada yang perlu Anda lakukan. Kami kirim email ke{' '}
        <strong className="text-foreground">{PREVIEW_BRAND.email}</strong> begitu hasilnya siap.
      </p>

      <ol className="mb-8 flex flex-col text-left">
        {STAGES.map((stage, i) => {
          const last = i === STAGES.length - 1;
          return (
            <li key={stage.title} className="relative flex items-start gap-4 pb-5.5">
              {!last && (
                <span
                  aria-hidden="true"
                  className={cn(
                    'absolute bottom-0 left-[13px] top-7 w-0.5',
                    stage.state === 'done' ? 'bg-primary' : 'bg-border',
                  )}
                />
              )}
              <span
                className={cn(
                  'relative z-10 grid size-7 shrink-0 place-items-center rounded-full',
                  stage.state === 'done' && 'bg-primary',
                  stage.state === 'running' && 'bg-primary',
                  stage.state === 'waiting' && 'border-2 border-border bg-card',
                )}
              >
                {stage.state === 'done' && (
                  <Check className="size-4 text-primary-foreground" aria-hidden="true" />
                )}
                {stage.state === 'running' && (
                  <span className="size-2.5 animate-pulse rounded-full bg-primary-foreground" />
                )}
              </span>
              <div className="min-w-0">
                <p
                  className={cn(
                    'mb-0.5 text-sm font-bold',
                    stage.state === 'waiting' ? 'text-muted-foreground' : 'text-foreground',
                  )}
                >
                  {stage.title}
                </p>
                <p className="text-[13px] text-muted-foreground">{stage.detail}</p>
              </div>
            </li>
          );
        })}
      </ol>

      <p className="inline-flex items-center gap-2 rounded-xl border border-border bg-secondary px-4 py-2.5 text-[13px] font-bold text-secondary-foreground">
        <Clock className="size-4" aria-hidden="true" />
        Estimasi selesai: 1–2 hari kerja
      </p>

      <Link
        to="/preview/onboarding/hasil"
        className="mt-7 block text-sm font-bold text-primary underline underline-offset-4"
      >
        [pratinjau] lompat ke hasil →
      </Link>
    </div>

    <p className="mx-auto mt-5 max-w-[60ch] text-center text-xs leading-relaxed text-muted-foreground">
      Halaman ini satu-satunya yang brand lihat sampai verdict keluar. Brand tidak bisa
      mempercepatnya, dan tidak melihat apa pun milik brand lain.
    </p>
  </OnboardingLayout>
);
