This document tells addition/changes of the UI/UX of the evaluation page.


Step 1. Brand Info & Operational
# Category Type -> Kategori Toko

# Operational -> Kesehatan Operasional Toko
Link: https://seller.shopee.co.id/portal/accounthealth/home

Pesanan Tidak Terselesaikan -> Tingkat Pesanan Tidak Terselesaikan
Keterlambatan -> Tingkat Keterlambatan Pengiriman
Chat Dibalas -> Persentase Chat Dibalas
Penilaian -> Keseluruhan Penilaian

Step 2. Business, Content & Visitors
# Business -> Bisnis Analisis
Link: https://seller.shopee.co.id/datacenter/dashboard

Penjualan Bulan Ini, Penjualan Bulan -1, Penjualan Bulan -2, etc. 
These should be specific. Example Penjualan Bulan Jan 2026, Penjualan Bulan Des 2025, etc. User should be able to choose the starting date, in this case the starting date is the Jan 2026. The remaining months should be in descending order. So if user choose Jan 2026 as the starting date, then the remaining months should be Des 2025, Nov 2025, etc.
Tingkat Konversi, this should be same as the first Penjualan Bulan. So if user choose Jan 2026 as the starting date, then the Tingkat Konversi should be Tingkat Konversi Jan 2026, and Penjualan Bulan 2026.
Add Rata-rata Penjualan 6 Bulan Terakhir which are the average of the first 6 months of the user's selected starting date.

# Visitors -> Tinjauan Pengunjung
Link: https://seller.shopee.co.id/datacenter/traffic/overview

Add % Pengunjung Lama which is Pengunjung Lama / Total Pengunjung.

In Total Pengikut add Link to the store link
# Content, this section can be deleted

Step 3. Promo Tools & Products/Status
# Promo Tools
Link: https://seller.shopee.co.id/datacenter/marketing/tools/discount

Promo Toko -> Penjualan dari Promo Toko
Paket Diskon -> Penjualan dari Paket Diskon
Kombo Hemat -> Penjualan dari Kombo Hemat
Flash Sale Toko Saya -> Penjualan dari Flash Sale Toko Saya
Voucher -> Penjualan dari Voucher
Shopee Live -> Penjualan dari Shopee Live
Game Toko -> Penjualan dari Game Toko

Brand Membership -> Penjualan dari Brand Membership
Add Link: https://seller.shopee.co.id/datacenter/marketing/membership

Gratis Ongkir XTRA -> Penjualan dari Gratis Ongkir XTRA
Add Link: https://seller.shopee.co.id/portal/marketing/cmt/campaign?tab=2&sort=9

Chat Broadcast -> Penjualan dari Chat Broadcast
Add Link: https://seller.shopee.co.id/datacenter/services/crm

Program Afiliasi -> Penjualan dari Program Afiliasi
Add Link: https://seller.shopee.co.id/portal/web-seller-affiliate/dashboard

Add % Penggunaan alat promosi which is COUNTIF of all Promo Tools that have values more than 0 divide by COUNTA of all Promo Tools.

Add % Efektifitas alat promosi which is COUNTIF of all Promo Tools that are more than the threshold set/passed divide by COUNTA of all Promo Tools

# Products/Status
Add Link to the store link.

Step 5. Ads, Campaign, Competition & Review

# Ads -> Data Iklan
Link: https://seller.shopee.co.id/portal/marketing/pas/assembly?&type=all&group=last-thirty-days

Add ROI which is Penjualan Iklan divide by Biaya Iklan
Add % GMV Iklan / GMV Toko which is Penjualan Iklan divide by Penjualan Bulan that the user chose, in this example Penjualan Bulan Jan 2026.
Add % Biaya Iklan / GMV Toko which is Biaya Iklan divide by Penjualan Bulan that the user chose, in this example Penjualan Bulan Jan 2026.

# Campaign -> Partisipasi Campaign
Link: https://seller.shopee.co.id/portal/marketing/cmt-product/campaign?tab=AllCampaign

Add % Partisipasi Campaign which is Sesi Dinominasikan divide by Sesi Tersedia.

# Competition -> Kompetisi TOP Produk
The order should be Produk Kompetitor 1 - Nama Produk, Produk Kompetitor 1 - Harga Jual, Produk Kompetitor 1 - Kata kunci pencarian, Produk Kompetitor 1 - LINK, Produk Kompetitor 1 - Harga rata-rata pasaran, then teh result.