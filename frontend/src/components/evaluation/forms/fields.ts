import type { CategoryDefinition, FieldDefinition, SelectOption } from './types';

// ── Store Status options ───────────────────────────────────────────────────

export const STORE_STATUS_OPTIONS: SelectOption[] = [
  { value: 'Shopee Mall', label: 'Shopee Mall' },
  { value: 'Star+', label: 'Star+' },
  { value: 'Star', label: 'Star' },
  { value: 'Regular', label: 'Regular' },
];

// ── Section reference links ────────────────────────────────────────────────

/** Returns the Shopee Seller Centre base URL for the given marketplace. */
export function getSellerBaseUrl(marketplace: string = 'ID'): string {
  return marketplace === 'TH'
    ? 'https://seller.shopee.co.th'
    : 'https://seller.shopee.co.id';
}

/** Rewrites a seller.shopee.co.id URL to the correct marketplace domain. */
export function localizeSellerLink(link: string, marketplace: string = 'ID'): string {
  if (marketplace === 'TH') {
    return link.replace('seller.shopee.co.id', 'seller.shopee.co.th');
  }
  return link;
}

export function getSectionLinks(marketplace: string = 'ID') {
  const base = getSellerBaseUrl(marketplace);
  return {
    operational: `${base}/portal/accounthealth/home`,
    business: `${base}/datacenter/dashboard`,
    visitors: `${base}/datacenter/traffic/overview`,
    promoTools: `${base}/datacenter/marketing/tools/discount`,
    ads: `${base}/portal/marketing/pas/assembly?&type=all&group=last-thirty-days`,
    campaign: `${base}/portal/marketing/cmt-product/campaign?tab=AllCampaign`,
  };
}

// ── Month label constants ─────────────────────────────────────────────────

export const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
export const GENERIC_LABELS = ["generic.thisMonth", "generic.month1", "generic.month2", "generic.month3", "generic.month4", "generic.month5"];

// ── Field definitions per category ─────────────────────────────────────────

export const OPERATIONAL_FIELDS: FieldDefinition[] = [
  { key: 'unfulfilledOrderRate', label: 'Tingkat Pesanan Tidak Terselesaikan', labelKey: 'fields.operational.unfulfilledOrderRate', inputType: 'number', unit: '%', benchmark: '<1%' },
  { key: 'lateShipmentRate', label: 'Tingkat Keterlambatan Pengiriman', labelKey: 'fields.operational.lateShipmentRate', inputType: 'number', unit: '%', benchmark: '<1%' },
  { key: 'preparationTime', label: 'Masa Pengemasan', labelKey: 'fields.operational.preparationTime', inputType: 'number', unit: 'hari', unitKey: 'common.days', benchmark: '<1' },
  { key: 'chatResponseRate', label: 'Persentase Chat Dibalas', labelKey: 'fields.operational.chatResponseRate', inputType: 'number', unit: '%', benchmark: '>95%' },
  { key: 'overallRating', label: 'Keseluruhan Penilaian', labelKey: 'fields.operational.overallRating', inputType: 'number', unit: 'rating', benchmark: '>4.7' },
];

export const BUSINESS_FIELDS: FieldDefinition[] = [
  { key: 'salesMonth0', label: 'Penjualan Bulan Ini', labelKey: 'fields.business.salesMonth0', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth1', label: 'Penjualan Bulan -1', labelKey: 'fields.business.salesMonth1', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth2', label: 'Penjualan Bulan -2', labelKey: 'fields.business.salesMonth2', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth3', label: 'Penjualan Bulan -3', labelKey: 'fields.business.salesMonth3', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth4', label: 'Penjualan Bulan -4', labelKey: 'fields.business.salesMonth4', inputType: 'currency', unit: 'IDR' },
  { key: 'salesMonth5', label: 'Penjualan Bulan -5', labelKey: 'fields.business.salesMonth5', inputType: 'currency', unit: 'IDR' },
  { key: 'conversionRate', label: 'Tingkat Konversi', labelKey: 'fields.business.conversionRate', inputType: 'number', unit: '%', benchmark: '>3%' },
];

export const VISITORS_FIELDS: FieldDefinition[] = [
  { key: 'totalVisitors', label: 'Total Pengunjung', labelKey: 'fields.visitors.totalVisitors', inputType: 'number', unit: 'count' },
  { key: 'returningVisitors', label: 'Pengunjung Lama', labelKey: 'fields.visitors.returningVisitors', inputType: 'number', unit: 'count' },
  { key: 'totalFollowers', label: 'Total Pengikut', labelKey: 'fields.visitors.totalFollowers', inputType: 'number', unit: 'count', benchmark: '>50,000' },
];

export const PROMO_TOOLS_FIELDS: FieldDefinition[] = [
  { key: 'promoToko', label: 'Penjualan dari Promo Toko', labelKey: 'fields.promoTools.promoToko', inputType: 'currency', unit: 'IDR', benchmark: '>8% dari penjualan', benchmarkKey: 'fields.promoTools.promoToko.benchmark', threshold: 0.08 },
  { key: 'paketDiskon', label: 'Penjualan dari Paket Diskon', labelKey: 'fields.promoTools.paketDiskon', inputType: 'currency', unit: 'IDR', benchmark: '>16% dari penjualan', benchmarkKey: 'fields.promoTools.paketDiskon.benchmark', threshold: 0.16 },
  { key: 'komboHemat', label: 'Penjualan dari Kombo Hemat', labelKey: 'fields.promoTools.komboHemat', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan', benchmarkKey: 'fields.promoTools.komboHemat.benchmark', threshold: 0.01 },
  { key: 'flashSale', label: 'Penjualan dari Flash Sale Toko Saya', labelKey: 'fields.promoTools.flashSale', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan', benchmarkKey: 'fields.promoTools.flashSale.benchmark', threshold: 0.01 },
  { key: 'voucher', label: 'Penjualan dari Voucher', labelKey: 'fields.promoTools.voucher', inputType: 'currency', unit: 'IDR', benchmark: '>68% dari penjualan', benchmarkKey: 'fields.promoTools.voucher.benchmark', threshold: 0.68 },
  { key: 'shopeeLive', label: 'Penjualan dari Shopee Live', labelKey: 'fields.promoTools.shopeeLive', inputType: 'currency', unit: 'IDR', benchmark: '>15% dari penjualan', benchmarkKey: 'fields.promoTools.shopeeLive.benchmark', threshold: 0.15 },
  { key: 'gameToko', label: 'Penjualan dari Game Toko', labelKey: 'fields.promoTools.gameToko', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan', benchmarkKey: 'fields.promoTools.gameToko.benchmark', threshold: 0.01 },
  { key: 'brandMembership', label: 'Penjualan dari Brand Membership', labelKey: 'fields.promoTools.brandMembership', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan', benchmarkKey: 'fields.promoTools.brandMembership.benchmark', threshold: 0.01, link: 'https://seller.shopee.co.id/datacenter/marketing/membership' },
  { key: 'gratisOngkir', label: 'Penjualan dari Gratis Ongkir XTRA', labelKey: 'fields.promoTools.gratisOngkir', inputType: 'currency', unit: 'IDR', benchmark: '>0', threshold: 0, link: 'https://seller.shopee.co.id/portal/marketing/cmt/campaign?tab=2&sort=9' },
  { key: 'chatBroadcast', label: 'Penjualan dari Chat Broadcast', labelKey: 'fields.promoTools.chatBroadcast', inputType: 'currency', unit: 'IDR', benchmark: '>1% dari penjualan', benchmarkKey: 'fields.promoTools.chatBroadcast.benchmark', threshold: 0.01, link: 'https://seller.shopee.co.id/datacenter/services/crm' },
  { key: 'programAfiliasi', label: 'Penjualan dari Program Afiliasi', labelKey: 'fields.promoTools.programAfiliasi', inputType: 'currency', unit: 'IDR', benchmark: '>21% dari penjualan', benchmarkKey: 'fields.promoTools.programAfiliasi.benchmark', threshold: 0.21, link: 'https://seller.shopee.co.id/portal/web-seller-affiliate/dashboard' },
  { key: 'komisiProgramAfiliasi', label: 'Komisi dari Program Afiliasi', labelKey: 'fields.promoTools.komisiProgramAfiliasi', inputType: 'currency', unit: 'IDR' },
];

export const PRODUCTS_FIELDS: FieldDefinition[] = [
  { key: 'productCount', label: 'Jumlah Produk', labelKey: 'fields.products.productCount', inputType: 'number', unit: 'count', benchmark: '>=35' },
  { key: 'storeStatus', label: 'Status Toko', labelKey: 'fields.products.storeStatus', inputType: 'select', benchmark: 'Shopee Mall' },
];

export const ADS_FIELDS: FieldDefinition[] = [
  { key: 'adSales', label: 'Penjualan Iklan', labelKey: 'fields.ads.adSales', inputType: 'currency', unit: 'IDR' },
  { key: 'adCost', label: 'Biaya Iklan', labelKey: 'fields.ads.adCost', inputType: 'currency', unit: 'IDR' },
];

export const CAMPAIGN_FIELDS: FieldDefinition[] = [
  { key: 'nominatedSessions', label: 'Sesi Dinominasikan', labelKey: 'fields.campaign.nominatedSessions', inputType: 'number', unit: 'count' },
  { key: 'availableSessions', label: 'Sesi Tersedia', labelKey: 'fields.campaign.availableSessions', inputType: 'number', unit: 'count' },
];

export const COMPETITION_FIELDS: FieldDefinition[] = [
  { key: 'product1.productName', label: 'Produk Kompetitor 1 — Nama Produk', labelKey: 'fields.competition.product1.productName', inputType: 'text' },
  { key: 'product1.sellingPrice', label: 'Produk Kompetitor 1 — Harga Jual', labelKey: 'fields.competition.product1.sellingPrice', inputType: 'currency', unit: 'IDR' },
  { key: 'product1.keyword', label: 'Produk Kompetitor 1 — Kata kunci pencarian', labelKey: 'fields.competition.product1.keyword', inputType: 'text' },
  { key: 'product1.link', label: 'Produk Kompetitor 1 — LINK', labelKey: 'fields.competition.product1.link', inputType: 'text' },
  { key: 'product1.marketPrice', label: 'Produk Kompetitor 1 — Harga rata-rata pasaran', labelKey: 'fields.competition.product1.marketPrice', inputType: 'currency', unit: 'IDR' },
  { key: 'product2.productName', label: 'Produk Kompetitor 2 — Nama Produk', labelKey: 'fields.competition.product2.productName', inputType: 'text' },
  { key: 'product2.sellingPrice', label: 'Produk Kompetitor 2 — Harga Jual', labelKey: 'fields.competition.product2.sellingPrice', inputType: 'currency', unit: 'IDR' },
  { key: 'product2.keyword', label: 'Produk Kompetitor 2 — Kata kunci pencarian', labelKey: 'fields.competition.product2.keyword', inputType: 'text' },
  { key: 'product2.link', label: 'Produk Kompetitor 2 — LINK', labelKey: 'fields.competition.product2.link', inputType: 'text' },
  { key: 'product2.marketPrice', label: 'Produk Kompetitor 2 — Harga rata-rata pasaran', labelKey: 'fields.competition.product2.marketPrice', inputType: 'currency', unit: 'IDR' },
  { key: 'product3.productName', label: 'Produk Kompetitor 3 — Nama Produk', labelKey: 'fields.competition.product3.productName', inputType: 'text' },
  { key: 'product3.sellingPrice', label: 'Produk Kompetitor 3 — Harga Jual', labelKey: 'fields.competition.product3.sellingPrice', inputType: 'currency', unit: 'IDR' },
  { key: 'product3.keyword', label: 'Produk Kompetitor 3 — Kata kunci pencarian', labelKey: 'fields.competition.product3.keyword', inputType: 'text' },
  { key: 'product3.link', label: 'Produk Kompetitor 3 — LINK', labelKey: 'fields.competition.product3.link', inputType: 'text' },
  { key: 'product3.marketPrice', label: 'Produk Kompetitor 3 — Harga rata-rata pasaran', labelKey: 'fields.competition.product3.marketPrice', inputType: 'currency', unit: 'IDR' },
];

// ── Category definitions (maps categories to their fields) ─────────────────

export const MANUAL_DATA_FIELDS: CategoryDefinition[] = [
  { key: 'operational', displayName: 'Kesehatan Operasional Toko', displayNameKey: 'categories.operational', fields: OPERATIONAL_FIELDS },
  { key: 'business', displayName: 'Bisnis Analisis', displayNameKey: 'categories.business', fields: BUSINESS_FIELDS },
  { key: 'visitors', displayName: 'Tinjauan Pengunjung', displayNameKey: 'categories.visitors', fields: VISITORS_FIELDS },
  { key: 'promoTools', displayName: 'Alat Promosi', displayNameKey: 'categories.promoTools', fields: PROMO_TOOLS_FIELDS },
  { key: 'products', displayName: 'Produk/Status', displayNameKey: 'categories.products', fields: PRODUCTS_FIELDS },
  { key: 'ads', displayName: 'Data Iklan', displayNameKey: 'categories.ads', fields: ADS_FIELDS },
  { key: 'campaign', displayName: 'Partisipasi Campaign', displayNameKey: 'categories.campaign', fields: CAMPAIGN_FIELDS },
  { key: 'competition', displayName: 'Kompetisi TOP Produk', displayNameKey: 'categories.competition', fields: COMPETITION_FIELDS },
];
