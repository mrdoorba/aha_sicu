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
  /** Shopee's sub-account form asks for a login ID separately from the email. */
  subAccountLoginId: 'aha789',
  subAccountMemberName: 'AHA',
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

/** Where Shopee's sub-account form lives. */
export const SHOPEE_SUBACCOUNT_URL = 'https://subaccount.shopee.com/member';

/**
 * The permissions the sub account must carry, exactly as Shopee labels them.
 *
 * Supplied by Marwah on 14 Oct 2026. Nesting mirrors Shopee's own form, so a
 * brand can tick down the list without translating our wording into theirs —
 * and a missing permission silently removes a whole SICU category, so the list
 * is reproduced rather than summarised.
 */
export interface SubAccountRole {
  label: string;
  children?: string[];
}

export const SUBACCOUNT_ROLES: SubAccountRole[] = [
  { label: 'Akses ke Daftar Pesanan', children: ['Akses ke Rincian Pesanan'] },
  { label: 'Akses ke Iklanku', children: ['Ekspor File'] },
  { label: 'Akses ke Promo Toko' },
  { label: 'Akses ke Promo Shopee' },
  { label: 'Akses ke Afiliasi' },
  { label: 'Lihat Pusat Promosi' },
  { label: 'Akses ke Brand Membership' },
  { label: 'Akses ke Data Toko Saya', children: ['Akses ke Kesehatan Toko'] },
  { label: "Akses ke 'Produk Saya'", children: ['Edit secara Massal', 'Download Masal'] },
];

/** Marwah's walkthrough, one per language. */
export const SUBACCOUNT_VIDEOS = [
  { code: 'id' as const, flag: '🇮🇩', label: 'Bahasa Indonesia', youtubeId: 'W9AC-ZiZc0Y' },
  { code: 'en' as const, flag: '🇬🇧', label: 'English', youtubeId: '3XdmtrBfp44' },
];
