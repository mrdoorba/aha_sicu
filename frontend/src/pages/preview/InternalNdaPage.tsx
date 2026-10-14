import { useRef, useState } from 'react';
import { Check, FileUp, PenLine, Printer } from 'lucide-react';
import { NdaSignatures } from '../../components/onboarding/NdaSignatures';
import {
  AHA_SIGNER,
  type NdaRecord,
  type NdaRoute,
  canCountersign,
  countersign,
  previewNdaQueue,
} from '../../mocks/nda';
import { cn } from '../../lib/utils';

const STATUS_LABEL: Record<NdaRecord['status'], string> = {
  awaiting_brand: 'Menunggu brand',
  awaiting_aha: 'Perlu tanda tangan Anda',
  executed: 'Selesai — kedua pihak',
};

const STATUS_TONE: Record<NdaRecord['status'], string> = {
  awaiting_brand: 'bg-secondary text-muted-foreground',
  awaiting_aha: 'bg-gold text-deep-navy',
  executed: 'bg-accent text-primary',
};

const ROUTE_LABEL: Record<NdaRoute, string> = {
  digital: 'Digital',
  paper: 'Kertas',
};

const RELATIVE = new Intl.RelativeTimeFormat('id-ID', { numeric: 'auto' });

function hoursSince(d: Date): string {
  const hours = Math.round((Date.now() - d.getTime()) / 3_600_000);
  return hours < 24 ? RELATIVE.format(-hours, 'hour') : RELATIVE.format(-Math.round(hours / 24), 'day');
}

/** AHA's side of the paper route: print the brand-signed copy, sign, upload it back. */
const AhaPaperRoute = ({ onUploaded }: { onUploaded: () => void }) => {
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <div>
      <ol className="mb-5 flex flex-col gap-2.5">
        {[
          'Cetak salinan yang sudah ditandatangani brand.',
          `Minta tanda tangan basah ${AHA_SIGNER.name} dan cap perusahaan.`,
          'Pindai seluruh halaman, lalu unggah di bawah ini.',
        ].map((step, i) => (
          <li key={step} className="flex items-start gap-3">
            <span className="grid size-6 shrink-0 place-items-center rounded-full bg-secondary text-xs font-extrabold text-foreground">
              {i + 1}
            </span>
            <span className="text-[13px] leading-relaxed text-foreground">{step}</span>
          </li>
        ))}
      </ol>

      <button
        type="button"
        onClick={() => window.print()}
        className="mb-4 inline-flex h-10 items-center gap-2 rounded-full border border-border px-4 text-[13px] font-bold text-foreground hover:bg-secondary"
      >
        <Printer className="size-4" aria-hidden="true" />
        Cetak salinan brand
      </button>

      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.jpg,.jpeg,.png"
        className="sr-only"
        onChange={(e) => setFileName(e.target.files?.[0]?.name ?? null)}
      />

      {fileName ? (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-primary bg-accent/30 p-4">
          <p className="flex min-w-0 items-center gap-2.5 text-[13px] font-bold text-foreground">
            <Check className="size-4 shrink-0 text-primary" aria-hidden="true" />
            <span className="truncate">{fileName}</span>
          </p>
          <button
            type="button"
            onClick={onUploaded}
            className="h-10 shrink-0 rounded-full bg-primary px-5 text-[13px] font-bold text-primary-foreground hover:bg-primary-dark"
          >
            Simpan sebagai NDA final
          </button>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="flex w-full flex-col items-center gap-2 rounded-xl border-2 border-dashed border-border px-4 py-7 text-center hover:border-primary hover:bg-accent/20"
        >
          <FileUp className="size-6 text-muted-foreground" aria-hidden="true" />
          <span className="text-[13px] font-bold text-foreground">
            Unggah salinan bertanda tangan kedua pihak
          </span>
          <span className="text-xs text-muted-foreground">PDF, JPG atau PNG · maks. 10 MB</span>
        </button>
      )}
    </div>
  );
};

/**
 * The AHA side of the NDA — the half that was missing.
 *
 * The brand-facing flow only ever collected the brand's signature, which left
 * every NDA one-sided. This is where AHA Commerce counter-signs, and it offers
 * the same two routes the brand gets: the partner choosing paper must not force
 * AHA onto paper, or the reverse.
 */
export const InternalNdaPage = () => {
  const [queue, setQueue] = useState<NdaRecord[]>(previewNdaQueue);
  const [selectedName, setSelectedName] = useState(
    () => previewNdaQueue().find((r) => r.status === 'awaiting_aha')?.brandName ?? '',
  );
  const [route, setRoute] = useState<NdaRoute>('digital');

  const selected = queue.find((r) => r.brandName === selectedName) ?? queue[0];
  const pending = queue.filter((r) => r.status === 'awaiting_aha').length;

  const apply = (r: NdaRoute) =>
    setQueue((rows) =>
      rows.map((row) =>
        row.brandName === selected.brandName ? countersign(row, r, new Date()) : row,
      ),
    );

  return (
    <div className="min-h-screen bg-background px-4 py-8 sm:px-8">
      <div className="mx-auto w-full max-w-6xl">
        <header className="mb-7">
          <p className="mb-1.5 text-[11px] font-extrabold tracking-wider text-muted-foreground">
            SISI INTERNAL AHA COMMERCE
          </p>
          <h1 className="mb-2 text-2xl font-extrabold tracking-tight text-foreground">
            Tanda tangan NDA
          </h1>
          <p className="max-w-[70ch] text-sm leading-relaxed text-muted-foreground">
            NDA mengikat AHA Commerce, jadi dokumen baru berlaku setelah{' '}
            <strong className="text-foreground">{AHA_SIGNER.name}</strong> ikut menandatangani.
            {pending > 0 && (
              <>
                {' '}
                <span className="font-bold text-foreground">
                  {pending} dokumen menunggu tanda tangan Anda.
                </span>
              </>
            )}
          </p>
        </header>

        <div className="flex flex-wrap items-start gap-5">
          <section className="min-w-0 flex-1 basis-80">
            <ul className="flex flex-col gap-2.5">
              {queue.map((row) => (
                <li key={row.brandName}>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedName(row.brandName);
                      // Reset the route with the document. Carrying the last
                      // choice over means a signer who used paper once lands on
                      // the paper route for the next brand without noticing.
                      setRoute('digital');
                    }}
                    aria-current={row.brandName === selected.brandName}
                    className={cn(
                      'w-full rounded-2xl border bg-card p-5 text-left transition-colors',
                      row.brandName === selected.brandName
                        ? 'border-primary ring-2 ring-ring/30'
                        : 'border-border hover:bg-secondary',
                    )}
                  >
                    <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
                      <span className="text-[15px] font-bold text-foreground">{row.brandName}</span>
                      <span
                        className={cn(
                          'rounded-full px-2.5 py-1 text-[11px] font-extrabold',
                          STATUS_TONE[row.status],
                        )}
                      >
                        {STATUS_LABEL[row.status]}
                      </span>
                    </div>
                    <p className="text-[13px] text-muted-foreground">
                      {row.pic} · {row.picRole}
                    </p>
                    {row.brandSignedAt && row.brandRoute && (
                      <p className="mt-1.5 text-xs text-muted-foreground">
                        Brand tanda tangan {ROUTE_LABEL[row.brandRoute].toLowerCase()} ·{' '}
                        {hoursSince(row.brandSignedAt)}
                      </p>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          </section>

          <section className="min-w-0 flex-[1.3] basis-96 rounded-2xl border border-border bg-card p-7">
            <h2 className="mb-1 text-lg font-extrabold tracking-tight text-foreground">
              {selected.brandName}
            </h2>
            <p className="mb-6 text-[13px] text-muted-foreground">
              {STATUS_LABEL[selected.status]}
            </p>

            {selected.brandRoute === 'paper' && selected.status === 'awaiting_aha' && (
              // The scan is the document here. Signing without opening it would
              // make the review a rubber stamp.
              <p className="mb-6 rounded-xl border border-gold/40 bg-gold/10 p-4 text-[13px] leading-relaxed text-foreground">
                Brand ini tanda tangan di atas kertas.{' '}
                <strong>Buka pindaiannya dan periksa</strong> tanda tangan serta meterainya sebelum
                Anda ikut menandatangani.
              </p>
            )}

            <div className="mb-7 rounded-xl border border-border bg-secondary/40 px-6 py-5">
              <NdaSignatures
                pic={selected.pic}
                picRole={selected.picRole}
                brandRoute={selected.brandRoute}
                brandSigned={selected.brandSignedAt !== null}
                ahaRoute={selected.ahaRoute}
                ahaSigned={selected.ahaSignedAt !== null}
              />
            </div>

            {selected.status === 'awaiting_brand' && (
              <p className="rounded-xl border border-border bg-secondary p-4 text-[13px] leading-relaxed text-secondary-foreground">
                Brand belum menandatangani. AHA tidak bisa menandatangani lebih dulu — urutannya
                justru inti dari tanda tangan balik.
              </p>
            )}

            {selected.status === 'executed' && (
              <p className="flex items-center gap-2.5 rounded-xl border border-primary/40 bg-accent/30 p-4 text-[13px] font-bold text-foreground">
                <Check className="size-4 shrink-0 text-primary" aria-hidden="true" />
                Ditandatangani kedua pihak. Salinan final sudah dikirim ke brand.
              </p>
            )}

            {canCountersign(selected) && (
              <>
                <div
                  className="mb-5 inline-flex flex-wrap gap-1 rounded-full bg-secondary p-1"
                  role="group"
                  aria-label="Cara menandatangani"
                >
                  {(
                    [
                      { r: 'digital' as const, label: 'Tanda tangan digital', icon: PenLine },
                      { r: 'paper' as const, label: 'Cetak & unggah', icon: Printer },
                    ]
                  ).map(({ r, label, icon: Icon }) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => setRoute(r)}
                      aria-pressed={route === r}
                      className={cn(
                        'inline-flex items-center gap-2 rounded-full px-4 py-2 text-[13px] font-bold transition-colors',
                        route === r
                          ? 'bg-card text-foreground shadow-sm'
                          : 'text-muted-foreground hover:text-foreground',
                      )}
                    >
                      <Icon className="size-4" aria-hidden="true" />
                      {label}
                    </button>
                  ))}
                </div>

                {route === 'digital' ? (
                  <div>
                    <p className="mb-4 text-[13px] leading-relaxed text-muted-foreground">
                      Menandatangani sebagai{' '}
                      <strong className="text-foreground">{AHA_SIGNER.name}</strong>,{' '}
                      {AHA_SIGNER.role}. Salinan final langsung dikirim ke brand.
                    </p>
                    <button
                      type="button"
                      onClick={() => apply('digital')}
                      className="h-12 w-full rounded-full bg-primary text-[15px] font-bold text-primary-foreground hover:bg-primary-dark"
                    >
                      Tanda tangani NDA ini
                    </button>
                  </div>
                ) : (
                  <AhaPaperRoute onUploaded={() => apply('paper')} />
                )}
              </>
            )}
          </section>
        </div>

        <p className="mx-auto mt-6 max-w-[76ch] text-center text-xs leading-relaxed text-muted-foreground">
          Pratinjau dengan data palsu. Status hanya berubah di layar ini dan kembali seperti semula
          saat halaman dimuat ulang.
        </p>
      </div>
    </div>
  );
};
