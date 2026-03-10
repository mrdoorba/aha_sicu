import type { CategoryDefinition, FieldDefinition, SelectOption } from './types';

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

// ── Month label constants ─────────────────────────────────────────────────

export const INDO_MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
export const GENERIC_LABELS = ["Bulan Ini", "Bulan -1", "Bulan -2", "Bulan -3", "Bulan -4", "Bulan -5"];

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
