import { useRef, useState } from 'react';
import { Check, FileUp, Printer } from 'lucide-react';
import { cn } from '../../lib/utils';

const STEPS = [
  'Unduh dan cetak NDA di sebelah kanan.',
  'Tanda tangani di atas meterai, bubuhkan cap perusahaan bila ada.',
  'Pindai atau foto seluruh halaman — pastikan terbaca jelas.',
  'Unggah berkasnya di bawah ini.',
];

const ACCEPT = '.pdf,.jpg,.jpeg,.png';

/**
 * The paper route through the NDA.
 *
 * Some partners will not sign anything digitally, and until now they had no
 * way through this step at all. The upload is what AHA verifies by hand — so
 * the copy says who checks it and how long that takes, rather than implying
 * the brand is instantly done.
 */
export const NdaManualUpload = ({
  onUploadedChange,
}: {
  onUploadedChange: (f: boolean) => void;
}) => {
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const pick = (name: string | null) => {
    setFileName(name);
    onUploadedChange(name !== null);
  };

  return (
    <div className="rounded-2xl border border-border bg-card p-7">
      <h1 className="mb-1 text-xl font-extrabold tracking-tight text-foreground">
        Tanda tangan manual
      </h1>
      <p className="mb-6 text-[13px] leading-relaxed text-muted-foreground">
        Untuk perusahaan yang mewajibkan dokumen fisik bermeterai.
      </p>

      <ol className="mb-6 flex flex-col gap-3.5">
        {STEPS.map((step, i) => (
          <li key={step} className="flex items-start gap-3">
            <span className="grid size-6 shrink-0 place-items-center rounded-full bg-secondary text-xs font-extrabold text-foreground">
              {i + 1}
            </span>
            <span className="text-[13px] leading-relaxed text-foreground">
              {step}
            </span>
          </li>
        ))}
      </ol>

      <button
        type="button"
        onClick={() => window.print()}
        className="mb-5 inline-flex h-11 items-center gap-2 rounded-full border border-border px-4 text-[13px] font-bold text-foreground hover:bg-secondary"
      >
        <Printer className="size-4" aria-hidden="true" />
        Cetak / simpan sebagai PDF
      </button>

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        className="sr-only"
        onChange={(e) => pick(e.target.files?.[0]?.name ?? null)}
      />

      {fileName ? (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-primary bg-accent/30 p-4">
          <p className="flex min-w-0 items-center gap-2.5 text-[13px] font-bold text-foreground">
            <Check
              className="size-4 shrink-0 text-primary"
              aria-hidden="true"
            />
            <span className="truncate">{fileName}</span>
          </p>
          <button
            type="button"
            onClick={() => pick(null)}
            className="text-[13px] font-bold text-primary underline underline-offset-2"
          >
            Ganti berkas
          </button>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className={cn(
            'flex w-full flex-col items-center gap-2 rounded-xl border-2 border-dashed border-border px-4 py-8',
            'text-center hover:border-primary hover:bg-accent/20',
          )}
        >
          <FileUp className="size-6 text-muted-foreground" aria-hidden="true" />
          <span className="text-[13px] font-bold text-foreground">
            Unggah NDA yang sudah ditandatangani
          </span>
          <span className="text-xs text-muted-foreground">
            PDF, JPG atau PNG · maks. 10 MB
          </span>
        </button>
      )}

      <p className="mt-4 text-xs leading-relaxed text-muted-foreground">
        Berkas diperiksa tim Partnership AHA Commerce dalam 1 hari kerja. Anda
        tetap bisa lanjut ke langkah berikutnya sambil menunggu — evaluasi baru
        dimulai setelah NDA disetujui.
      </p>
    </div>
  );
};
