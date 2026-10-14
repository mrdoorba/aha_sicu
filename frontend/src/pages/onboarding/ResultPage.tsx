import { Download } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { HealthRadar } from '../../components/onboarding/HealthRadar';
import { Button } from '../../components/ui/button';
import { PREVIEW_AXES, PREVIEW_BRAND, PREVIEW_RECOMMENDATIONS } from '../../mocks/onboarding';
import { cn } from '../../lib/utils';

/** Health bands. Deliberately three, so "cukup" is visibly not "baik". */
function band(value: number): { bar: string; text: string } {
  if (value >= 80) return { bar: 'bg-primary', text: 'text-primary' };
  if (value >= 65) return { bar: 'bg-gold', text: 'text-foreground' };
  return { bar: 'bg-penalti', text: 'text-penalti' };
}

export const ResultPage = () => {
  const overall = Math.round(
    PREVIEW_AXES.reduce((sum, axis) => sum + axis.value, 0) / PREVIEW_AXES.length,
  );
  const sorted = [...PREVIEW_AXES].sort((a, b) => b.value - a.value);

  return (
    <OnboardingLayout current={6} showDeadline={false} width="max-w-5xl">
      <div className="mb-5 rounded-2xl border border-border bg-card p-8">
        <div className="flex flex-wrap items-center gap-8">
          <div className="min-w-0 flex-1 basis-72">
            <p className="mb-1.5 text-[11px] font-extrabold tracking-wider text-muted-foreground">
              HASIL STORE ICU · PERIODE SEP 2026
            </p>
            <h1 className="mb-4 text-2xl font-extrabold tracking-tight text-foreground">
              {PREVIEW_BRAND.name}
            </h1>
            <div className="mb-2 flex items-baseline gap-3">
              <span className="text-6xl font-extrabold leading-none tracking-tight text-primary">
                {overall}
              </span>
              <span className="text-xl font-bold text-muted-foreground">/ 100</span>
            </div>
            <p className="mb-4 text-sm font-bold text-foreground">Skor Kesehatan Toko</p>
            <span className="inline-flex items-center gap-2 rounded-full bg-gold px-4 py-2 text-[13px] font-bold text-deep-navy">
              Cukup sehat — 3 area perlu perbaikan
            </span>
          </div>

          <div className="min-w-0 flex-1 basis-80">
            <HealthRadar axes={PREVIEW_AXES} />
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-start gap-5">
        <section className="min-w-0 flex-1 basis-96 rounded-2xl border border-border bg-card p-7">
          <h2 className="mb-5 text-base font-extrabold text-foreground">Rincian per kategori</h2>
          <dl className="flex flex-col gap-4">
            {sorted.map((axis) => {
              const tone = band(axis.value);
              return (
                <div key={axis.label}>
                  <div className="mb-1.5 flex justify-between gap-3">
                    <dt className="text-[13px] font-semibold text-foreground">{axis.label}</dt>
                    <dd className={cn('text-[13px] font-extrabold', tone.text)}>{axis.value}</dd>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-secondary">
                    <div className={cn('h-full', tone.bar)} style={{ width: `${axis.value}%` }} />
                  </div>
                </div>
              );
            })}
          </dl>
        </section>

        <section className="flex min-w-0 flex-1 basis-80 flex-col gap-4">
          <div className="rounded-2xl border border-border bg-card p-7">
            <h2 className="mb-4 text-base font-extrabold text-foreground">
              Yang paling cepat memberi hasil
            </h2>
            <ol className="flex flex-col gap-4">
              {PREVIEW_RECOMMENDATIONS.map((rec, i) => (
                <li key={rec.title} className="flex items-start gap-3">
                  <span
                    className={cn(
                      'grid size-6 shrink-0 place-items-center rounded-full text-xs font-extrabold',
                      rec.severity === 'high'
                        ? 'bg-penalti/15 text-penalti'
                        : 'bg-gold/25 text-foreground',
                    )}
                  >
                    {i + 1}
                  </span>
                  <div className="min-w-0">
                    <p className="mb-0.5 text-sm font-bold text-foreground">{rec.title}</p>
                    <p className="text-[13px] leading-relaxed text-muted-foreground">{rec.body}</p>
                  </div>
                </li>
              ))}
            </ol>
          </div>

          <Button className="h-13 gap-2 text-[15px] font-bold">
            <Download className="size-4.5" aria-hidden="true" />
            Unduh laporan lengkap (PDF)
          </Button>
        </section>
      </div>

      {/* The internal 100-point score is not the brand's business: explaining
          that AHA's own scoring awards points when a metric FAILS invites a
          question we don't want to answer on a results page. */}
      <p className="mx-auto mt-5 max-w-[72ch] text-center text-xs leading-relaxed text-muted-foreground">
        Angka di halaman ini adalah <strong>kesehatan toko</strong> — makin tinggi makin baik.
      </p>
    </OnboardingLayout>
  );
};
