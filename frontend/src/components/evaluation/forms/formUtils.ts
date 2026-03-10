import type { ManualData, SectionProgress } from './types';
import { GENERIC_LABELS, INDO_MONTHS } from './fields';

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
    labels.push(`${INDO_MONTHS[monthIndex]} ${year + yearOffset}`);
  }
  return labels;
}

// ── IDR formatting utilities ───────────────────────────────────────────────

export function formatIDR(value: number | null | undefined): string {
  if (value == null || isNaN(value)) return '';
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(Math.round(value));
}

export function parseIDR(formatted: string): number | null {
  const stripped = formatted.replace(/\./g, '').replace(/,/g, '').trim();
  if (stripped === '') return null;
  const num = Number(stripped);
  return isNaN(num) ? null : num;
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
