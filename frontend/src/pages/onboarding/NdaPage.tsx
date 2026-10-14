import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Clock, PenLine, Printer, ShieldCheck } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { NdaManualUpload } from '../../components/onboarding/NdaManualUpload';
import { NdaSignatures } from '../../components/onboarding/NdaSignatures';
import { AHA_SIGNER } from '../../mocks/nda';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { RadioGroup, RadioGroupItem } from '../../components/ui/radio-group';
import { cn } from '../../lib/utils';

const ENTITY_TYPES = ['PT', 'CV', 'Perorangan'] as const;

/** Digital signature, or print-sign-scan for partners who require paper. */
type SignMode = 'digital' | 'manual';

const SIGN_MODES: { mode: SignMode; label: string; icon: typeof PenLine }[] = [
  { mode: 'digital', label: 'Tanda tangan digital', icon: PenLine },
  { mode: 'manual', label: 'Cetak, tanda tangan, unggah', icon: Printer },
];

export const NdaPage = () => {
  const [mode, setMode] = useState<SignMode>('digital');
  const [uploaded, setUploaded] = useState(false);
  const [entity, setEntity] = useState<string>('PT');
  const [company, setCompany] = useState('PT Covermake Indonesia');
  const [pic, setPic] = useState('Budi Santoso');
  const [role, setRole] = useState('Direktur Operasional');
  const [address, setAddress] = useState(
    'Jl. Gatot Subroto Kav. 21, Jakarta Selatan 12930',
  );

  const signature = pic.trim() || 'Nama Anda';
  // On the paper route nothing is agreed until the scan is in.
  const canContinue = mode === 'digital' || uploaded;

  return (
    <OnboardingLayout current={2} width="max-w-6xl">
      <div className="mb-6 flex gap-3 rounded-xl border border-border bg-secondary p-4">
        <ShieldCheck
          className="mt-0.5 size-[22px] shrink-0 text-primary"
          aria-hidden="true"
        />
        <p className="text-sm leading-relaxed text-secondary-foreground">
          <strong>NDA ini melindungi Anda, bukan kami.</strong> Dokumen ini
          mengikat AHA Commerce untuk menjaga kerahasiaan seluruh data toko,
          penjualan dan produk Anda — dan melarang kami membagikannya ke pihak
          mana pun, termasuk brand lain.
        </p>
      </div>

      <div
        className="mb-6 inline-flex flex-wrap gap-1 rounded-full bg-secondary p-1"
        role="group"
        aria-label="Cara menandatangani"
      >
        {SIGN_MODES.map(({ mode: m, label, icon: Icon }) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            aria-pressed={mode === m}
            className={cn(
              'inline-flex items-center gap-2 rounded-full px-4 py-2 text-[13px] font-bold transition-colors',
              mode === m
                ? 'bg-card text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground',
            )}
          >
            <Icon className="size-4" aria-hidden="true" />
            {label}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap items-start gap-6">
        {/* Form */}
        <section className="min-w-0 flex-1 basis-[420px]">
          {mode === 'manual' ? (
            <NdaManualUpload onUploadedChange={setUploaded} />
          ) : (
            <div className="rounded-2xl border border-border bg-card p-7">
              <h1 className="mb-1 text-xl font-extrabold tracking-tight text-foreground">
                Data perusahaan
              </h1>
              <p className="mb-6 text-[13px] text-muted-foreground">
                NDA di sebelah kanan terisi otomatis saat Anda mengetik.
              </p>

              <fieldset className="mb-5">
                <legend className="mb-2 text-[13px] font-bold text-foreground">
                  Bentuk badan usaha
                </legend>
                <RadioGroup
                  value={entity}
                  onValueChange={setEntity}
                  className="flex flex-wrap gap-2"
                >
                  {ENTITY_TYPES.map((type) => (
                    <Label
                      key={type}
                      htmlFor={`entity-${type}`}
                      className={
                        entity === type
                          ? 'flex cursor-pointer items-center gap-2 rounded-full border-2 border-primary bg-accent/30 px-4 py-2.5 text-[13px] font-bold text-primary'
                          : 'flex cursor-pointer items-center gap-2 rounded-full border border-border px-4 py-2.5 text-[13px] font-semibold text-foreground'
                      }
                    >
                      <RadioGroupItem value={type} id={`entity-${type}`} />
                      {type}
                    </Label>
                  ))}
                </RadioGroup>
              </fieldset>

              <div className="mb-4">
                <Label
                  htmlFor="company"
                  className="mb-1.5 block text-[13px] font-bold"
                >
                  Nama perusahaan / brand
                </Label>
                <Input
                  id="company"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="h-11"
                />
              </div>

              <div className="mb-4">
                <Label
                  htmlFor="pic"
                  className="mb-1.5 block text-[13px] font-bold"
                >
                  Nama penanggung jawab
                </Label>
                <Input
                  id="pic"
                  value={pic}
                  onChange={(e) => setPic(e.target.value)}
                  className="h-11"
                />
              </div>

              <div className="mb-4">
                <Label
                  htmlFor="role"
                  className="mb-1.5 block text-[13px] font-bold"
                >
                  Jabatan PIC
                </Label>
                <Input
                  id="role"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="h-11"
                />
              </div>

              <div className="mb-6">
                <Label
                  htmlFor="address"
                  className="mb-1.5 block text-[13px] font-bold"
                >
                  Alamat perusahaan
                </Label>
                <textarea
                  id="address"
                  rows={3}
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  className="w-full resize-y rounded-xl border border-input bg-card px-3.5 py-2.5 text-sm leading-relaxed text-foreground outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                />
              </div>

              <div className="rounded-xl border border-border bg-secondary p-5">
                <h2 className="mb-1 text-sm font-extrabold text-foreground">
                  Tanda tangan
                </h2>
                <p className="mb-3.5 text-xs leading-relaxed text-muted-foreground">
                  Dibuat otomatis dari nama penanggung jawab. Ubah nama di atas
                  untuk memperbarui.
                </p>
                <div className="relative grid h-26 place-items-center rounded-xl border-2 border-dashed border-border bg-card">
                  <span className="px-4 text-center text-4xl leading-none text-foreground [font-family:'Caveat',cursive]">
                    {signature}
                  </span>
                  <span
                    className="absolute inset-x-5 bottom-4 h-px bg-border"
                    aria-hidden="true"
                  />
                </div>
                <Label className="mt-4 flex cursor-pointer items-start gap-2.5 text-[13px] leading-relaxed font-normal">
                  <input
                    type="checkbox"
                    defaultChecked
                    className="mt-1 accent-primary"
                  />
                  <span className="text-foreground">
                    Saya menyatakan berwenang menandatangani atas nama{' '}
                    <strong>{company}</strong> dan menyetujui isi NDA ini.
                  </span>
                </Label>
              </div>
            </div>
          )}
        </section>

        {/* Live NDA */}
        <section className="flex min-w-0 flex-1 basis-[400px] flex-col gap-3.5">
          <article className="rounded-2xl border border-border bg-card px-8 py-8 text-xs leading-[1.85] text-secondary-foreground">
            <p className="mb-1 text-center text-[11px] font-extrabold tracking-[0.12em] text-muted-foreground">
              PERJANJIAN KERAHASIAAN
            </p>
            <p className="mb-6 text-center text-[15px] font-extrabold text-foreground">
              Non-Disclosure Agreement
            </p>

            <p className="mb-3.5">
              Perjanjian ini dibuat antara{' '}
              <strong>PT AHA Commerce Indonesia</strong> (<em>Pihak Pertama</em>
              ) dan{' '}
              <strong className="rounded bg-gold/25 px-1">{company}</strong> (
              {entity}), beralamat di{' '}
              <span className="rounded bg-gold/25 px-1">{address}</span>,
              diwakili oleh{' '}
              <strong className="rounded bg-gold/25 px-1">{pic}</strong> selaku{" "}
              <strong className="rounded bg-gold/25 px-1">{role}</strong> (
              <em>Pihak Kedua</em>).
            </p>

            <p className="mb-2 font-bold text-foreground">
              Pasal 1 — Informasi Rahasia
            </p>
            <p className="mb-4">
              Seluruh data penjualan, produk, pelanggan, iklan dan operasional
              toko Pihak Kedua yang diakses Pihak Pertama selama evaluasi Store
              ICU merupakan Informasi Rahasia.
            </p>

            <p className="mb-2 font-bold text-foreground">
              Pasal 2 — Kewajiban Pihak Pertama
            </p>
            <p className="mb-4">
              Pihak Pertama dilarang mengungkapkan Informasi Rahasia kepada
              pihak ketiga mana pun, termasuk brand lain yang juga dievaluasi.
            </p>

            <p className="mb-2 font-bold text-foreground">
              Pasal 3 — Akses Sub Akun
            </p>
            <p className="mb-6">
              Akses sub akun Shopee yang diberikan bersifat sementara dan akan
              dihapus Pihak Pertama setelah evaluasi selesai.
            </p>

            <NdaSignatures
              pic={pic}
              picRole={role}
              brandRoute={mode === 'manual' ? 'paper' : 'digital'}
              brandSigned
              ahaRoute={null}
              ahaSigned={false}
            />
          </article>

          <Link
            to="/preview/onboarding/tutorial"
            aria-disabled={!canContinue}
            tabIndex={canContinue ? undefined : -1}
            className={cn(
              'block h-13 rounded-full text-center text-[15px] font-bold leading-[52px]',
              canContinue
                ? 'bg-primary text-primary-foreground hover:bg-primary-dark'
                : 'pointer-events-none bg-muted text-muted-foreground',
            )}
          >
            {mode === 'manual'
              ? 'Kirim NDA & lanjutkan →'
              : 'Tanda tangani & lanjutkan →'}
          </Link>
          <p className="text-center text-xs leading-relaxed text-muted-foreground">
            {mode === 'manual'
              ? canContinue
                ? 'Berkas Anda dikirim ke tim Partnership untuk diperiksa.'
                : 'Unggah NDA yang sudah ditandatangani untuk melanjutkan.'
              : 'Salinan PDF dikirim ke email Anda dan disimpan di akun SICU.'}
          </p>

          {/* An NDA binds AHA too, so it is not an agreement until AHA has
              signed it. Saying "selesai" here would be a lie the brand only
              discovers when they look for the executed copy. */}
          <p className="flex items-start gap-2 rounded-xl border border-border bg-secondary p-3.5 text-xs leading-relaxed text-secondary-foreground">
            <Clock className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
            <span>
              Setelah Anda tanda tangan, <strong>{AHA_SIGNER.name}</strong> (
              {AHA_SIGNER.role}) menandatangani dari pihak AHA Commerce. Salinan final yang sudah
              ditandatangani kedua pihak dikirim ke email Anda — biasanya dalam 1 hari kerja.
            </span>
          </p>
        </section>
      </div>
    </OnboardingLayout>
  );
};
