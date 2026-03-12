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
