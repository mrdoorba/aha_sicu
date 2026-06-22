import type { ManualData } from '../components/evaluation/forms/formConfig';
import { EMPTY_MANUAL_DATA } from '../components/evaluation/forms/formConfig';
import { isRecord } from '../lib/typeGuards';

/** Deep merge initialData into EMPTY_MANUAL_DATA to preserve null defaults for missing fields */
export function buildManualData(initialData: Record<string, unknown> | null): ManualData {
  const source = initialData ?? {};
  // Safely extract each category — only spread if it's actually an object
  const raw = {
    operational: isRecord(source.operational) ? source.operational : undefined,
    business: isRecord(source.business) ? source.business : undefined,
    visitors: isRecord(source.visitors) ? source.visitors : undefined,
    promoTools: isRecord(source.promoTools) ? source.promoTools : undefined,
    products: isRecord(source.products) ? source.products : undefined,
    ads: isRecord(source.ads) ? source.ads : undefined,
    campaign: isRecord(source.campaign) ? source.campaign : undefined,
    competition: isRecord(source.competition) ? source.competition : undefined,
  };
  const comp = raw.competition;
  return {
    operational: { ...EMPTY_MANUAL_DATA.operational, ...raw.operational },
    business: { ...EMPTY_MANUAL_DATA.business, ...raw.business },
    visitors: { ...EMPTY_MANUAL_DATA.visitors, ...raw.visitors },
    promoTools: { ...EMPTY_MANUAL_DATA.promoTools, ...raw.promoTools },
    products: { ...EMPTY_MANUAL_DATA.products, ...raw.products },
    ads: { ...EMPTY_MANUAL_DATA.ads, ...raw.ads },
    campaign: { ...EMPTY_MANUAL_DATA.campaign, ...raw.campaign },
    competition: {
      product1: {
        ...EMPTY_MANUAL_DATA.competition.product1,
        ...(isRecord(comp?.product1) ? comp.product1 : undefined),
      },
      product2: {
        ...EMPTY_MANUAL_DATA.competition.product2,
        ...(isRecord(comp?.product2) ? comp.product2 : undefined),
      },
      product3: {
        ...EMPTY_MANUAL_DATA.competition.product3,
        ...(isRecord(comp?.product3) ? comp.product3 : undefined),
      },
    },
  };
}

// ── Period-scoped swap (session-only) ──────────────────────────────────────
// Everything below the period selector is "data for that period" EXCEPT
// competition (and marketplace/category, which live outside ManualData).
//
// Two memory models, because the sections differ in kind:
//  • The monthly sales grid is a rolling 6-month window. Adjacent periods
//    overlap (Mei's window holds Apr; Apr's window also holds Apr), so each
//    figure is keyed by its CALENDAR MONTH and carries across periods.
//  • Visitors/operational/promo/products/ads/campaign are single values for
//    the period, keyed by the start month and dropped/remembered per period.
export type PeriodScopedData = Pick<
  ManualData,
  'operational' | 'business' | 'visitors' | 'promoTools' | 'products' | 'ads' | 'campaign'
>;

type SectionData = Pick<
  ManualData,
  'operational' | 'visitors' | 'promoTools' | 'products' | 'ads' | 'campaign'
>;

export interface PeriodMemory {
  /** Non-business sections, keyed by period (start month). */
  sections: Map<string, SectionData>;
  /** Monthly sales, keyed by calendar month "YYYY-MM" — overlaps carry across periods. */
  salesByMonth: Map<string, number | null>;
  /** Conversion rate, keyed by period (it describes the start month). */
  conversionByPeriod: Map<string, number | null>;
}

export function createPeriodMemory(): PeriodMemory {
  return { sections: new Map(), salesByMonth: new Map(), conversionByPeriod: new Map() };
}

const SALES_SLOTS = ['salesMonth0', 'salesMonth1', 'salesMonth2', 'salesMonth3', 'salesMonth4', 'salesMonth5'] as const;

/** Calendar-month key for slot `i` of a window starting at `startMonth` (i months back). */
function monthKeyForSlot(startMonth: string, slotIndex: number): string {
  const [year, month] = startMonth.split('-').map(Number);
  const d = new Date(year, month - 1 - slotIndex, 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
}

function pickSections(d: ManualData): SectionData {
  return {
    operational: d.operational,
    visitors: d.visitors,
    promoTools: d.promoTools,
    products: d.products,
    ads: d.ads,
    campaign: d.campaign,
  };
}

function blankSections(): SectionData {
  const e = EMPTY_MANUAL_DATA;
  return {
    operational: { ...e.operational },
    visitors: { ...e.visitors },
    promoTools: { ...e.promoTools },
    products: { ...e.products },
    ads: { ...e.ads },
    campaign: { ...e.campaign },
  };
}

/** Rebuild the business section for `startMonth` from calendar-month + per-period memory. */
function buildBusiness(startMonth: string | null, mem: PeriodMemory): ManualData['business'] {
  const business = { ...EMPTY_MANUAL_DATA.business, salesStartMonth: startMonth };
  if (!startMonth) return business;
  business.conversionRate = mem.conversionByPeriod.get(startMonth) ?? null;
  SALES_SLOTS.forEach((slot, i) => {
    business[slot] = mem.salesByMonth.get(monthKeyForSlot(startMonth, i)) ?? null;
  });
  return business;
}

/**
 * Session-only period swap. Stashes the leaving period's data into `mem`, then
 * rebuilds the target period: non-business sections from per-period memory
 * (blank if unvisited), the sales grid from calendar-month memory so overlapping
 * months refill automatically. Competition is left to the caller (not period-scoped).
 * Mutates `mem`, the in-memory session store.
 * ponytail: session-only — `mem` lives in memory, so a reload shows only the
 * last-saved period. Upgrade path: persist data keyed by period in the backend.
 */
export function applyPeriodSwap(
  current: ManualData,
  newPeriod: string | null,
  mem: PeriodMemory,
): PeriodScopedData {
  const oldPeriod = current.business.salesStartMonth;

  // No-op selection: return current data untouched (don't wipe from empty memory).
  if (oldPeriod === newPeriod) {
    return { ...pickSections(current), business: current.business };
  }

  if (oldPeriod) {
    mem.sections.set(oldPeriod, pickSections(current));
    mem.conversionByPeriod.set(oldPeriod, current.business.conversionRate);
    SALES_SLOTS.forEach((slot, i) => {
      mem.salesByMonth.set(monthKeyForSlot(oldPeriod, i), current.business[slot]);
    });
  }

  const sections = (newPeriod && mem.sections.has(newPeriod))
    ? mem.sections.get(newPeriod)!
    : blankSections();
  return { ...sections, business: buildBusiness(newPeriod, mem) };
}

/** Merge local overrides into base server data */
export function mergeWithOverrides(base: ManualData, overrides: Partial<ManualData>): ManualData {
  return {
    operational: { ...base.operational, ...overrides.operational },
    business: { ...base.business, ...overrides.business },
    visitors: { ...base.visitors, ...overrides.visitors },
    promoTools: { ...base.promoTools, ...overrides.promoTools },
    products: { ...base.products, ...overrides.products },
    ads: { ...base.ads, ...overrides.ads },
    campaign: { ...base.campaign, ...overrides.campaign },
    competition: {
      product1: { ...base.competition.product1, ...overrides.competition?.product1 },
      product2: { ...base.competition.product2, ...overrides.competition?.product2 },
      product3: { ...base.competition.product3, ...overrides.competition?.product3 },
    },
  };
}
