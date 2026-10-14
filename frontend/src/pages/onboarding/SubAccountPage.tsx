import { useState } from 'react';
import { Link } from 'react-router-dom';
import { TriangleAlert } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { PREVIEW_BRAND } from '../../mocks/onboarding';
import { cn } from '../../lib/utils';

/**
 * The two answers are mutually exclusive, so they are radios, not checkboxes:
 * a brand either used the credentials we gave them or used their own, and
 * 'both' is not a state the evaluation team can act on.
 */
type SubAccountChoice = 'given' | 'own';

export const SubAccountPage = () => {
  // Nothing is preselected. A pre-ticked 'sudah' is the answer most brands
  // would leave untouched, and a wrong yes here costs the team a failed login
  // and a day of back-and-forth.
  const [choice, setChoice] = useState<SubAccountChoice | null>(null);
  const chosen = choice !== null;

  return (
    <OnboardingLayout current={4} width="max-w-3xl">
      <h1 className="mb-2 text-2xl font-extrabold tracking-tight text-foreground">
        Konfirmasi sub akun Anda
      </h1>
      <p className="mb-6 text-sm leading-relaxed text-muted-foreground">
        Pilih salah satu — setelah ini tim AHA mulai menarik data dan Anda tidak perlu melakukan
        apa pun lagi.
      </p>

      <fieldset className="mb-6">
        <legend className="sr-only">Status sub akun</legend>

        <div className="flex flex-col gap-3">
          <Label
            className={cn(
              'flex cursor-pointer items-start gap-3.5 rounded-2xl border bg-card p-6 font-normal transition-colors',
              choice === 'given' ? 'border-primary ring-2 ring-ring/30' : 'border-border',
            )}
          >
            <input
              type="radio"
              name="sub-akun"
              value="given"
              checked={choice === 'given'}
              onChange={() => setChoice('given')}
              className="mt-0.5 size-4.5 accent-primary"
            />
            <span className="min-w-0 flex-1">
              <span className="mb-2 block text-[15px] font-bold text-foreground">
                Sudah — saya memakai email dan kata sandi yang diberikan
              </span>
              <span className="block break-all rounded-lg border border-border bg-secondary px-3 py-2.5 font-mono text-[13px] text-secondary-foreground">
                {PREVIEW_BRAND.subAccountEmail} · {PREVIEW_BRAND.subAccountPassword}
              </span>
            </span>
          </Label>

          <Label
            className={cn(
              'flex cursor-pointer items-start gap-3.5 rounded-2xl border bg-card p-6 font-normal transition-colors',
              choice === 'own' ? 'border-primary ring-2 ring-ring/30' : 'border-border',
            )}
          >
            <input
              type="radio"
              name="sub-akun"
              value="own"
              checked={choice === 'own'}
              onChange={() => setChoice('own')}
              className="mt-0.5 size-4.5 accent-primary"
            />
            <span className="min-w-0 flex-1">
              <span className="block text-[15px] font-bold text-foreground">
                Saya memakai email / kata sandi yang berbeda
              </span>
              <span className="mt-1 block text-[13px] leading-relaxed text-muted-foreground">
                Isi kredensial yang benar-benar Anda pakai.
              </span>

              {choice === 'own' && (
                <span className="mt-5 block animate-in fade-in slide-in-from-top-1 duration-200">
                  <span className="mb-5 flex gap-3 rounded-xl border border-gold/40 bg-gold/10 p-3.5">
                    <TriangleAlert
                      className="mt-0.5 size-4.5 shrink-0 text-foreground"
                      aria-hidden="true"
                    />
                    <span className="text-[13px] leading-relaxed text-foreground">
                      Boleh saja — tapi proses jadi lebih lambat karena tim kami harus memasukkan
                      kredensial ini secara manual.
                    </span>
                  </span>

                  <span className="mb-4 block">
                    <Label htmlFor="own-email" className="mb-1.5 block text-[13px] font-bold">
                      Email sub akun yang Anda pakai
                    </Label>
                    <Input
                      id="own-email"
                      type="email"
                      placeholder="email@contoh.com"
                      className="h-11"
                    />
                  </span>
                  <span className="block">
                    <Label htmlFor="own-pw" className="mb-1.5 block text-[13px] font-bold">
                      Kata sandi sub akun
                    </Label>
                    <Input
                      id="own-pw"
                      type="password"
                      placeholder="Kata sandi yang Anda buat"
                      className="h-11"
                    />
                  </span>
                  <span className="mt-3 block text-xs leading-relaxed text-muted-foreground">
                    Disimpan terenkripsi, hanya terbaca tim evaluasi, dan dihapus bersama sub akun
                    setelah evaluasi selesai.
                  </span>
                </span>
              )}
            </span>
          </Label>
        </div>
      </fieldset>

      <Link
        to="/preview/onboarding/proses"
        aria-disabled={!chosen}
        tabIndex={chosen ? undefined : -1}
        className={cn(
          'block h-13 rounded-full text-center text-[15px] font-bold leading-[52px]',
          chosen
            ? 'bg-primary text-primary-foreground hover:bg-primary-dark'
            : 'pointer-events-none bg-muted text-muted-foreground',
        )}
      >
        Kirim &amp; mulai evaluasi →
      </Link>

      <p className="mt-4 text-center text-xs leading-relaxed text-muted-foreground">
        {chosen
          ? 'Menekan tombol ini mengirim notifikasi ke tim AHA bahwa brand Anda siap dievaluasi.'
          : 'Pilih salah satu di atas untuk melanjutkan.'}
      </p>
    </OnboardingLayout>
  );
};
