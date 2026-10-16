import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Check, Mail, ShieldCheck } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { RadioGroup, RadioGroupItem } from '../../components/ui/radio-group';
import { formatDeadline } from '../../lib/workdays';
import { cn } from '../../lib/utils';

const ENTITY_TYPES = ['PT', 'CV', 'Perorangan'] as const;

/**
 * Marks a field the brand cannot skip.
 *
 * Marwah, 14 Oct: an incomplete company form must block the request outright.
 * These fields are what the internal team generates the NDA from, so a blank
 * here is a document that names nobody and a day lost chasing it.
 */
const Required = () => (
  <span className="ms-0.5 text-penalti" aria-label="wajib diisi">
    *
  </span>
);

/**
 * The NDA step.
 *
 * Alfiano, 15 Oct: the NDA is generated OUTSIDE this app. This page shows the
 * template and collects the company details; when the brand agrees, a button
 * emails the internal team, who send the DocuSign NDA out of band. Nothing is
 * signed here — the in-app signature, the print/sign/scan route and the
 * counter-signature queue were all removed with that decision.
 */
export const NdaPage = () => {
  const [entity, setEntity] = useState<string>('PT');
  const [company, setCompany] = useState('PT Covermake Indonesia');
  const [pic, setPic] = useState('Budi Santoso');
  const [role, setRole] = useState('Direktur Operasional');
  const [address, setAddress] = useState('Jl. Gatot Subroto Kav. 21, Jakarta Selatan 12930');
  const [agreed, setAgreed] = useState(false);
  const [requested, setRequested] = useState(false);

  // Stamped at render in the preview. The real flow stamps it when the NDA is
  // generated and stores it — a creation date that moves every time the
  // document is opened is worse than no date.
  const createdOn = formatDeadline(new Date());

  const complete = [company, pic, role, address].every((v) => v.trim().length > 0);
  // Agreement alone isn't enough: the team can't generate anything from a form
  // with holes in it, so the button only appears once both are true.
  const canRequest = complete && agreed;

  return (
    <OnboardingLayout current={2} width="max-w-6xl">
      <div className="mb-6 flex gap-3 rounded-xl border border-border bg-secondary p-4">
        <ShieldCheck className="mt-0.5 size-[22px] shrink-0 text-primary" aria-hidden="true" />
        <p className="text-sm leading-relaxed text-secondary-foreground">
          <strong>NDA ini melindungi Anda, bukan kami.</strong> Dokumen ini mengikat AHA Commerce
          untuk menjaga kerahasiaan seluruh data toko, penjualan dan produk Anda — dan melarang
          kami membagikannya ke pihak mana pun, termasuk brand lain.
        </p>
      </div>

      <div className="flex flex-wrap items-start gap-6">
        <section className="min-w-0 flex-1 basis-[420px]">
          <div className="rounded-2xl border border-border bg-card p-7">
            <h1 className="mb-1 text-xl font-extrabold tracking-tight text-foreground">
              Data perusahaan
            </h1>
            <p className="mb-6 text-[13px] leading-relaxed text-muted-foreground">
              Dipakai tim AHA untuk menyiapkan NDA Anda. Pratinjau di sebelah kanan ikut berubah
              saat Anda mengetik.
            </p>

            <fieldset className="mb-5">
              <legend className="mb-2 text-[13px] font-bold text-foreground">
                Bentuk badan usaha
                <Required />
              </legend>
              <RadioGroup value={entity} onValueChange={setEntity} className="flex flex-wrap gap-2">
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
              <Label htmlFor="company" className="mb-1.5 block text-[13px] font-bold">
                Nama perusahaan / brand
                <Required />
              </Label>
              <Input
                id="company"
                required
                aria-invalid={company.trim().length === 0}
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="h-11"
              />
            </div>

            <div className="mb-4">
              <Label htmlFor="pic" className="mb-1.5 block text-[13px] font-bold">
                Nama penanggung jawab
                <Required />
              </Label>
              <Input
                id="pic"
                required
                aria-invalid={pic.trim().length === 0}
                value={pic}
                onChange={(e) => setPic(e.target.value)}
                className="h-11"
              />
            </div>

            <div className="mb-4">
              <Label htmlFor="role" className="mb-1.5 block text-[13px] font-bold">
                Jabatan PIC
                <Required />
              </Label>
              <Input
                id="role"
                required
                aria-invalid={role.trim().length === 0}
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="h-11"
              />
            </div>

            <div className="mb-6">
              <Label htmlFor="address" className="mb-1.5 block text-[13px] font-bold">
                Alamat perusahaan
                <Required />
              </Label>
              <textarea
                id="address"
                required
                aria-invalid={address.trim().length === 0}
                rows={3}
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                className="w-full resize-y rounded-xl border border-input bg-card px-3.5 py-2.5 text-sm leading-relaxed text-foreground outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
              />
            </div>

            <Label className="flex cursor-pointer items-start gap-2.5 rounded-xl border border-border bg-secondary p-4 text-[13px] font-normal leading-relaxed">
              <input
                type="checkbox"
                checked={agreed}
                onChange={(e) => setAgreed(e.target.checked)}
                className="mt-0.5 size-4 accent-primary"
              />
              <span className="text-foreground">
                Saya menyatakan berwenang mewakili <strong>{company}</strong> dan menyetujui isi
                NDA di samping.
              </span>
            </Label>
          </div>
        </section>

        <section className="flex min-w-0 flex-1 basis-[400px] flex-col gap-3.5">
          <article className="rounded-2xl border border-border bg-card px-8 py-8 text-xs leading-[1.85] text-secondary-foreground">
            <header className="mb-6 flex items-center justify-between gap-4 border-b-2 border-foreground/15 pb-4">
              <div className="flex items-center gap-3">
                <img src="/aha-logo.png" alt="AHA Commerce" className="size-9 shrink-0" />
                <div className="min-w-0">
                  <p className="text-[13px] font-extrabold leading-tight text-foreground">
                    PT AHA Commerce Indonesia
                  </p>
                  <p className="text-[10px] leading-tight text-muted-foreground">ahacommerce.net</p>
                </div>
              </div>
              <p className="shrink-0 text-end text-[10px] leading-tight text-muted-foreground">
                Dibuat
                <br />
                <span className="font-semibold text-foreground">{createdOn}</span>
              </p>
            </header>

            <p className="mb-1 text-center text-[11px] font-extrabold tracking-[0.12em] text-muted-foreground">
              PERJANJIAN KERAHASIAAN
            </p>
            <p className="mb-6 text-center text-[15px] font-extrabold text-foreground">
              Non-Disclosure Agreement
            </p>

            <p className="mb-3.5">
              Perjanjian ini dibuat antara <strong>PT AHA Commerce Indonesia</strong> (
              <em>Pihak Pertama</em>) dan{' '}
              <strong className="rounded bg-gold/25 px-1">{company}</strong> ({entity}), beralamat
              di <span className="rounded bg-gold/25 px-1">{address}</span>, diwakili oleh{' '}
              <strong className="rounded bg-gold/25 px-1">{pic}</strong> selaku{' '}
              <strong className="rounded bg-gold/25 px-1">{role}</strong> (<em>Pihak Kedua</em>).
            </p>

            <p className="mb-2 font-bold text-foreground">Pasal 1 — Informasi Rahasia</p>
            <p className="mb-4">
              Seluruh data penjualan, produk, pelanggan, iklan dan operasional toko Pihak Kedua
              yang diakses Pihak Pertama selama evaluasi Store ICU merupakan Informasi Rahasia.
            </p>

            <p className="mb-2 font-bold text-foreground">Pasal 2 — Kewajiban Pihak Pertama</p>
            <p className="mb-4">
              Pihak Pertama dilarang mengungkapkan Informasi Rahasia kepada pihak ketiga mana pun,
              termasuk brand lain yang juga dievaluasi.
            </p>

            <p className="mb-2 font-bold text-foreground">Pasal 3 — Akses Sub Akun</p>
            <p className="mb-6">
              Akses sub akun Shopee yang diberikan bersifat sementara dan akan dihapus Pihak
              Pertama setelah evaluasi selesai.
            </p>

            {/* No signature blocks: signing happens in DocuSign, not here.
                Drawing empty signature lines on a document nobody signs on this
                page would imply the brand is meant to do something with them. */}
            <p className="border-t border-border pt-3.5 text-[11px] leading-relaxed text-muted-foreground">
              Pratinjau. Penandatanganan dilakukan melalui DocuSign — tautan dikirim ke email Anda
              oleh tim AHA Commerce.
            </p>
          </article>

          {requested ? (
            <>
              <div className="flex items-start gap-3 rounded-xl border border-primary bg-accent/30 p-4">
                <Check className="mt-0.5 size-5 shrink-0 text-primary" aria-hidden="true" />
                <div>
                  <p className="mb-1 text-sm font-bold text-foreground">
                    Permintaan NDA terkirim ke tim AHA Commerce
                  </p>
                  <p className="text-[13px] leading-relaxed text-secondary-foreground">
                    Anda akan menerima email dari DocuSign berisi NDA untuk ditandatangani,
                    biasanya dalam 1 hari kerja. Anda bisa lanjut ke langkah berikutnya sambil
                    menunggu.
                  </p>
                </div>
              </div>

              <Link
                to="/preview/onboarding/tutorial"
                className="block h-13 rounded-full bg-primary text-center text-[15px] font-bold leading-[52px] text-primary-foreground hover:bg-primary-dark"
              >
                Lanjut ke tutorial sub akun →
              </Link>
            </>
          ) : (
            <>
              <button
                type="button"
                onClick={() => setRequested(true)}
                disabled={!canRequest}
                className={cn(
                  'inline-flex h-13 items-center justify-center gap-2.5 rounded-full text-[15px] font-bold',
                  canRequest
                    ? 'bg-primary text-primary-foreground hover:bg-primary-dark'
                    : 'cursor-not-allowed bg-muted text-muted-foreground',
                )}
              >
                <Mail className="size-4.5" aria-hidden="true" />
                Minta NDA dari tim AHA
              </button>
              <p className="text-center text-xs leading-relaxed text-muted-foreground">
                {!complete
                  ? 'Lengkapi semua kolom bertanda * terlebih dahulu.'
                  : !agreed
                    ? 'Centang persetujuan di samping untuk meminta NDA.'
                    : 'Tim AHA akan mengirim NDA melalui DocuSign ke email Anda.'}
              </p>
            </>
          )}
        </section>
      </div>
    </OnboardingLayout>
  );
};
