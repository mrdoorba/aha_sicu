/**
 * Fake data for the onboarding UX preview.
 *
 * Everything here is invented. The shapes deliberately mirror what the real
 * endpoints will return in Phase A/D, so swapping this module for API calls is
 * a change of source, not a change of screens.
 */
import { addWorkdays } from '../lib/workdays';

export type VoucherStatus = 'none' | 'pending' | 'active' | 'claimed' | 'expired';

export interface PreviewVoucher {
  brandName: string;
  marketplace: 'ID' | 'TH';
  /** Null until Ka Marwah activates it — a pending voucher has no code to copy. */
  code: string | null;
  status: VoucherStatus;
  expiresAt: Date | null;
  claimedAt: Date | null;
  /** Which of the 6 onboarding steps the brand has reached, when claimed. */
  step: number | null;
}

/** The brand a preview visitor "is" once they claim the voucher. */
export const PREVIEW_BRAND = {
  name: 'Covermake',
  marketplace: 'ID' as const,
  slug: 'covermakeofficial',
  storeUrl: 'shopee.co.id/covermakeofficial',
  code: 'K7M4PXQ9TRJ2',
  email: 'budi@covermake.co.id',
  /** Derived from the voucher's brand — the brand never types this. */
  subAccountEmail: 'aha+covermake@ahacommerce.net',
  subAccountPassword: 'caberawit123!',
  priceIdr: 3_000_000,
};

export function previewDeadline(): Date {
  return addWorkdays(new Date(), 7);
}

export const VOUCHER_CODE_LENGTH = 12;

/**
 * What the claim page can learn about a typed code.
 *
 * `idle` and `typing` are deliberately separate from `unknown`: shouting
 * "kode tidak ditemukan" at someone who has entered four characters is wrong,
 * so nothing is judged until a full code is present.
 */
export type VoucherLookup =
  | { state: 'idle' }
  | { state: 'typing'; remaining: number }
  | { state: 'unknown' }
  | { state: 'expired'; expiredOn: Date }
  | { state: 'claimed'; claimedOn: Date }
  | { state: 'valid'; brand: typeof PREVIEW_BRAND; expiresAt: Date };

/** Codes that let every branch be reached by hand in the preview. */
export const PREVIEW_TEST_CODES = {
  valid: PREVIEW_BRAND.code,
  expired: 'EXPIRED00001',
  claimed: 'CLAIMED00001',
} as const;

export function lookupVoucher(raw: string): VoucherLookup {
  const code = raw.trim().toUpperCase();

  if (code.length === 0) return { state: 'idle' };
  if (code.length < VOUCHER_CODE_LENGTH) {
    return { state: 'typing', remaining: VOUCHER_CODE_LENGTH - code.length };
  }

  if (code === PREVIEW_TEST_CODES.valid) {
    return { state: 'valid', brand: PREVIEW_BRAND, expiresAt: previewDeadline() };
  }
  if (code === PREVIEW_TEST_CODES.expired) {
    return { state: 'expired', expiredOn: new Date(Date.now() - 4 * 86_400_000) };
  }
  if (code === PREVIEW_TEST_CODES.claimed) {
    return { state: 'claimed', claimedOn: new Date(Date.now() - 9 * 86_400_000) };
  }
  return { state: 'unknown' };
}

/** Where a brand without a voucher is sent. */
export const AHA_WHATSAPP = 'https://wa.me/6281234567890';

/** Rows for the Brands table, one per voucher state so every branch is visible. */
export function previewVouchers(): PreviewVoucher[] {
  const now = new Date();
  const past = new Date(now.getTime() - 3 * 86_400_000);
  return [
    {
      brandName: 'Covermake',
      marketplace: 'ID',
      code: 'K7M4PXQ9TRJ2',
      status: 'active',
      expiresAt: addWorkdays(now, 5),
      claimedAt: null,
      step: null,
    },
    {
      brandName: 'Lem Castol',
      marketplace: 'ID',
      code: null,
      status: 'pending',
      expiresAt: null,
      claimedAt: null,
      step: null,
    },
    {
      brandName: 'Monkefit',
      marketplace: 'ID',
      code: 'B4T8NRW6YKD3',
      status: 'claimed',
      expiresAt: null,
      claimedAt: past,
      step: 4,
    },
    {
      brandName: 'คุณแม่จู้',
      marketplace: 'TH',
      code: 'Z9H2VMC5XQF7',
      status: 'expired',
      expiresAt: past,
      claimedAt: null,
      step: null,
    },
    {
      brandName: 'สุขภาพโอสถ',
      marketplace: 'TH',
      code: null,
      status: 'none',
      expiresAt: null,
      claimedAt: null,
      step: null,
    },
  ];
}

export interface PreviewAxis {
  label: string;
  /** Health, 0–100: higher is always better. Never the 100-point SICU score. */
  value: number;
}

export const PREVIEW_AXES: PreviewAxis[] = [
  { label: 'Operasional', value: 100 },
  { label: 'Bisnis', value: 71 },
  { label: 'Pengunjung', value: 58 },
  { label: 'Promo', value: 45 },
  { label: 'Produk', value: 71 },
  { label: 'Iklan', value: 100 },
  { label: 'Campaign', value: 62 },
  { label: 'Stok', value: 80 },
];

export const PREVIEW_RECOMMENDATIONS = [
  {
    severity: 'high' as const,
    title: 'Aktifkan 5 alat promosi yang belum dipakai',
    body: 'Baru 6 dari 11 alat Seller Centre yang digunakan. Paket Diskon dan Program Afiliasi paling berdampak di kategori Anda.',
  },
  {
    severity: 'high' as const,
    title: 'Tingkatkan pengunjung yang kembali',
    body: 'Saat ini 13% — benchmark sehat di atas 23%. Chat Broadcast ke pembeli lama adalah cara tercepat.',
  },
  {
    severity: 'medium' as const,
    title: 'Tambah jumlah produk aktif',
    body: '25 produk, benchmark 35. Varian dari SKU terlaris adalah tambahan termurah.',
  },
];
