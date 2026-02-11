# Calculator 1: Kalkulator Kata Kunci Iklan Shopee

This calculator analyzes Shopee ad performance. It has 2 sheets. The final output is a combined text summary used in the scoring system.

---

## Sheet 1: Iklan Health Check Up V2A

### Input

- **Source**: Shopee CPC Ad Report CSV (Data Keseluruhan Iklan)
- **Rows 1–7**: Store metadata (username, store name, store ID, report period)
- **Row 8**: Header row
- **Row 9+**: Ad data

### Column Mapping

Both Sheet 1 and Sheet 2 have a **blank column F** inserted in the Google Sheet (not present in the CSV export). This shifts all columns after E by +1. The table below shows both the **Sheet column** (used in formulas) and the **CSV column** (used when reading files).

| Sheet Col | CSV Col | Name |
|-----------|---------|------|
| A | A | Urutan |
| B | B | Nama Iklan |
| C | C | Status: "Berjalan" (Active), "Dijeda" (Paused), "Berakhir" (Ended) |
| D | D | Jenis Iklan: "Iklan Produk" or empty for shop-level ads |
| E | E | Kode Produk |
| F | — | BLANK (unused, inserted in sheet) |
| G | F | Tampilan Iklan |
| H | G | Mode Bidding: "Bidding Otomatis", "Bidding Manual", "GMV Max ROAS", "GMV Max Auto", "GMV Max Auto Bidding (Shop)" |
| I | H | Penempatan Iklan: "Halaman Pencarian", "Halaman Rekomendasi", "Semua Penempatan" |
| J | I | Tanggal Mulai |
| K | J | Tanggal Selesai |
| ... | ... | (metric columns continue with +1 offset) |
| AH | — | Helper column (CleanName) |

### Manual Input

- **AK1**: Total number of products in the store (entered manually by user)

### Helper Column (AH)

- **Purpose**: Clean the ad name by removing everything from `[` onward
- **Formula logic**: If ad name contains `[`, take text before it. Otherwise keep full name.

### Output Cells

#### AK2 — Ad Overview Summary

Formula:
```
"• Total Iklan: " & COUNTIF(C,"Berjalan") & " Aktif, " & COUNTIF(C,"Dijeda") & " Dijeda dan " & COUNTIF(C,"Berakhir") & " Berakhir.
• Melibatkan " & COUNTA(UNIQUE(QUERY(B2:AH,"select AH where D='Iklan Produk' and C<>'Berakhir'"))) & " (" & TEXT(.../AK1,"0.0%") & ") produk dari total jumlah produk: " & AK1 & "."
```

Key points:
- Unique product count uses **non-ended** (C<>'Berakhir') ads where **D='Iklan Produk'**
- Uses CleanName (column AH) for deduplication
- Shop-level ads (empty Jenis Iklan) are excluded from product count
- Percentage = unique products / AK1, formatted as "0.0%"

#### AK3 — Ad Type Breakdown

Counts **non-ended** (C<>'Berakhir') ads by type:

```
"• Jenis Iklan yang aktif digunakan:
[X] Iklan Produk Halaman Pencarian ([Y] Otomatis & [Z] Manual).
[X] Iklan Produk Halaman Rekomendasi ([Y] Otomatis & [Z] Manual).
[X] Iklan Produk Otomatis Semua Halaman.
[X] Iklan Toko ([Y] Otomatis & [Z] Manual)."
```

Line-by-line formulas:
- **Search**: COUNTIFS(D="Iklan Produk", C<>"Berakhir", I="Halaman Pencarian"), split by H="Bidding Otomatis" / H="Bidding Manual"
- **Recommendation**: COUNTIFS(D="Iklan Produk", C<>"Berakhir", I="Halaman Rekomendasi"), split by H
- **Semua Halaman**: COUNTIFS(I="Semua Penempatan", C<>"Berakhir") — **NO Jenis Iklan filter**, includes shop-level ads
- **Iklan Toko**: COUNTIFS(D="Iklan Toko", C<>"Berakhir"), split by H

#### AK4 — Recommendations

Generates flags. Each check is independent and all applicable flags are concatenated.

**Flag 1 — Product participation:**
```
IF product_pct < 50%:
  "📌 Jumlah produk yang dipartisipasikan ke dalam iklan kurang maksimal (saran >50%)."
ELSE:
  "📌 Jumlah produk yang dipartisipasikan ke dalam iklan sudah cukup baik."
```

**Flag 2 — Active ad ratio:**
```
IF active_ratio < 50%:
  "📌 Jumlah iklan dengan status aktif kurang maksimal (saran >50%)."
ELSE IF product_pct >= 50%:
  "📌 Jumlah iklan dengan status aktif sudah cukup baik."
ELSE:
  (nothing — suppressed when product participation is already flagged as low)
```

**Flags 3-7 — Ad type checks (count ALL ads regardless of status):**

| # | Check | Condition | Flag |
|---|-------|-----------|------|
| 3 | Search Page | COUNTIF(I, "Halaman Pencarian") = 0 | "📌 Iklan Produk Halaman Pencarian belum dimanfaatkan." |
| 4 | Search Manual | COUNTIFS(I, "Halaman Pencarian", H, "Bidding Manual") = 0 | "📌 Iklan Produk Halaman Pencarian (Bidding Manual) belum dimanfaatkan." |
| 5 | Recommendation | COUNTIF(I, "Halaman Rekomendasi") = 0 | "📌 Iklan Produk Halaman Rekomendasi belum dimanfaatkan." |
| 6 | Reco Manual | COUNTIFS(I, "Halaman Rekomendasi", H, "Bidding Manual") = 0 | "📌 Iklan Produk Halaman Rekomendasi (Bidding Manual) belum dimanfaatkan." |
| 7 | Shop Ads | COUNTIF(D, "Iklan Toko") = 0 | "📌 Iklan Toko belum dimanfaatkan." |

> **Important**: Flags 3-7 check **ALL ads** (including ended ones), not just non-ended. This is different from AK2/AK3 which filter by C<>'Berakhir'.

---

## Sheet 2: Iklan Health Check Up V2B

### Input

- **Source**: Shopee Keyword/Placement Report CSV (Laporan Penempatan Kata Pencarian)
- **Rows 1–7**: Store metadata
- **Row 8**: Header row
- **Row 9+**: Ad keyword-level data

### Column Mapping

Same blank column F as Sheet 1, plus two additional columns (Kata Pencarian, Tipe Pencocokan):

| Sheet Col | CSV Col | Name |
|-----------|---------|------|
| D | D | Jenis Iklan |
| E | E | Kode Produk |
| F | — | BLANK (unused) |
| G | F | Tampilan Iklan |
| H | G | Mode Bidding |
| I | H | Penempatan Iklan |
| J | I | Kata Pencarian/Penempatan |
| K | J | Tipe Pencocokan |
| L | K | Tanggal Mulai |
| M | L | Tanggal Selesai |
| ... | ... | (metric columns) |
| Y | X | Omzet Penjualan (GMV) — used for TOP filter |
| Z | Y | Penjualan Langsung (GMV Langsung) |
| AA | Z | Biaya (Cost) — used for BOTTOM filter |
| AB | AA | Efektifitas Iklan (ROAS) — used for both filters |
| AJ | — | Helper column (CleanName) |

### Calculated Thresholds

Thresholds are calculated from **ALL rows** (including shop-level ads with empty Jenis):

| Cell | Formula | Description |
|------|---------|-------------|
| AM6 | ROUND(AVERAGEIF(Y, ">0")) | GMV threshold for TOP ads |
| AM7 | MIN(ROUND(AVERAGEIF(AB, ">0")), 10) | ROAS threshold for TOP (capped at 10) |
| AM9 | ROUND(AVERAGEIF(AA, ">0")) | Cost threshold for BOTTOM ads |
| AM10 | MIN(ROUND(AVERAGEIF(AB, ">0")), 3) | ROAS threshold for BOTTOM (capped at 3) |

### Output Cells

#### AL2 — TOP Ads (Best Performers)

**Primary QUERY**: `select AJ where D<>'' and Y > AM6 and AB > AM7 order by Y desc limit 5`

The `D<>''` excludes shop-level ads from results. Thresholds use all data.

**Fallback** (if primary returns no results via IFNA): `where D<>'' and Y > AM6/2 and AB > MAX(AM7/2, 6) order by Y desc limit 5`

**Primary format** (per ad):
```
▶[CleanName (AJ)]
   GMV: IDR [GMV (Y) formatted "0,0"] {ROAS: [ROAS (AB)]}
   [Mode Bidding (H)]
   [Jenis Iklan (D)] [Penempatan (I)]: [Kata Pencarian (J)]
```

**Fallback format** (per ad):
```
▶[CleanName (AJ)]
   GMV: IDR [GMV (Y) formatted "0,0"] {ROAS: [ROAS (AB)]}
   [Mode Bidding (H)]
   [Jenis Iklan (D)] [Penempatan (I)]: [Kata Pencarian (J)]
```

#### AL3 — Top Ads Recommendation

Counts substrings in AL2 text (case-insensitive):

```
IF count("Bidding Otomatis" in AL2) >= 3:
  "📌 Iklan dengan performa terbaik mengandalkan pengaturan otomatis (pengaturan manual berpotensi belum dimanfaatkan secara maksimal)."
ELSE IF count("GMV Max" in AL2) >= 3:
  "📌 Iklan dengan performa terbaik mengandalkan pengaturan otomatis (pengaturan manual berpotensi belum dimanfaatkan secara maksimal)."
ELSE:
  "📌 Iklan dengan performa terbaik sudah mengandalkan pengaturan manual."
```

> **Key**: "GMV Max ROAS" contains substring "GMV Max", so it counts. With 3+ top ads using any "GMV Max" variant, the auto flag triggers.

#### AL5 — BOTTOM Ads (Worst Performers)

**Primary QUERY**: `where D<>'' and AA > 100000 and AA > AM9 and AB < AM10 and AB < 5 order by AA desc limit 5`

**Primary format** (per ad):
```
▶[CleanName (AJ)]
   Biaya: IDR [Cost (AA) formatted "0,0"] {ROAS: [ROAS (AB)]}
   [Mode Bidding (H)]
   [Jenis Iklan (D)] [Penempatan (I)]: [Kata Pencarian (J)]
```

**Fallback** (if primary returns no results via IFNA): `where D<>'' and AA > 100000 and AA > AM9 and AB < MIN(ROUND(AM10*2,0), 5) and AB < 5 order by AA desc limit 5`

**Fallback format differs** — no newline between Mode Bidding and Jenis (lines 3-4 merged):
```
▶[CleanName (AJ)]
   Biaya: IDR [Cost (AA) formatted "0,0"] {ROAS: [ROAS (AB)]}
   [Mode Bidding (H)] [Jenis Iklan (D)] [Penempatan (I)]: [Kata Pencarian (J)]
```

#### AL6 — Bottom Auto Bidding Flag

```
IF count("Otomatis" in AL5) >= 1:
  "📌 Terdapat iklan dengan pengaturan otomatis yang tidak terkontrol biayanya (disarankan dimonitor 1-2x setiap hari)."
```

> **Note**: "Pilih Otomatis" (from Kata Pencarian column) also contains "Otomatis" and will trigger this flag.

#### AL7 — Bottom Manual Bidding Flag

```
IF count("Bidding Manual" in AL5) >= 1:
  "📌 Terdapat iklan dengan pengaturan manual yang tidak terkontrol biayanya (disarankan dimonitor 1-2x setiap hari)."
```

#### AL8 — Bottom Keywords Flag

```
IF count("Iklan Pencarian Produk: " in AL5) >= 3:
  "📌 Terdapat kata kunci dengan pengaturan manual yang tidak terkontrol biayanya (disarankan dipantau 1-2x setiap hari)."
```

#### AL9 — Bottom Auto Bidding Flag (variant)

```
IF count("Auto Bidding" in AL5) >= 1:
  "📌 Terdapat iklan dengan pengaturan otomatis yang tidak terkontrol biayanya (disarankan dimonitor 1-2x setiap hari)."
```

---

## Final Output: Combined Results for Scoring System

All results are stacked into **one cell** in the scoring system sheet (Template SICU), specifically **cell G53**, in this order:

```
[Sheet 1] AK2 — Ad Overview Summary
[Sheet 1] AK3 — Ad Type Breakdown
[Sheet 1] AK4 — Recommendations
[Sheet 2] AL2 — TOP Ads
[Sheet 2] AL3 — Top Ads Recommendation
[Sheet 2] AL5 — BOTTOM Ads
[Sheet 2] AL6 — Bottom Auto Bidding Flag
[Sheet 2] AL7 — Bottom Manual Bidding Flag
[Sheet 2] AL8 — Bottom Keywords Flag
[Sheet 2] AL9 — Bottom Auto Bidding Flag (variant)
```

---

## Sample Results

### MND (Moon Dae Official Store, Nov 2025) — AK1=80

**Sheet 1:**
```
• Total Iklan: 4 Aktif, 1 Dijeda dan 44 Berakhir.
• Melibatkan 4 (5.0%) produk dari total jumlah produk: 80.

• Jenis Iklan yang aktif digunakan:
  0 Iklan Produk Halaman Pencarian (0 Otomatis & 0 Manual).
  0 Iklan Produk Halaman Rekomendasi (0 Otomatis & 0 Manual).
  5 Iklan Produk Otomatis Semua Halaman.
  0 Iklan Toko (0 Otomatis & 0 Manual).

📌 Jumlah produk yang dipartisipasikan ke dalam iklan kurang maksimal (saran >50%).
📌 Jumlah iklan dengan status aktif kurang maksimal (saran >50%).
📌 Iklan Produk Halaman Pencarian belum dimanfaatkan.
📌 Iklan Produk Halaman Pencarian (Bidding Manual) belum dimanfaatkan.
📌 Iklan Produk Halaman Rekomendasi belum dimanfaatkan.
📌 Iklan Produk Halaman Rekomendasi (Bidding Manual) belum dimanfaatkan.
📌 Iklan Toko belum dimanfaatkan.
```

**Sheet 2:**
```
Thresholds: AM6=3,786,348 | AM7=5 | AM9=451,559 | AM10=3

• TOP Iklan (GMV tertinggi dengan ROAS terbaik):
  ▶ MOON DAE Yonsei Bag Tas Ransel Wanita Kulit Premium Backpack Women Tas Korea
    GMV: IDR 26,433,781 {ROAS: 5.68}
    GMV Max ROAS
    Iklan Produk Semua Penempatan: Pilih Otomatis
  ▶ MOON DAE Seoul Shoulder Bag Tas Bahu Wanita Kulit Premium Sling Bag Totebag For Women Tas Korea
    GMV: IDR 18,426,425 {ROAS: 5.52}
    GMV Max ROAS
    Iklan Produk Semua Penempatan: Pilih Otomatis
  ▶ MOON DAE Namsan Bag Tas Ransel Wanita Kulit Premium Backpack Women Tas Korea
    GMV: IDR 11,624,623 {ROAS: 6}
    GMV Max ROAS
    Iklan Produk Semua Penempatan: Pilih Otomatis
  ▶ MOON DAE Honey Shoulder Bag Tas Bahu Wanita Denim Kulit Premium Handbag For Women Tas Korea
    GMV: IDR 8,973,367 {ROAS: 6.73}
    GMV Max ROAS
    Iklan Produk Semua Penempatan: Pilih Otomatis
  ▶ MOON DAE Seoul Shoulder Bag Tas Bahu Wanita Kulit Premium Sling Bag Totebag For Women Tas Korea
    GMV: IDR 6,846,341 {ROAS: 5.9}
    GMV Max ROAS
    Iklan Produk Semua Penempatan: Pilih Otomatis

📌 Iklan dengan performa terbaik mengandalkan pengaturan otomatis (pengaturan manual berpotensi belum dimanfaatkan secara maksimal).

• BOTTOM Iklan [fallback] (biaya tertinggi dengan ROAS terendah):
  ▶ MOON DAE Haru Pack Tas Ransel Laptop Wanita Multifungsi Totepack Kuliah Kerja Korea MND-HARU
    Biaya: IDR 490,361 {ROAS: 4.7}
    GMV Max Auto Iklan Produk Semua Penempatan: Pilih Otomatis

📌 Terdapat iklan dengan pengaturan otomatis yang tidak terkontrol biayanya (disarankan dimonitor 1-2x setiap hari).
```

### KYPSO (KYPSO Official Store, Nov 2025) — AK1=54

**Sheet 1:**
```
• Total Iklan: 3 Aktif, 0 Dijeda dan 7 Berakhir.
• Melibatkan 2 (3.7%) produk dari total jumlah produk: 54.

• Jenis Iklan yang aktif digunakan:
  0 Iklan Produk Halaman Pencarian (0 Otomatis & 0 Manual).
  0 Iklan Produk Halaman Rekomendasi (0 Otomatis & 0 Manual).
  3 Iklan Produk Otomatis Semua Halaman.
  0 Iklan Toko (0 Otomatis & 0 Manual).

📌 Jumlah produk yang dipartisipasikan ke dalam iklan kurang maksimal (saran >50%).
📌 Jumlah iklan dengan status aktif kurang maksimal (saran >50%).
📌 Iklan Produk Halaman Pencarian belum dimanfaatkan.
📌 Iklan Produk Halaman Pencarian (Bidding Manual) belum dimanfaatkan.
📌 Iklan Produk Halaman Rekomendasi belum dimanfaatkan.
📌 Iklan Produk Halaman Rekomendasi (Bidding Manual) belum dimanfaatkan.
```

**Sheet 2:**
```
Thresholds: AM6=7,623,425 | AM7=5 | AM9=1,561,197 | AM10=3

• TOP Iklan (GMV tertinggi dengan ROAS terbaik):
  ▶ KYPSO Sovereign Tas Selempang Kulit Pria Sling Bag Anti Air Shoulder Bag Tas Bahu Waterproof Premium
    GMV: IDR 38,479,479 {ROAS: 6.77}
    GMV Max ROAS
    Iklan Produk Semua Penempatan: Pilih Otomatis
  ▶ KYPSO Monarch Tas Kerja Kulit Pria Selempang Laptop Tas Kantor Sling Bag Messenger Leather Briefcase
    GMV: IDR 14,881,374 {ROAS: 5.59}
    GMV Max ROAS
    Iklan Produk Semua Penempatan: Pilih Otomatis

📌 Iklan dengan performa terbaik sudah mengandalkan pengaturan manual.

• BOTTOM Iklan (biaya tertinggi dengan ROAS terendah):
  ▶ KYPSO Phantom Tas Selempang Kulit Pria Sling Bag Anti Air Waterproof Tas Bahu Premium Crossbody Bag
    Biaya: IDR 2,145,872 {ROAS: 4.94}
    GMV Max ROAS
    Iklan Produk Semua Penempatan: Pilih Otomatis

📌 Terdapat iklan dengan pengaturan otomatis yang tidak terkontrol biayanya (disarankan dimonitor 1-2x setiap hari).
```
