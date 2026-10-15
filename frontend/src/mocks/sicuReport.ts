/**
 * The SICU report, shaped exactly like the email the app already sends.
 *
 * Source: the Agu 2026 "[ID] AHA Store Internal Check Up (Store ICU)" email, as
 * forwarded by Marwah on 15 Oct 2026. BD asked the results page to match that
 * email's output and format, so this file mirrors its sections, its metric set,
 * its benchmark wording and its verdict strings rather than paraphrasing them —
 * a verdict reworded on the page is a verdict that no longer matches the one
 * the brand already has in their inbox.
 *
 * The numbers are the email's. Only the competition product names are changed,
 * because the sample brand in this preview sells cosmetics and the email's
 * example is a car-care store.
 */

export type MetricStatus =
  /** Meets its benchmark. Green tick. */
  | 'good'
  /** Misses its benchmark. Red cross, amber card. */
  | 'bad'
  /** Context, not a verdict — these carry no tick and no benchmark. */
  | 'info';

export interface ReportMetric {
  label: string;
  /** Pre-formatted, because the email prints each one its own way. */
  value: string;
  benchmark?: string;
  /** The coloured line under the rule. Absent on 'info' metrics. */
  verdict?: string;
  status: MetricStatus;
  /** Competition rows run the full width and carry a product link. */
  wide?: boolean;
  linkLabel?: string;
}

export interface ReportGroup {
  title: string;
  metrics: ReportMetric[];
  /** The REAL BENCHMARK aside that sits under Bisnis. */
  note?: { title: string; body: string };
}

export const REPORT_SCORE = {
  /** The headline evaluation score. */
  value: 42,
  /** Shown beside it in the email as a separate chip — a different number. */
  compatibility: 73,
  verdict: 'Performa dapat Ditingkatkan',
};

export const REPORT_META = {
  period: 'Agu 2026',
  category: 'Beauty & Personal Care',
  pic: 'Budi Santoso',
  storeUrl: 'https://shopee.co.id/covermakeofficial',
};

export const REPORT_GROUPS: ReportGroup[] = [
  {
    title: 'Operasional',
    metrics: [
      {
        label: 'Tingkat Pesanan Tidak Terselesaikan',
        value: '0%',
        benchmark: '<1%',
        verdict: 'Tingkat Pesanan Tidak Terselesaikan = 0.0% [Sudah Baik]',
        status: 'good',
      },
      {
        label: 'Tingkat Keterlambatan Pengiriman',
        value: '2.33%',
        benchmark: '<1%',
        verdict: 'Tingkat Keterlambatan Pengiriman = 2.3% [Kurang Baik, nilai disarankan: <1%]',
        status: 'bad',
      },
      {
        label: 'Waktu Persiapan',
        value: '0.55',
        benchmark: '<1',
        verdict: 'Masa Pengemasan = 0.55 hari [Sudah Baik]',
        status: 'good',
      },
      {
        label: 'Persentase Chat Dibalas',
        value: '100%',
        benchmark: '>95%',
        verdict: 'Persentase Chat Dibalas = 100% [Sudah Baik]',
        status: 'good',
      },
      {
        label: 'Rating Keseluruhan',
        value: '4.91',
        benchmark: '>4.7',
        verdict: 'Keseluruhan Penilaian = 4.91 [Sudah Baik]',
        status: 'good',
      },
    ],
  },
  {
    title: 'Bisnis',
    metrics: [
      { label: 'Rata-rata Penjualan 6 Bulan', value: '91,076,096', status: 'info' },
      {
        label: 'Conversion Rate',
        value: '0.99%',
        benchmark: '>3%',
        verdict: 'Tingkat Konversi = 1.0% [Kurang Baik, nilai disarankan: >3%]',
        status: 'bad',
      },
    ],
    note: {
      title: 'REAL BENCHMARK',
      body: 'Real benchmark akan diambil dari omset daftar pesanan yang dikurangi dengan pembatalan. Perhitungan real benchmark baru dapat dilakukan setelah brand mengisi form registrasi. Omset seller center hanya digunakan sebagai penentu skema kerjasama.',
    },
  },
  {
    title: 'Pengunjung',
    metrics: [
      { label: 'Total Pengunjung', value: '4,973', status: 'info' },
      { label: 'Pengunjung Kembali', value: '1,253', status: 'info' },
      {
        label: '% Pengunjung Kembali',
        value: '25.2%',
        benchmark: '>23%',
        verdict: '% Pengunjung Lama = 25.2% [Sudah Baik]',
        status: 'good',
      },
      {
        label: 'Total Followers',
        value: '4,100',
        benchmark: '>50000',
        verdict: 'Total Pengikut = 4,100 [Kurang Baik, nilai disarankan: >50.000]',
        status: 'bad',
      },
    ],
  },
  {
    title: 'Alat Promo',
    metrics: [
      {
        label: 'Tingkat Penggunaan Promo',
        value: '27.3%',
        benchmark: '>80%',
        verdict: 'Penggunaan alat promosi = 27% [Kurang Baik, nilai disarankan: >80%]',
        status: 'bad',
      },
      {
        label: 'Efektivitas Promo',
        value: '9.1%',
        benchmark: '>90%',
        verdict: 'Efektifitas alat promosi = 9% [Kurang Baik, nilai disarankan: >90%]',
        status: 'bad',
      },
    ],
  },
  {
    title: 'Produk & Status',
    metrics: [
      {
        label: 'Jumlah Produk',
        value: '152',
        benchmark: '>=35',
        verdict: 'Jumlah Produk = 152 [OK]',
        status: 'good',
      },
      {
        label: 'Status Toko',
        value: 'Star+',
        benchmark: 'Shopee Mall',
        verdict: 'Status Toko = Star+ [OK]',
        status: 'good',
      },
    ],
  },
  {
    title: 'Iklan',
    metrics: [
      { label: 'Penjualan Iklan', value: '70,336,473', status: 'info' },
      { label: 'Biaya Iklan', value: '4,306,553', status: 'info' },
      { label: 'ROI Iklan', value: '16.3', benchmark: '>9', verdict: 'ROI = 16.3 [Sudah Baik]', status: 'good' },
      {
        label: '% GMV Iklan',
        value: '75.8%',
        benchmark: '<74%',
        verdict:
          '% GMV Iklan / GMV Toko = 75.8% [Terlalu bergantung terhadap Iklan, nilai disarankan: <74%]',
        status: 'bad',
      },
      {
        label: '% Biaya Iklan',
        value: '4.6%',
        benchmark: '<10%',
        verdict: '[Penggunaan iklan terlalu minim (4.6%). Nilai disarankan: 5%-10%.]',
        status: 'bad',
      },
    ],
  },
  {
    title: 'Campaign',
    metrics: [
      { label: 'Sesi Dinominasikan', value: '3', status: 'info' },
      { label: 'Sesi Tersedia', value: '10', status: 'info' },
      {
        label: 'Partisipasi Campaign',
        value: '30.0%',
        benchmark: '>90%',
        verdict: '% Partisipasi Campaign = 30.0% [Kurang Baik, nilai disarankan: >90%]',
        status: 'bad',
      },
    ],
  },
  {
    title: 'Kompetisi',
    metrics: [
      {
        label: 'Produk Kompetisi',
        value: '245,000',
        benchmark: 'IDR 215,027',
        verdict:
          'Covermake Cushion Foundation SPF50 / 15g (IDR 245,000) = ✗ [tidak kompetitif (harga kisaran pasaran: IDR 215,027)]',
        status: 'bad',
        wide: true,
        linkLabel: 'Lihat di Shopee',
      },
      {
        label: 'Produk Kompetisi',
        value: '835,000',
        benchmark: 'IDR 831,364',
        verdict:
          'Covermake Pro Artistry Palette / 24 Shades Limited Edition (IDR 835,000) = ✓ [kompetitif]',
        status: 'good',
        wide: true,
        linkLabel: 'Lihat di Shopee',
      },
      {
        label: 'Produk Kompetisi',
        value: '145,000',
        benchmark: 'IDR 166,759',
        verdict: 'Covermake Hydra Serum Vitamin C - 30ml (IDR 145,000) = ✓ [kompetitif]',
        status: 'good',
        wide: true,
        linkLabel: 'Lihat di Shopee',
      },
    ],
  },
  {
    title: 'Stok',
    metrics: [
      {
        label: 'Rata-rata Stok Top 20% SKU',
        value: '73',
        benchmark: '>=24',
        verdict: 'Rata² Stok TOP 20% SKU = 73 [Sudah Baik]',
        status: 'good',
      },
      {
        label: 'Ketersediaan Stok',
        value: '5.0%',
        benchmark: '≤10% stok habis',
        verdict: '% Ketersediaan Stok = 5% stok habis [Sudah Baik]',
        status: 'good',
      },
    ],
  },
];

export const REPORT_CONCLUSIONS = [
  'Pendapatan toko dalam range 62 juta - 135 juta per bulan selama 6 bulan terakhir',
  'Kualitas operasional toko sudah cukup baik',
  'Nama produk disarankan untuk dimulai dengan nama brand dan mencantumkan FAB produk (Feature, Advantage, & Benefit).',
  'Gambar produk utama sebaiknya menampilkan logo brand termasuk FAB (Features, Advantage, Benefit).',
  'Beberapa fitur promosi masih belum optimal.',
  'Partisipasi Campaign Shopee belum maksimal.',
  'Pastikan produk yang stoknya habis diarsipkan',
  'Tinjau dan optimalkan produk yang kurang laku',
  'Range diskon: 9.6% ~ 10.3%',
];

export const REPORT_MARKETING_BUDGET = {
  label: 'EST. BIAYA MARKETING',
  body: 'Minimum budget marketing yang dibutuhkan AHA untuk meningkatkan performa penjualan toko = 10%',
};

export const REPORT_CLOSING = {
  body: 'Kami melihat bahwa potensi dari Toko {brand} masih belum maksimal. Silahkan klik di link berikut ini untuk menjadwalkan sesi konsultasi yang lebih mendalam untuk menemukan solusi yang tepat bagi bisnis Anda.',
  cta: 'Jadwalkan Konsultasi Gratis',
  outro: 'Semoga apa yang kami bagikan dapat bermanfaat.',
  signoff: 'Salam sukses,',
};
