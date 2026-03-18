// ── ManualData TypeScript types matching JSONB schema ──────────────────────

export interface OperationalData {
  unfulfilledOrderRate: number | null;
  lateShipmentRate: number | null;
  preparationTime: number | null;
  chatResponseRate: number | null;
  overallRating: number | null;
}

export interface BusinessData {
  salesStartMonth: string | null;
  salesMonth0: number | null;
  salesMonth1: number | null;
  salesMonth2: number | null;
  salesMonth3: number | null;
  salesMonth4: number | null;
  salesMonth5: number | null;
  conversionRate: number | null;
}

export interface VisitorsData {
  totalVisitors: number | null;
  totalFollowers: number | null;
  returningVisitors: number | null;
}

export interface PromoToolsData {
  promoToko: number | null;
  paketDiskon: number | null;
  komboHemat: number | null;
  flashSale: number | null;
  voucher: number | null;
  shopeeLive: number | null;
  gameToko: number | null;
  brandMembership: number | null;
  gratisOngkir: number | null;
  chatBroadcast: number | null;
  programAfiliasi: number | null;
}

export interface ProductsData {
  productCount: number | null;
  storeStatus: string | null;
}

export interface AdsData {
  adSales: number | null;
  adCost: number | null;
}

export interface CampaignData {
  nominatedSessions: number | null;
  availableSessions: number | null;
}

export interface CompetitionProduct {
  productName: string | null;
  sellingPrice: number | null;
  keyword: string | null;
  link: string | null;
  marketPrice: number | null;
}

export interface CompetitionData {
  product1: CompetitionProduct;
  product2: CompetitionProduct;
  product3: CompetitionProduct;
}

export interface ManualData {
  operational: OperationalData;
  business: BusinessData;
  visitors: VisitorsData;
  promoTools: PromoToolsData;
  products: ProductsData;
  ads: AdsData;
  campaign: CampaignData;
  competition: CompetitionData;
}

// ── Field definition types ─────────────────────────────────────────────────

export type InputType = 'number' | 'currency' | 'text' | 'select';

export interface FieldDefinition {
  key: string;
  label: string;
  labelKey?: string;
  inputType: InputType;
  unit?: string;
  unitKey?: string;
  benchmark?: string;
  benchmarkKey?: string;
  threshold?: number;
  link?: string;
}

export interface SelectOption {
  value: string;
  label: string;
}

export interface CategoryDefinition {
  key: string;
  displayName: string;
  displayNameKey?: string;
  fields: FieldDefinition[];
}

export interface SectionProgress {
  filled: number;
  total: number;
}
