import type { ManualData, SectionProgress } from './types';
import { GENERIC_LABELS, MONTHS } from './fields';

// ── Month label generation ─────────────────────────────────────────────────

export function generateMonthLabels(startMonth: string | null): string[] {
  if (!startMonth) return [...GENERIC_LABELS];

  if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(startMonth)) return [...GENERIC_LABELS];

  const [yearStr, monthStr] = startMonth.split('-');
  const year = parseInt(yearStr, 10);
  const month = parseInt(monthStr, 10);

  const labels: string[] = [];
  for (let i = 0; i < 6; i++) {
    const monthIndex = ((month - 1 - i) % 12 + 12) % 12;
    const yearOffset = Math.floor((month - 1 - i) / 12);
    labels.push(`${MONTHS[monthIndex]} ${year + yearOffset}`);
  }
  return labels;
}

// ── Currency utilities ──────────────────────────────────────────────────────

/**
 * Map marketplace code to currency code.
 * 'TH' → 'THB', 'ID' → 'IDR' (default). Unknown codes are uppercased as-is.
 */
export function getCurrencyCode(marketplace?: string): string {
  if (!marketplace) return 'IDR';
  const upper = marketplace.toUpperCase();
  switch (upper) {
    case 'TH':
      return 'THB';
    case 'ID':
      return 'IDR';
    default:
      return upper;
  }
}

/**
 * Format a numeric value as a comma-separated currency string.
 * Both IDR and THB use identical number formatting (no decimals, comma thousands).
 * The marketplace parameter is accepted for future use but does not change formatting today.
 */
export function formatCurrency(value: number | null | undefined, _marketplace?: string): string {
  if (value == null || isNaN(value)) return '';
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Math.round(value));
}

/**
 * Parse a formatted currency string back to a number.
 * Strips dots and commas, returns null for empty/non-numeric input.
 * The marketplace parameter is accepted for future use but does not change parsing today.
 */
export function parseCurrency(formatted: string, _marketplace?: string): number | null {
  const stripped = formatted.replace(/\./g, '').replace(/,/g, '').trim();
  if (stripped === '') return null;
  const num = Number(stripped);
  return isNaN(num) ? null : num;
}

/** @deprecated Use `formatCurrency` instead. Kept for backward compatibility. */
export function formatIDR(value: number | null | undefined): string {
  return formatCurrency(value);
}

/** @deprecated Use `parseCurrency` instead. Kept for backward compatibility. */
export function parseIDR(formatted: string): number | null {
  return parseCurrency(formatted);
}

// ── Section progress computation ──────────────────────────────────────────

function countFilledInFlat(obj: object): { filled: number; total: number } {
  const values = Object.values(obj);
  return {
    total: values.length,
    filled: values.filter((v) => v != null && v !== '').length,
  };
}

export function computeSectionProgress(data: ManualData): Record<string, SectionProgress> {
  const s1 = countFilledInFlat(data.operational);

  const { salesStartMonth, ...bizData } = data.business;
  void salesStartMonth;
  const biz = countFilledInFlat(bizData);
  const visitors = countFilledInFlat(data.visitors);
  const s2 = {
    filled: biz.filled + visitors.filled,
    total: biz.total + visitors.total,
  };

  const promo = countFilledInFlat(data.promoTools);
  const products = countFilledInFlat(data.products);
  const s3 = {
    filled: promo.filled + products.filled,
    total: promo.total + products.total,
  };

  // Section 4 is file upload — no manual fields

  const ads = countFilledInFlat(data.ads);
  const campaign = countFilledInFlat(data.campaign);
  const compFilled = [data.competition.product1, data.competition.product2, data.competition.product3]
    .reduce(
      (acc, p) =>
        acc +
        (p.productName != null && p.productName !== '' ? 1 : 0) +
        (p.sellingPrice != null ? 1 : 0) +
        (p.keyword != null && p.keyword !== '' ? 1 : 0) +
        (p.link != null && p.link !== '' ? 1 : 0) +
        (p.marketPrice != null ? 1 : 0),
      0,
    );
  const s5 = {
    filled: ads.filled + campaign.filled + compFilled,
    total: ads.total + campaign.total + 15, // 3 products × 5 fields
  };

  return {
    'section-1': s1,
    'section-2': s2,
    'section-3': s3,
    'section-5': s5,
  };
}
