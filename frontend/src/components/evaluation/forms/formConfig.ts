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
  fields: FieldDefinition[];
}

// ── Store Status options ───────────────────────────────────────────────────

export const STORE_STATUS_OPTIONS: SelectOption[] = [
  { value: 'Shopee Mall', label: 'Shopee Mall' },
  { value: 'Star+', label: 'Star+' },
  { value: 'Star', label: 'Star' },
  { value: 'Regular', label: 'Regular' },
];

// ── Section reference links ────────────────────────────────────────────────

export const SECTION_LINKS = {
  operational: 'https://seller.shopee.co.id/portal/accounthealth/home',
  business: 'https://seller.shopee.co.id/datacenter/dashboard',
  visitors: 'https://seller.shopee.co.id/datacenter/traffic/overview',
  promoTools: 'https://seller.shopee.co.id/datacenter/marketing/tools/discount',
  ads: 'https://seller.shopee.co.id/portal/marketing/pas/assembly?&type=all&group=last-thirty-days',
  campaign: 'https://seller.shopee.co.id/portal/marketing/cmt-product/campaign?tab=AllCampaign',
} as const;

// ── Month label generation ─────────────────────────────────────────────────

const INDO_MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
const GENERIC_LABELS = ["Bulan Ini", "Bulan -1", "Bulan -2", "Bulan -3", "Bulan -4", "Bulan -5"];

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

// ── Field definitions per category ─────────────────────────────────────────

export const OPERATIONAL_FIELDS: FieldDefinition[] = [
  { key: 'unfulfilledOrderRate', label: 'Tingkat Pesanan Tidak Terselesaikan', inputType: 'number', unit: '%', benchmark: '<1%' },
  { key: 'lateShipmentRate', label: 'Tingkat Keterlambatan Pengiriman', inputType: 'number', unit: '%', benchmark: '<1%' },
  { key: 'preparationTime', label: 'Masa Pengemasan', inputType: 'number', unit: 'hari', benchmark: '<1' },
  { key: 'chatResponseRate', label: 'Persentase Chat Dibalas', inputType: 'number', unit: '%', benchmark: '>95%' },
  { key: 'overallRating', label: 'Keseluruhan Penilaian', inputType: 'number', unit: 'rating', benchmark: '>4.7' },
];

export const BUSINESS_FIELDS: FieldDefinition[] = [
  { key: 'salesMonth0', label: 'Penjualan Bulan Ini', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth1', label: 'Penjualan Bulan -1', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth2', label: 'Penjualan Bulan -2', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth3', label: 'Penjualan Bulan -3', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth4', label: 'Penjualan Bulan -4', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth5', label: 'Penjualan Bulan -5', inputType: 'currency', unit: 'IDR' },
  { key: 'conversionRate', label: 'Tingkat Konversi', inputType: 'number', unit: '%', benchmark: '>3%' },
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
  { key: 'promoToko', label: 'Penjualan dari Promo Toko', inputType: 'currency', unit: 'IDR', benchmark: '>8% dari penjualan', threshold: 0.08 },
  { key: 'paketDiskon', label: 'Penjualan dari Paket Diskon', inputType: 'currency', unit: 'IDR', benchmark: '>16% dari penjualan', threshold: 0.16 },
  { key: 'komboHemat', label: 'Penjualan dari Kombo Hemat', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan', threshold: 0.01 },
  { key: 'flashSale', label: 'Penjualan dari Flash Sale Toko Saya', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan', threshold: 0.01 },
  { key: 'voucher', label: 'Penjualan dari Voucher', inputType: 'currency', unit: 'IDR', benchmark: '>84% dari penjualan', threshold: 0.84 },
  { key: 'shopeeLive', label: 'Penjualan dari Shopee Live', inputType: 'currency', unit: 'IDR', benchmark: '>15% dari penjualan', threshold: 0.15 },
  { key: 'gameToko', label: 'Penjualan dari Game Toko', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan', threshold: 0.01 },
  { key: 'brandMembership', label: 'Penjualan dari Brand Membership', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan', threshold: 0.01, link: 'https://seller.shopee.co.id/datacenter/marketing/membership' },
  { key: 'gratisOngkir', label: 'Penjualan dari Gratis Ongkir XTRA', inputType: 'currency', unit: 'IDR', benchmark: '>0', threshold: 0, link: 'https://seller.shopee.co.id/portal/marketing/cmt/campaign?tab=2&sort=9' },
  { key: 'chatBroadcast', label: 'Penjualan dari Chat Broadcast', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan', threshold: 0.01, link: 'https://seller.shopee.co.id/datacenter/services/crm' },
  { key: 'programAfiliasi', label: 'Penjualan dari Program Afiliasi', inputType: 'currency', unit: 'IDR', benchmark: '>18% dari penjualan', threshold: 0.18, link: 'https://seller.shopee.co.id/portal/web-seller-affiliate/dashboard' },
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
  { key: 'product1.productName', label: 'Produk Kompetitor 1 — Nama Produk', inputType: 'text' },
  { key: 'product1.sellingPrice', label: 'Produk Kompetitor 1 — Harga Jual', inputType: 'currency', unit: 'IDR' },
  { key: 'product1.keyword', label: 'Produk Kompetitor 1 — Kata kunci pencarian', inputType: 'text' },
  { key: 'product1.link', label: 'Produk Kompetitor 1 — LINK', inputType: 'text' },
  { key: 'product1.marketPrice', label: 'Produk Kompetitor 1 — Harga rata-rata pasaran', inputType: 'currency', unit: 'IDR' },
  { key: 'product2.productName', label: 'Produk Kompetitor 2 — Nama Produk', inputType: 'text' },
  { key: 'product2.sellingPrice', label: 'Produk Kompetitor 2 — Harga Jual', inputType: 'currency', unit: 'IDR' },
  { key: 'product2.keyword', label: 'Produk Kompetitor 2 — Kata kunci pencarian', inputType: 'text' },
  { key: 'product2.link', label: 'Produk Kompetitor 2 — LINK', inputType: 'text' },
  { key: 'product2.marketPrice', label: 'Produk Kompetitor 2 — Harga rata-rata pasaran', inputType: 'currency', unit: 'IDR' },
  { key: 'product3.productName', label: 'Produk Kompetitor 3 — Nama Produk', inputType: 'text' },
  { key: 'product3.sellingPrice', label: 'Produk Kompetitor 3 — Harga Jual', inputType: 'currency', unit: 'IDR' },
  { key: 'product3.keyword', label: 'Produk Kompetitor 3 — Kata kunci pencarian', inputType: 'text' },
  { key: 'product3.link', label: 'Produk Kompetitor 3 — LINK', inputType: 'text' },
  { key: 'product3.marketPrice', label: 'Produk Kompetitor 3 — Harga rata-rata pasaran', inputType: 'currency', unit: 'IDR' },
];

// ── Category definitions (maps categories to their fields) ─────────────────

export const MANUAL_DATA_FIELDS: CategoryDefinition[] = [
  { key: 'operational', displayName: 'Kesehatan Operasional Toko', fields: OPERATIONAL_FIELDS },
  { key: 'business', displayName: 'Bisnis Analisis', fields: BUSINESS_FIELDS },
  { key: 'visitors', displayName: 'Tinjauan Pengunjung', fields: VISITORS_FIELDS },
  { key: 'promoTools', displayName: 'Alat Promosi', fields: PROMO_TOOLS_FIELDS },
  { key: 'products', displayName: 'Produk/Status', fields: PRODUCTS_FIELDS },
  { key: 'ads', displayName: 'Data Iklan', fields: ADS_FIELDS },
  { key: 'campaign', displayName: 'Partisipasi Campaign', fields: CAMPAIGN_FIELDS },
  { key: 'competition', displayName: 'Kompetisi TOP Produk', fields: COMPETITION_FIELDS },
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

  const { salesStartMonth: _ssm, ...bizData } = data.business;
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
    salesStartMonth: null,
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
    product1: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
    product2: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
    product3: { productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null },
  },
};
