import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '../../components/ui/table';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { VoucherCell } from '../../components/brands/VoucherCell';
import { previewVouchers } from '../../mocks/onboarding';

const BRAND_SCREENS = [
  { to: '/preview/daftar', label: 'Klaim voucher', note: 'publik · register gradient' },
  { to: '/preview/onboarding/biaya', label: '1 · Diskon 100%', note: 'animasi 3 jt → Rp 0' },
  { to: '/preview/onboarding/nda', label: '2 · Form + NDA', note: 'tanda tangan otomatis' },
  { to: '/preview/onboarding/tutorial', label: '3 · Tutorial sub akun', note: 'screenshot menyusul' },
  { to: '/preview/onboarding/sub-akun', label: '4 · Kirim sub akun', note: 'form cadangan' },
  { to: '/preview/onboarding/proses', label: '5 · Menunggu', note: 'checklist, bukan spinner' },
  { to: '/preview/onboarding/hasil', label: '6 · Hasil SICU', note: 'radar kesehatan' },
];

export const PreviewIndexPage = () => {
  const vouchers = previewVouchers();

  return (
    <div className="min-h-screen bg-background px-4 py-10 sm:px-8">
      <div className="mx-auto max-w-5xl">
        <Badge className="mb-4 bg-gold text-deep-navy hover:bg-gold">PRATINJAU · DATA PALSU</Badge>
        <h1 className="mb-2 text-2xl font-extrabold tracking-tight text-foreground">
          SICU — alur voucher &amp; onboarding
        </h1>
        <p className="mb-9 max-w-[70ch] text-sm leading-relaxed text-muted-foreground">
          Semua data di halaman-halaman ini palsu dan tidak ada panggilan ke backend. Tujuannya
          satu: merasakan UX sebelum apa pun dibangun betulan. Halaman ini tidak muncul di
          produksi.
        </p>

        <h2 className="mb-3 text-base font-extrabold text-foreground">Sisi brand</h2>
        <ul className="mb-10 grid gap-2.5 sm:grid-cols-2">
          {BRAND_SCREENS.map((screen) => (
            <li key={screen.to}>
              <Link
                to={screen.to}
                className="flex items-center justify-between gap-3 rounded-xl border border-border bg-card px-4 py-3.5 transition-colors hover:border-primary hover:bg-accent/20"
              >
                <span className="min-w-0">
                  <span className="block text-sm font-bold text-foreground">{screen.label}</span>
                  <span className="block text-xs text-muted-foreground">{screen.note}</span>
                </span>
                <ArrowRight className="size-4 shrink-0 text-primary" aria-hidden="true" />
              </Link>
            </li>
          ))}
        </ul>

        <h2 className="mb-1 text-base font-extrabold text-foreground">
          Sisi internal — kolom Voucher di tab Brands
        </h2>
        <p className="mb-4 text-sm text-muted-foreground">
          Kolom <strong className="text-foreground">Info Utama</strong> dihapus; kolom Voucher
          menggantikannya. Lima baris di bawah menunjukkan setiap keadaan sekaligus.
        </p>

        <div className="overflow-hidden rounded-2xl border border-border bg-card">
          <div className="overflow-x-auto">
            <Table aria-label="Pratinjau kolom voucher">
              <TableHeader>
                <TableRow>
                  <TableHead className="text-xs uppercase">Brand</TableHead>
                  <TableHead className="text-xs uppercase">1st Meeting</TableHead>
                  <TableHead className="text-xs uppercase">Voucher SICU</TableHead>
                  <TableHead className="text-xs uppercase">Aksi</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {vouchers.map((voucher) => (
                  <TableRow key={voucher.brandName}>
                    <TableCell className="font-medium">
                      <span className="me-2">{voucher.marketplace === 'TH' ? '🇹🇭' : '🇮🇩'}</span>
                      {voucher.brandName}
                    </TableCell>
                    <TableCell>
                      {voucher.status === 'none' ? (
                        <span className="text-sm text-muted-foreground">— Tidak tersedia</span>
                      ) : (
                        <Badge className="bg-primary text-primary-foreground hover:bg-primary">
                          Tersedia
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <VoucherCell voucher={voucher} />
                    </TableCell>
                    <TableCell>
                      <Button size="sm">Evaluasi</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </div>
    </div>
  );
};
