import { Link } from 'react-router-dom';
import { Copy, TriangleAlert } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { Button } from '../../components/ui/button';
import { PREVIEW_BRAND } from '../../mocks/onboarding';

const STEPS = [
  {
    title: 'Buka Seller Centre › Pengaturan Toko › Pengaturan Sub Akun',
    body: 'Hanya akun utama (main account) yang bisa membuat sub akun.',
  },
  {
    title: 'Klik "Tambah Sub Akun" dan tempel email di atas',
    body: 'Gunakan tombol Salin agar tidak ada salah ketik.',
  },
  {
    title: 'Beri hak akses: Pesanan, Produk, Keuangan, Iklan, Data',
    body: 'Tanpa kelimanya, sebagian kategori SICU tidak bisa dinilai.',
  },
];

const CopyField = ({ label, value, hint }: { label: string; value: string; hint?: string }) => (
  <div className="min-w-0 flex-1 basis-64">
    <p className="mb-1.5 text-xs font-extrabold tracking-wider text-muted-foreground">{label}</p>
    <div className="flex flex-wrap items-center gap-2">
      <code className="break-all rounded-lg border border-border bg-secondary px-3 py-2.5 font-mono text-[15px] font-bold text-foreground">
        {value}
      </code>
      <Button variant="outline" size="sm" className="h-9.5 gap-1.5" aria-label={`Salin ${label}`}>
        <Copy className="size-3.5" aria-hidden="true" />
        Salin
      </Button>
    </div>
    {hint && <p className="mt-2 text-xs text-muted-foreground">{hint}</p>}
  </div>
);

export const TutorialPage = () => (
  <OnboardingLayout current={3} width="max-w-4xl">
    <h1 className="mb-2 text-2xl font-extrabold tracking-tight text-foreground">
      Buat sub akun Shopee untuk tim AHA
    </h1>
    <p className="mb-6 max-w-[72ch] text-sm leading-relaxed text-muted-foreground">
      Supaya kami bisa menarik data toko Anda, buat satu sub akun di Seller Centre dengan email dan
      kata sandi berikut. Akun ini kami hapus setelah evaluasi selesai.
    </p>

    <div className="mb-6 rounded-2xl border-2 border-primary bg-card p-6">
      <div className="flex flex-wrap gap-5">
        <CopyField
          label="EMAIL SUB AKUN"
          value={PREVIEW_BRAND.subAccountEmail}
          hint="Diambil otomatis dari voucher Anda."
        />
        <CopyField label="KATA SANDI" value={PREVIEW_BRAND.subAccountPassword} />
      </div>

      <div className="mt-5 flex gap-3 rounded-xl border border-penalti/30 bg-penalti/5 p-4">
        <TriangleAlert className="mt-0.5 size-[18px] shrink-0 text-penalti" aria-hidden="true" />
        <p className="text-[13px] leading-relaxed text-foreground">
          <strong>Email dan kata sandi harus sama persis.</strong> Kalau berbeda, sistem kami tidak
          bisa masuk dan evaluasi tertunda. Kalau Anda terlanjur memakai yang lain, isi form di
          langkah berikutnya.
        </p>
      </div>
    </div>

    <div className="rounded-2xl border border-border bg-card p-7">
      <h2 className="mb-5 text-[17px] font-extrabold text-foreground">
        Langkah-langkah di Seller Centre
      </h2>

      <ol className="flex flex-col gap-6">
        {STEPS.map((step, i) => (
          <li key={step.title} className="flex flex-wrap items-start gap-4">
            <span className="grid size-7.5 shrink-0 place-items-center rounded-full bg-primary text-sm font-extrabold text-primary-foreground">
              {i + 1}
            </span>
            <div className="min-w-0 flex-1 basis-60">
              <p className="mb-1 text-sm font-bold text-foreground">{step.title}</p>
              <p className="text-[13px] leading-relaxed text-muted-foreground">{step.body}</p>
            </div>
            <div className="grid h-36 w-64 shrink-0 place-items-center rounded-xl border-2 border-dashed border-border bg-secondary p-3 text-center">
              <span className="text-xs font-bold text-muted-foreground">
                [TANGKAPAN LAYAR {i + 1} — menyusul dari AHA]
              </span>
            </div>
          </li>
        ))}
      </ol>

      <p className="mt-6 border-t border-border pt-4 text-xs leading-relaxed text-muted-foreground">
        Isi dan jumlah langkah menyesuaikan tutorial final yang Anda kirim — struktur halaman ini
        tidak berubah.
      </p>
    </div>

    <Link
      to="/preview/onboarding/sub-akun"
      className="mt-6 block h-13 rounded-xl bg-primary text-center text-[15px] font-bold leading-[52px] text-primary-foreground hover:bg-primary-dark"
    >
      Saya sudah membuat sub akun →
    </Link>
  </OnboardingLayout>
);
