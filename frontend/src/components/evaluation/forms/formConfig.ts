// ── ManualData TypeScript types matching JSONB schema ──────────────────────

export interface OperationalData {
  unfulfilledOrderRate: number | null;
  lateShipmentRate: number | null;
  preparationTime: number | null;
  chatResponseRate: number | null;
  overallRating: number | null;
}

export interface BusinessData {
  salesMonth0: number | null;
  salesMonth1: number | null;
  salesMonth2: number | null;
  salesMonth3: number | null;
  salesMonth4: number | null;
  salesMonth5: number | null;
  conversionRate: number | null;
}

export interface ContentData {
  needsImprovement: number | null;
  goodQuality: number | null;
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
  keyword: string | null;
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
  content: ContentData;
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
  inputType: InputType;
  unit?: string;
  benchmark?: string;
  benchmarkFashion?: string;
}

export interface SelectOption {
  value: string;
  label: string;
}

export interface CategoryDefinition {
  key: string;
  displayName: string;
  fields: FieldDefinition[];
}

// ── Store Status options ───────────────────────────────────────────────────

export const STORE_STATUS_OPTIONS: SelectOption[] = [
  { value: 'Shopee Mall', label: 'Shopee Mall' },
  { value: 'Star+', label: 'Star+' },
  { value: 'Star', label: 'Star' },
  { value: 'Regular', label: 'Regular' },
];

// ── Field definitions per category ─────────────────────────────────────────

export const OPERATIONAL_FIELDS: FieldDefinition[] = [
  { key: 'unfulfilledOrderRate', label: 'Pesanan Tidak Terselesaikan', inputType: 'number', unit: '%', benchmark: '<1%' },
  { key: 'lateShipmentRate', label: 'Keterlambatan', inputType: 'number', unit: '%', benchmark: '<1%' },
  { key: 'preparationTime', label: 'Masa Pengemasan', inputType: 'number', unit: 'hari', benchmark: '<1' },
  { key: 'chatResponseRate', label: 'Chat Dibalas', inputType: 'number', unit: '%', benchmark: '>95%' },
  { key: 'overallRating', label: 'Penilaian', inputType: 'number', unit: 'rating', benchmark: '>4.7' },
];

export const BUSINESS_FIELDS: FieldDefinition[] = [
  { key: 'salesMonth0', label: 'Penjualan Bulan Ini', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth1', label: 'Penjualan Bulan -1', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth2', label: 'Penjualan Bulan -2', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth3', label: 'Penjualan Bulan -3', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth4', label: 'Penjualan Bulan -4', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth5', label: 'Penjualan Bulan -5', inputType: 'currency', unit: 'IDR' },
  { key: 'conversionRate', label: 'Tingkat Konversi', inputType: 'number', unit: '%', benchmark: '>3%', benchmarkFashion: '>2%' },
];

export const CONTENT_FIELDS: FieldDefinition[] = [
  { key: 'needsImprovement', label: 'Perlu Ditingkatkan', inputType: 'number', unit: 'count' },
  { key: 'goodQuality', label: 'Kualitas Baik', inputType: 'number', unit: 'count' },
];

export const VISITORS_FIELDS: FieldDefinition[] = [
  { key: 'totalVisitors', label: 'Total Pengunjung', inputType: 'number', unit: 'count' },
  { key: 'returningVisitors', label: 'Pengunjung Lama', inputType: 'number', unit: 'count' },
  { key: 'totalFollowers', label: 'Total Pengikut', inputType: 'number', unit: 'count', benchmark: '>50,000' },
];

export const PROMO_TOOLS_FIELDS: FieldDefinition[] = [
  { key: 'promoToko', label: 'Promo Toko', inputType: 'currency', unit: 'IDR', benchmark: '>8% dari penjualan' },
  { key: 'paketDiskon', label: 'Paket Diskon', inputType: 'currency', unit: 'IDR', benchmark: '>16% dari penjualan' },
  { key: 'komboHemat', label: 'Kombo Hemat', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan' },
  { key: 'flashSale', label: 'Flash Sale Toko Saya', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan' },
  { key: 'voucher', label: 'Voucher', inputType: 'currency', unit: 'IDR', benchmark: '>84% dari penjualan' },
  { key: 'shopeeLive', label: 'Shopee Live', inputType: 'currency', unit: 'IDR', benchmark: '>15% dari penjualan' },
  { key: 'gameToko', label: 'Game Toko', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan' },
  { key: 'brandMembership', label: 'Brand Membership', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan' },
  { key: 'gratisOngkir', label: 'Gratis Ongkir XTRA', inputType: 'currency', unit: 'IDR', benchmark: '>0' },
  { key: 'chatBroadcast', label: 'Chat Broadcast', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan' },
  { key: 'programAfiliasi', label: 'Program Afiliasi', inputType: 'currency', unit: 'IDR', benchmark: '>18% dari penjualan' },
];

export const PRODUCTS_FIELDS: FieldDefinition[] = [
  { key: 'productCount', label: 'Jumlah Produk', inputType: 'number', unit: 'count', benchmark: '>=35' },
  { key: 'storeStatus', label: 'Status Toko', inputType: 'select', benchmark: 'Shopee Mall' },
];

export const ADS_FIELDS: FieldDefinition[] = [
  { key: 'adSales', label: 'Penjualan Iklan', inputType: 'currency', unit: 'IDR' },
  { key: 'adCost', label: 'Biaya Iklan', inputType: 'currency', unit: 'IDR' },
];

export const CAMPAIGN_FIELDS: FieldDefinition[] = [
  { key: 'nominatedSessions', label: 'Sesi Dinominasikan', inputType: 'number', unit: 'count' },
  { key: 'availableSessions', label: 'Sesi Tersedia', inputType: 'number', unit: 'count' },
];

export const COMPETITION_FIELDS: FieldDefinition[] = [
  { key: 'product1.keyword', label: 'Produk Kompetitor 1 — Keyword', inputType: 'text' },
  { key: 'product1.marketPrice', label: 'Produk Kompetitor 1 — Harga Pasar', inputType: 'currency', unit: 'IDR' },
  { key: 'product2.keyword', label: 'Produk Kompetitor 2 — Keyword', inputType: 'text' },
  { key: 'product2.marketPrice', label: 'Produk Kompetitor 2 — Harga Pasar', inputType: 'currency', unit: 'IDR' },
  { key: 'product3.keyword', label: 'Produk Kompetitor 3 — Keyword', inputType: 'text' },
  { key: 'product3.marketPrice', label: 'Produk Kompetitor 3 — Harga Pasar', inputType: 'currency', unit: 'IDR' },
];

// ── Category definitions (maps categories to their fields) ─────────────────

export const MANUAL_DATA_FIELDS: CategoryDefinition[] = [
  { key: 'operational', displayName: 'Operasional', fields: OPERATIONAL_FIELDS },
  { key: 'business', displayName: 'Bisnis', fields: BUSINESS_FIELDS },
  { key: 'content', displayName: 'Konten', fields: CONTENT_FIELDS },
  { key: 'visitors', displayName: 'Pengunjung', fields: VISITORS_FIELDS },
  { key: 'promoTools', displayName: 'Alat Promo', fields: PROMO_TOOLS_FIELDS },
  { key: 'products', displayName: 'Produk/Status', fields: PRODUCTS_FIELDS },
  { key: 'ads', displayName: 'Iklan', fields: ADS_FIELDS },
  { key: 'campaign', displayName: 'Kampanye', fields: CAMPAIGN_FIELDS },
  { key: 'competition', displayName: 'Kompetisi', fields: COMPETITION_FIELDS },
];

// ── IDR formatting utilities ───────────────────────────────────────────────

export function formatIDR(value: number | null | undefined): string {
  if (value == null || isNaN(value)) return '';
  return String(Math.round(value));
}

export function parseIDR(formatted: string): number | null {
  const stripped = formatted.replace(/\./g, '').replace(/,/g, '').trim();
  if (stripped === '') return null;
  const num = Number(stripped);
  return isNaN(num) ? null : num;
}

// ── Section progress computation ──────────────────────────────────────────

export interface SectionProgress {
  filled: number;
  total: number;
}

function countFilledInFlat(obj: object): { filled: number; total: number } {
  const values = Object.values(obj);
  return {
    total: values.length,
    filled: values.filter((v) => v != null && v !== '').length,
  };
}

export function computeSectionProgress(data: ManualData): Record<string, SectionProgress> {
  const s1 = countFilledInFlat(data.operational);

  const biz = countFilledInFlat(data.business);
  const content = countFilledInFlat(data.content);
  const visitors = countFilledInFlat(data.visitors);
  const s2 = {
    filled: biz.filled + content.filled + visitors.filled,
    total: biz.total + content.total + visitors.total,
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
        (p.keyword != null && p.keyword !== '' ? 1 : 0) +
        (p.marketPrice != null ? 1 : 0),
      0,
    );
  const s5 = {
    filled: ads.filled + campaign.filled + compFilled,
    total: ads.total + campaign.total + 6, // 3 products × 2 fields
  };

  return {
    'section-1': s1,
    'section-2': s2,
    'section-3': s3,
    'section-5': s5,
  };
}

// ── Default empty ManualData ───────────────────────────────────────────────

export const EMPTY_MANUAL_DATA: ManualData = {
  operational: {
    unfulfilledOrderRate: null,
    lateShipmentRate: null,
    preparationTime: null,
    chatResponseRate: null,
    overallRating: null,
  },
  business: {
    salesMonth0: null,
    salesMonth1: null,
    salesMonth2: null,
    salesMonth3: null,
    salesMonth4: null,
    salesMonth5: null,
    conversionRate: null,
  },
  content: {
    needsImprovement: null,
    goodQuality: null,
  },
  visitors: {
    totalVisitors: null,
    totalFollowers: null,
    returningVisitors: null,
  },
  promoTools: {
    promoToko: null,
    paketDiskon: null,
    komboHemat: null,
    flashSale: null,
    voucher: null,
    shopeeLive: null,
    gameToko: null,
    brandMembership: null,
    gratisOngkir: null,
    chatBroadcast: null,
    programAfiliasi: null,
  },
  products: {
    productCount: null,
    storeStatus: null,
  },
  ads: {
    adSales: null,
    adCost: null,
  },
  campaign: {
    nominatedSessions: null,
    availableSessions: null,
  },
  competition: {
    product1: { keyword: null, marketPrice: null },
    product2: { keyword: null, marketPrice: null },
    product3: { keyword: null, marketPrice: null },
  },
};
