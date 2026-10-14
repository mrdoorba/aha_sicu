import { Link } from 'react-router-dom';
import { Check, Copy, ExternalLink, TriangleAlert } from 'lucide-react';
import { OnboardingLayout } from '../../components/onboarding/OnboardingLayout';
import { TutorialVideo } from '../../components/onboarding/TutorialVideo';
import { Button } from '../../components/ui/button';
import {
  PREVIEW_BRAND,
  SHOPEE_SUBACCOUNT_URL,
  SUBACCOUNT_ROLES,
} from '../../mocks/onboarding';
import { cn } from '../../lib/utils';

const CopyField = ({
  label,
  value,
  hint,
  wide,
}: {
  label: string;
  value: string;
  hint?: string;
  /** The sub-account email is long enough to wrap its own button off the row. */
  wide?: boolean;
}) => (
  <div className={cn('min-w-0 flex-1', wide ? 'basis-full' : 'basis-60')}>
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
    {hint && <p className="mt-2 text-xs leading-relaxed text-muted-foreground">{hint}</p>}
  </div>
);

const Step = ({
  n,
  title,
  children,
}: {
  n: number;
  title: React.ReactNode;
  children?: React.ReactNode;
}) => (
  <li className="flex items-start gap-4">
    <span className="grid size-7.5 shrink-0 place-items-center rounded-full bg-primary text-sm font-extrabold text-primary-foreground">
      {n}
    </span>
    <div className="min-w-0 flex-1">
      <p className="mb-1 text-sm font-bold text-foreground">{title}</p>
      {children}
    </div>
  </li>
);

export const TutorialPage = () => (
  <OnboardingLayout current={3} width="max-w-4xl">
    <h1 className="mb-2 text-2xl font-extrabold tracking-tight text-foreground">
      Buat sub akun Shopee untuk tim AHA
    </h1>
    <p className="mb-6 max-w-[72ch] text-sm leading-relaxed text-muted-foreground">
      Kami membutuhkan akses untuk menganalisa performa toko{' '}
      <strong className="text-foreground">{PREVIEW_BRAND.name}</strong> melalui sub akun yang bisa
      Anda buat dengan cara berikut. Akun ini kami hapus setelah evaluasi selesai.
    </p>

    <div className="mb-6">
      <TutorialVideo />
    </div>

    <ol className="mb-6 flex flex-col gap-7 rounded-2xl border border-border bg-card p-7">
      <Step
        n={1}
        title={
          <>
            Kunjungi halaman sub akun Shopee{' '}
            <a
              href={SHOPEE_SUBACCOUNT_URL}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 font-bold text-primary underline underline-offset-2"
            >
              subaccount.shopee.com/member
              <ExternalLink className="size-3.5" aria-hidden="true" />
            </a>
          </>
        }
      >
        <p className="text-[13px] leading-relaxed text-muted-foreground">
          Hanya akun utama (main account) yang bisa membuat sub akun.
        </p>
      </Step>

      <Step n={2} title={<>Klik &ldquo;Tambah Anggota&rdquo;</>} />

      <Step n={3} title="Isi dengan data berikut">
        <div className="mt-3.5 rounded-xl border-2 border-primary bg-card p-5">
          <div className="flex flex-wrap gap-5">
            <CopyField label="NAMA ANGGOTA" value={PREVIEW_BRAND.subAccountMemberName} />
            <CopyField label="LOGIN ID" value={PREVIEW_BRAND.subAccountLoginId} />
            <CopyField label="PASSWORD LOG IN" value={PREVIEW_BRAND.subAccountPassword} />
            <CopyField
              wide
              label="ALAMAT EMAIL"
              value={PREVIEW_BRAND.subAccountEmail}
              hint="Diambil otomatis dari voucher Anda."
            />
          </div>

          <div className="mt-5 rounded-xl border border-border bg-secondary p-4">
            <p className="mb-1 text-xs font-extrabold tracking-wider text-muted-foreground">
              NO. HP
            </p>
            <p className="text-[13px] leading-relaxed text-foreground">
              Gunakan nomor yang <strong>belum pernah dipakai di Shopee</strong>. Nomor yang sudah
              terdaftar akan ditolak saat sub akun dibuat.
            </p>
          </div>

          <div className="mt-4 flex gap-3 rounded-xl border border-penalti/30 bg-penalti/5 p-4">
            <TriangleAlert className="mt-0.5 size-[18px] shrink-0 text-penalti" aria-hidden="true" />
            <p className="text-[13px] leading-relaxed text-foreground">
              <strong>Login ID, email dan password harus sama persis.</strong> Kalau berbeda, sistem
              kami tidak bisa masuk dan evaluasi tertunda. Kalau Anda terlanjur memakai yang lain,
              isi form di langkah berikutnya.
            </p>
          </div>
        </div>
      </Step>

      <Step n={4} title="Pengaturan Peran — centang semuanya">
        <p className="mb-3.5 text-[13px] leading-relaxed text-muted-foreground">
          Tanpa salah satu izin di bawah, ada kategori SICU yang tidak bisa dinilai sama sekali.
        </p>
        <ul className="flex flex-col gap-2 rounded-xl border border-border bg-secondary/50 p-5">
          {SUBACCOUNT_ROLES.map((role) => (
            <li key={role.label}>
              <p className="flex items-start gap-2 text-[13px] font-semibold text-foreground">
                <Check className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
                {role.label}
              </p>
              {role.children && (
                <ul className="ms-6 mt-2 flex flex-col gap-2">
                  {role.children.map((child) => (
                    <li
                      key={child}
                      className="flex items-start gap-2 text-[13px] text-secondary-foreground"
                    >
                      <Check className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
                      {child}
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      </Step>
    </ol>

    <Link
      to="/preview/onboarding/sub-akun"
      className="block h-13 rounded-full bg-primary text-center text-[15px] font-bold leading-[52px] text-primary-foreground hover:bg-primary-dark"
    >
      Saya sudah membuat sub akun →
    </Link>

    {/* Marwah's written steps ended with "konfirmasi ke kak Marwah lewat
        WhatsApp". Dropped on her and Alfiano's instruction (14 Oct): the next
        screen already confirms it in-app, so a WhatsApp round trip would be a
        second way to say the same thing — and the slower one. */}
    <p className="mt-4 text-center text-xs leading-relaxed text-muted-foreground">
      Tidak perlu konfirmasi lewat WhatsApp — langkah berikutnya sudah mengabari tim kami.
    </p>
  </OnboardingLayout>
);
