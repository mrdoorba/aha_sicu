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
  { key: 'conversionRate', label: 'Conversion Rate', inputType: 'number', unit: '%', benchmark: '>3%', benchmarkFashion: '>2%' },
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

// ── Category definitions (maps categories to their fields) ─────────────────

export const MANUAL_DATA_FIELDS: CategoryDefinition[] = [
  { key: 'operational', displayName: 'Operational', fields: OPERATIONAL_FIELDS },
  { key: 'business', displayName: 'Business', fields: BUSINESS_FIELDS },
  { key: 'content', displayName: 'Content', fields: CONTENT_FIELDS },
  { key: 'visitors', displayName: 'Visitors', fields: VISITORS_FIELDS },
  { key: 'promoTools', displayName: 'Promo Tools', fields: PROMO_TOOLS_FIELDS },
  { key: 'products', displayName: 'Products/Status', fields: PRODUCTS_FIELDS },
  { key: 'ads', displayName: 'Ads', fields: ADS_FIELDS },
  { key: 'campaign', displayName: 'Campaign', fields: CAMPAIGN_FIELDS },
];

// ── IDR formatting utilities ───────────────────────────────────────────────

export function formatIDR(value: number | null | undefined): string {
  if (value == null || isNaN(value)) return '';
  return Math.round(value).toLocaleString('id-ID');
}

export function parseIDR(formatted: string): number | null {
  const stripped = formatted.replace(/\./g, '').replace(/,/g, '').trim();
  if (stripped === '') return null;
  const num = Number(stripped);
  return isNaN(num) ? null : num;
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
