import { useState } from 'react';
import { Link } from 'react-router-dom';
import { TriangleAlert } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { PREVIEW_BRAND } from '../../mocks/onboarding';

export const SubAccountPage = () => {
  const [useOwn, setUseOwn] = useState(false);

  return (
    <OnboardingLayout current={4} width="max-w-3xl">
      <h1 className="mb-2 text-2xl font-extrabold tracking-tight text-foreground">
        Konfirmasi sub akun Anda
      </h1>
      <p className="mb-6 text-sm leading-relaxed text-muted-foreground">
        Setelah ini tim AHA mulai menarik data — Anda tidak perlu melakukan apa pun lagi.
      </p>

      <div className="mb-4 rounded-2xl border border-border bg-card p-7">
        <Label className="flex cursor-pointer items-start gap-3 font-normal">
          <input type="checkbox" defaultChecked className="mt-1 size-4.5 accent-primary" />
          <span>
            <span className="mb-2 block text-[15px] font-bold text-foreground">
              Saya sudah membuat sub akun dengan email dan kata sandi yang diberikan
            </span>
            <span className="block break-all rounded-lg border border-border bg-secondary px-3 py-2.5 font-mono text-[13px] text-secondary-foreground">
              {PREVIEW_BRAND.subAccountEmail} · {PREVIEW_BRAND.subAccountPassword}
            </span>
          </span>
        </Label>
      </div>

      <div className="mb-6 overflow-hidden rounded-2xl border border-border bg-card">
        <button
          type="button"
          onClick={() => setUseOwn((v) => !v)}
          aria-expanded={useOwn}
          className="flex w-full items-center justify-between gap-3.5 px-7 py-5 text-left text-sm font-bold text-foreground"
        >
          <span>Saya memakai email / kata sandi yang berbeda</span>
          <span className="text-[13px] font-bold text-primary">
            {useOwn ? 'Tutup' : 'Buka form'}
          </span>
        </button>

        {useOwn && (
          <div className="border-t border-border px-7 pb-6">
            <div className="my-5 flex gap-3 rounded-xl border border-gold/40 bg-gold/10 p-3.5">
              <TriangleAlert className="mt-0.5 size-4.5 shrink-0 text-foreground" aria-hidden="true" />
              <p className="text-[13px] leading-relaxed text-foreground">
                Boleh saja — tapi proses jadi lebih lambat karena tim kami harus memasukkan
                kredensial ini secara manual.
              </p>
            </div>

            <div className="mb-4">
              <Label htmlFor="own-email" className="mb-1.5 block text-[13px] font-bold">
                Email sub akun yang Anda pakai
              </Label>
              <Input id="own-email" type="email" placeholder="email@contoh.com" className="h-11" />
            </div>
            <div>
              <Label htmlFor="own-pw" className="mb-1.5 block text-[13px] font-bold">
                Kata sandi sub akun
              </Label>
              <Input
                id="own-pw"
                type="password"
                placeholder="Kata sandi yang Anda buat"
                className="h-11"
              />
            </div>
            <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
              Disimpan terenkripsi, hanya terbaca tim evaluasi, dan dihapus bersama sub akun
              setelah evaluasi selesai.
            </p>
          </div>
        )}
      </div>

      <Link
        to="/preview/onboarding/proses"
        className="block h-13 rounded-xl bg-primary text-center text-[15px] font-bold leading-[52px] text-primary-foreground hover:bg-primary-dark"
      >
        Kirim &amp; mulai evaluasi →
      </Link>

      <p className="mt-4 text-center text-xs leading-relaxed text-muted-foreground">
        Menekan tombol ini mengirim notifikasi ke tim AHA bahwa brand Anda siap dievaluasi.
      </p>
    </OnboardingLayout>
  );
};
