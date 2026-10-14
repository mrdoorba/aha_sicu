import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { RadioGroup, RadioGroupItem } from '../../components/ui/radio-group';

const ENTITY_TYPES = ['PT', 'CV', 'Perorangan'] as const;

export const NdaPage = () => {
  const [entity, setEntity] = useState<string>('PT');
  const [company, setCompany] = useState('PT Covermake Indonesia');
  const [pic, setPic] = useState('Budi Santoso');
  const [role, setRole] = useState('Direktur Operasional');
  const [address, setAddress] = useState('Jl. Gatot Subroto Kav. 21, Jakarta Selatan 12930');

  const signature = pic.trim() || 'Nama Anda';

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
        {/* Form */}
        <section className="min-w-0 flex-1 basis-[420px] rounded-2xl border border-border bg-card p-7">
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
            </Label>
            <Input
              id="company"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              className="h-11"
            />
          </div>

          <div className="mb-4">
            <Label htmlFor="pic" className="mb-1.5 block text-[13px] font-bold">
              Nama penanggung jawab
            </Label>
            <Input id="pic" value={pic} onChange={(e) => setPic(e.target.value)} className="h-11" />
          </div>

          <div className="mb-4">
            <Label htmlFor="role" className="mb-1.5 block text-[13px] font-bold">
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
            <Label htmlFor="address" className="mb-1.5 block text-[13px] font-bold">
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
            <h2 className="mb-1 text-sm font-extrabold text-foreground">Tanda tangan</h2>
            <p className="mb-3.5 text-xs leading-relaxed text-muted-foreground">
              Dibuat otomatis dari nama penanggung jawab. Ubah nama di atas untuk memperbarui.
            </p>
            <div className="relative grid h-26 place-items-center rounded-xl border-2 border-dashed border-border bg-card">
              <span className="px-4 text-center text-4xl leading-none text-foreground [font-family:'Caveat',cursive]">
                {signature}
              </span>
              <span className="absolute inset-x-5 bottom-4 h-px bg-border" aria-hidden="true" />
            </div>
            <Label className="mt-4 flex cursor-pointer items-start gap-2.5 text-[13px] leading-relaxed font-normal">
              <input type="checkbox" defaultChecked className="mt-1 accent-primary" />
              <span className="text-foreground">
                Saya menyatakan berwenang menandatangani atas nama <strong>{company}</strong> dan
                menyetujui isi NDA ini.
              </span>
            </Label>
          </div>
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

            <div className="flex flex-wrap gap-6 border-t border-border pt-3">
              <div className="min-w-0 flex-1 basis-36">
                <p className="mb-0.5 text-[11px] text-muted-foreground">Pihak Kedua</p>
                <p className="text-3xl leading-tight text-foreground [font-family:'Caveat',cursive]">
                  {signature}
                </p>
                <p className="mt-0.5 text-[11px] font-bold text-foreground">{pic}</p>
                <p className="text-[11px] text-muted-foreground">{role}</p>
              </div>
              <div className="min-w-0 flex-1 basis-36">
                <p className="mb-0.5 text-[11px] text-muted-foreground">Pihak Pertama</p>
                <p className="text-3xl leading-tight text-muted-foreground [font-family:'Caveat',cursive]">
                  AHA Commerce
                </p>
                <p className="mt-0.5 text-[11px] font-bold text-foreground">Marwah K.</p>
                <p className="text-[11px] text-muted-foreground">Partnership Lead</p>
              </div>
            </div>
          </article>

          <Link
            to="/preview/onboarding/tutorial"
            className="block h-13 rounded-full bg-primary text-center text-[15px] font-bold leading-[52px] text-primary-foreground hover:bg-primary-dark"
          >
            Tanda tangani &amp; lanjutkan →
          </Link>
          <p className="text-center text-xs leading-relaxed text-muted-foreground">
            Salinan PDF dikirim ke email Anda dan disimpan di akun SICU.
          </p>
        </section>
      </div>
    </OnboardingLayout>
  );
};
