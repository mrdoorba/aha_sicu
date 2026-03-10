import type { ManualData } from '../components/evaluation/forms/formConfig';
import { EMPTY_MANUAL_DATA } from '../components/evaluation/forms/formConfig';

/** Deep merge initialData into EMPTY_MANUAL_DATA to preserve null defaults for missing fields */
export function buildManualData(initialData: Record<string, unknown> | null): ManualData {
  const raw = (initialData ?? {}) as Partial<ManualData>;
  return {
    operational: { ...EMPTY_MANUAL_DATA.operational, ...raw.operational },
    business: { ...EMPTY_MANUAL_DATA.business, ...raw.business },
    visitors: { ...EMPTY_MANUAL_DATA.visitors, ...raw.visitors },
    promoTools: { ...EMPTY_MANUAL_DATA.promoTools, ...raw.promoTools },
    products: { ...EMPTY_MANUAL_DATA.products, ...raw.products },
    ads: { ...EMPTY_MANUAL_DATA.ads, ...raw.ads },
    campaign: { ...EMPTY_MANUAL_DATA.campaign, ...raw.campaign },
    competition: {
      product1: { ...EMPTY_MANUAL_DATA.competition.product1, ...raw.competition?.product1 },
      product2: { ...EMPTY_MANUAL_DATA.competition.product2, ...raw.competition?.product2 },
      product3: { ...EMPTY_MANUAL_DATA.competition.product3, ...raw.competition?.product3 },
    },
  };
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
