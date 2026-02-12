# Scoring Calculator Logic — Pre-Epic 5 Snapshot

**Date:** 2026-02-12
**Purpose:** Exhaustive documentation of all hardcoded scoring logic in `backend/app/calculators/scoring.py` (1429 lines). This document captures every threshold, weight, formula, edge case, and verdict so the calculator can be **perfectly recreated** from this document alone. Created before Epic 5 modifies the calculator to accept configurable rules from the database.

**Source file:** `backend/app/calculators/scoring.py`
**Spec file:** `logic/scoring-system-template-sicu.md`

---

## Table of Contents

1. [Overview](#overview)
2. [Data Types and Result Structures](#data-types-and-result-structures)
3. [Helper Functions](#helper-functions)
4. [Category 1: Kesehatan Operasional Toko (Rows 7-11)](#category-1-kesehatan-operasional-toko-rows-7-11)
5. [Category 2: Bisnis Analisis (Rows 13-20)](#category-2-bisnis-analisis-rows-13-20)
6. [Category 3: Skor Kesehatan Konten (Rows 22-24)](#category-3-skor-kesehatan-konten-rows-22-24)
7. [Category 4: Tinjauan Pengunjung (Rows 26-29)](#category-4-tinjauan-pengunjung-rows-26-29)
8. [Category 5: Promo Toko (Rows 31-43)](#category-5-promo-toko-rows-31-43)
9. [Category 6: Jumlah Produk & Status Toko (Rows 45-46)](#category-6-jumlah-produk--status-toko-rows-45-46)
10. [Category 7: Data Iklan (Rows 48-53)](#category-7-data-iklan-rows-48-53)
11. [Category 8: Partisipasi Campaign (Rows 55-57)](#category-8-partisipasi-campaign-rows-55-57)
12. [Category 9: Kompetisi TOP Produk (Rows 60-63)](#category-9-kompetisi-top-produk-rows-60-63)
13. [Category 10: Stok (Row 70)](#category-10-stok-row-70)
14. [Category 11: Discount (Row 73)](#category-11-discount-row-73)
15. [Template-Specific Thresholds](#template-specific-thresholds)
16. [Complex Derived Formulas (G-column)](#complex-derived-formulas-g-column)
17. [Final Verdict and Closing Messages (Row 75)](#final-verdict-and-closing-messages-row-75)
18. [Email Assembly](#email-assembly)
19. [WhatsApp Link](#whatsapp-link)
20. [Score Summary Table](#score-summary-table)
21. [Worked Examples](#worked-examples)

---

## Overview

The scoring calculator is a **pure function** (`calculate_score()`) with no I/O and no database access. It takes:

- `manual_data`: dict — All manual input data from the evaluation form
- `calculator_results`: dict — Output from Calculator 1 (Ads Keyword), Calculator 2 (Top SKU), Calculator 3 (Discount)
- `template`: str — `"fashion"` or `"non_fashion"`
- `verdict`: str — User-selected final verdict (F75)
- `store_name`: str — Store display name
- `period`: str — Period string (e.g., "Jan 2026")
- `brand_name`: str — Short brand name
- `email`: str | None — Optional email address

It returns a `ScoringResult` containing:
- Per-category scores with individual row scores
- Total score (sum of all H-column values)
- G-column messages for each row
- Conclusion (G66), marketing estimation (G68), marketing percentage (G72), marketing budget (G73)
- Closing message (G75)
- Email subject and body
- WhatsApp link

The system evaluates stores across **11 categories** with a 75-row scoring template. Each row has:
- **D column**: Raw value (input or calculated)
- **E column**: Benchmark/threshold
- **F column**: Verdict (`"✔️"`, `"❌"`, or `"-"`)
- **G column**: Text message for email output
- **H column**: Score points

**Total Score** = SUM of all H-column values across all categories.

---

## Data Types and Result Structures

```python
@dataclass
class RowScore:
    row: int          # Row number (e.g., 7, 8, 9...)
    metric: str       # Metric name in Indonesian
    value: Any        # D column: raw value
    benchmark: str    # E column: threshold string
    verdict: str      # F column: "✔️", "❌", or "-"
    message: str      # G column: text output
    score: float      # H column: points

@dataclass
class CategoryScore:
    category: str           # Category name
    score: float            # Total category score
    max_score: float        # Maximum possible score
    rows: list[RowScore]    # Individual row scores
    available: bool = True  # False when required calculator data is missing

@dataclass
class ScoringResult:
    total_score: float
    category_scores: list[CategoryScore]
    verdict: str                     # F75 value
    conclusion: str                  # G66
    marketing_estimation: str        # G68
    marketing_percentage: str        # G72
    marketing_budget: str            # G73
    closing_message: str             # G75
    email_subject: str
    email_body: str                  # G1 assembled
    whatsapp_link: str               # E1
    template: str                    # "fashion" or "non_fashion"
```

---

## Helper Functions

| Function | Purpose |
|----------|---------|
| `_safe_num(value, default=0.0)` | Coerce value to float; None/empty/"−" → default |
| `_safe_str(value, default="")` | Coerce value to stripped string |
| `_get_nested(data, *keys, default=None)` | Safely traverse nested dict keys |
| `_fmt_pct_1dp(value)` | Format fraction as `"23.5%"` (1 decimal) |
| `_fmt_pct_0dp(value)` | Format fraction as `"95%"` (no decimal) |
| `_fmt_num_1dp(value)` | Format as `"0.5%"` (percentage number, 1 decimal) |
| `_fmt_num_2dp(value)` | Format as `"4.70"` (2 decimals) |
| `_fmt_idr(value)` | Format IDR with Indonesian thousands separator (dot): `"26.433.781"` |
| `_rounddown(value, decimals)` | Round DOWN using `math.floor` |
| `_extract_pct(pattern, text)` | Extract percentage from text via regex, return as fraction |

---

## Category 1: Kesehatan Operasional Toko (Rows 7-11)

**Source data:** `manual_data["operational"]`
**Max score:** 10.0

### Row 7: Tingkat Pesanan Tidak Terselesaikan (Unfulfilled Order Rate)
- **Input:** `operational.unfulfilledOrderRate` (percentage number, e.g., 0.5 = 0.5%)
- **Benchmark:** `<1%`
- **Verdict:** `"✔️"` if value ≤ 1.0, else `"❌"`
- **Score:** ✔️ = **4.0**, ❌ = **-(value)** (negative penalty equal to the rate)
- **G message:** `"✔️ Tingkat Pesanan Tidak Terselesaikan = {value:.1f}% Sudah Baik"` or `"❌ ... Kurang Baik, nilai disarankan: <1%"`

### Row 8: Tingkat Keterlambatan Pengiriman (Late Shipment Rate)
- **Input:** `operational.lateShipmentRate` (percentage number)
- **Benchmark:** `<1%`
- **Verdict:** `"✔️"` if value ≤ 1.0, else `"❌"`
- **Score:** ✔️ = **3.0**, ❌ = **-(value)** (negative penalty)
- **G message:** Same pattern as Row 7 with metric name substituted

### Row 9: Masa Pengemasan (Preparation Time)
- **Input:** `operational.preparationTime` (days, e.g., 0.5 = half a day)
- **Benchmark:** `<1`
- **Verdict:** `"✔️"` if value ≤ 1.0, else `"❌"`
- **Score:** ✔️ = **3.0**, ❌ = **-((value - 1) × 100)** (severe penalty)
- **G message:** `"✔️ Masa Pengemasan = {value:.2f} hari Sudah Baik"` or `"❌ ... Kurang Baik, nilai disarankan: <1 hari"`

### Row 10: Persentase Chat Dibalas (Chat Response Rate)
- **Input:** `operational.chatResponseRate` (percentage number)
- **Benchmark:** `>95%`
- **Verdict:** `"✔️"` if `math.ceil(value * 100) / 100 >= 95.0`, else `"❌"` (**ROUNDUP to 2 decimals before comparing**)
- **Score:** **0.0** (no score, verdict only)
- **G message:** `"✔️ Persentase Chat Dibalas = {value:.0f}% Sudah Baik"` or `"❌ ... Kurang Baik, nilai disarankan: >95%"`

### Row 11: Keseluruhan Penilaian (Overall Rating)
- **Input:** `operational.overallRating` (number, e.g., 4.8)
- **Benchmark:** `>4.7`
- **Verdict:** `"✔️"` if value ≥ 4.7, else `"❌"`
- **Score:** **0.0** (no score, verdict only)
- **G message:** `"✔️ Keseluruhan Penilaian = {value:.2f} Sudah Baik"` or `"❌ ... Kurang Baik, nilai disarankan: >4.7"`

---

## Category 2: Bisnis Analisis (Rows 13-20)

**Source data:** `manual_data["business"]`
**Max score:** 20.0

### Row 13: Penjualan (Current Month Sales)
- **Input:** `business.salesMonth0` (IDR amount)
- **Derived:** `avg_6mo = average of salesMonth0 through salesMonth5`
- **Benchmark:** `">{formatted avg_6mo}"` (dynamic)
- **Verdict:** `"✔️"` if `avg_6mo < current_month × 1.10`, else `"❌"`
- **Score:** ✔️ = **10.0**, ❌ = **0.0**
- **G message (✔️):** `"✔️ Penjualan = IDR {value} Meningkat {change_pct:.1f}% dibandingkan dengan rata² 6 bulan terakhir: IDR {avg}"`
- **G message (❌):** `"❌ Penjualan = IDR {value} Menurun {change_pct:.1f}% dibandingkan dengan rata² 6 bulan terakhir: IDR {avg}"`
- **Edge case:** If decline > 25%, append: `"\n❗️ Potensi peningkatan harga jual signifikan atau terdapat event abnormal."`

### Rows 14-18: Past 5 Months Sales
- **Input:** `business.salesMonth1` through `business.salesMonth5`
- **Score:** **0.0** each (reference data only)

### Row 19: Rata² Penjualan 6 bulan terakhir (6-Month Average)
- **Computed:** `sum(salesMonth0..salesMonth5) / 6` (only if any month > 0)
- **Benchmark:** `-`
- **Verdict:** `"✔️"` if avg_6mo > 100,000,000 IDR, else `"❌"`
- **Score:** ✔️ = **10.0**, ❌ = **0.0**

### Row 20: Tingkat Konversi (Conversion Rate)
- **Input:** `business.conversionRate` (percentage number)
- **Benchmark:** `">2%"` for Fashion, `">3%"` for Non-Fashion (**TEMPLATE-SPECIFIC**)
- **Verdict:** `"✔️"` if value ≥ threshold, else `"❌"` (applied in main function, not in category function)
- **Score:** **0.0** (no score, verdict only)
- **G message:** `"✔️ Tingkat Konversi = {value:.1f}% Sudah Baik"` or `"❌ ... Kurang Baik, nilai disarankan: {benchmark}"`

---

## Category 3: Skor Kesehatan Konten (Rows 22-24)

**Source data:** `manual_data["content"]`
**Max score:** 0.0 (no scores, verdict only)

### Row 22: Perlu ditingkatkan (Needs Improvement)
- **Input:** `content.needsImprovement` (count)
- **Score:** 0.0

### Row 23: Kualitas baik (Good Quality)
- **Input:** `content.goodQuality` (count)
- **Score:** 0.0

### Row 24: % Konten baik (Quality Percentage)
- **Computed:** `goodQuality / (goodQuality + needsImprovement)` (0.0 if both are 0)
- **Benchmark:** `>95%`
- **Verdict:** `"✔️"` if value ≥ 0.95, else `"❌"`
- **Score:** **0.0**
- **G message:** `"✔️ % Konten baik = {value as %}  Sudah Baik"` or `"❌ ... Kurang Baik, nilai disarankan: >95%"`

---

## Category 4: Tinjauan Pengunjung (Rows 26-29)

**Source data:** `manual_data["visitors"]`
**Max score:** 5.0

### Row 26: Total Pengunjung
- **Input:** `visitors.totalVisitors` (count)
- **Score:** 0.0

### Row 27: Pengunjung Lama (Returning Visitors)
- **Input:** `visitors.returningVisitors` (count)
- **Score:** 0.0

### Row 28: % Pengunjung Lama (Returning Visitors %)
- **Computed:** `returningVisitors / totalVisitors` (0.0 if totalVisitors is 0)
- **Benchmark:** `>23%`
- **Verdict:** `"✔️"` if value > 0.23, else `"❌"`
- **Score:** ✔️ = **3.0**, ❌ = **0.0**
- **G message:** `"✔️ % Pengunjung Lama = {value as %}  Sudah Baik"` or `"❌ ... Kurang Baik, nilai disarankan: >23%"`

### Row 29: Total Pengikut (Total Followers)
- **Input:** `visitors.totalFollowers` (count)
- **Benchmark:** `>50000`
- **Verdict:** `"✔️"` if value > 50,000, else `"❌"`
- **Score:** ✔️ = **2.0**, ❌ = **0.0**
- **G message:** `"✔️ Total Pengikut = {value:,.0f} Sudah Baik"` or `"❌ ... Kurang Baik, nilai disarankan: >50.000"`

---

## Category 5: Promo Toko (Rows 31-43)

**Source data:** `manual_data["promoTools"]` and `manual_data["business"]["salesMonth0"]` (D13)
**Max score:** 15.0

### Promo Tools Configuration (HARDCODED)

| Row | Field Key | Display Name | Benchmark % |
|-----|-----------|-------------|-------------|
| 31 | `promoToko` | Promo Toko | 8% |
| 32 | `paketDiskon` | Paket Diskon | 16% |
| 33 | `komboHemat` | Kombo Hemat | 1% |
| 34 | `flashSale` | Flash Sale Toko Saya | 1% |
| 35 | `voucher` | Voucher | 84% |
| 36 | `shopeeLive` | Shopee Live | 15% |
| 37 | `gameToko` | Game Toko | 1% |
| 38 | `brandMembership` | Brand Membership | 1% |
| 39 | `gratisOngkir` | Gratis Ongkir XTRA | 0% (any value > 0 passes) |
| 40 | `chatBroadcast` | Chat Broadcast | 1% |
| 41 | `programAfiliasi` | Program Afiliasi | 18% |

### Promo Verdict Logic (Rows 31-41)

For each promo tool row, the verdict follows this priority:
1. If D value = 0 → `"❌"` (not used)
2. If D value / D13 ≥ 50% → `"❌"` (too dependent on this promo)
3. If benchmark is 0.0 (gratisOngkir): any value > 0 → `"✔️"`
4. If D value ≥ benchmark% × D13 → `"✔️"` (meets benchmark)
5. Else → `"❌"`

**Individual row scores:** All **0.0** (no per-tool score)

### Promo G-column Messages (Rows 31-41)

- If D=0: `"{verdict} {tool_name} nil pendapatan"`
- If D/D13 ≥ 50%: `"{verdict} {tool_name} = {pct}% Terlalu mengandalkan promo, nilai disarankan: 15%-50%"`
- If ❌: `"❌ {tool_name} = {pct}% Kurang Efektif, nilai disarankan: {benchmark}"`
- If ✔️ (Program Afiliasi): `"✔️ {tool_name} ({pct}%) digunakan"`
- If ✔️ (all others): `"✔️ {tool_name} ({pct}%) digunakan & persentase penggunaan baik"`

### Row 42: % Penggunaan alat promosi (Usage Rate)
- **Computed:** `count(tools where D > 0) / 11`
- **Benchmark:** `>80%`
- **Verdict:** `"✔️"` if usage_rate > 0.80, else `"❌"`
- **Score:** ✔️ = **0.0**, ❌ = **5.0** (opportunity points — store has unused promo tools)

### Row 43: % Efektifitas alat promosi (Effectiveness Rate)
- **Computed:** `count(tools where verdict = "✔️") / 11`
- **Benchmark:** `>90%`
- **Verdict:** `"✔️"` if effectiveness_rate > 0.90, else `"❌"`
- **Score:** ✔️ = **0.0**, ❌ = **10.0** (opportunity points — store has ineffective promos)

---

## Category 6: Jumlah Produk & Status Toko (Rows 45-46)

**Source data:** `manual_data["products"]`
**Max score:** 15.0

### Row 45: Jumlah Produk (Product Count)
- **Input:** `products.productCount` (number)
- **Benchmark:** `>=35`
- **Verdict:** `"✔️"` if value ≥ 35, else `"❌"`
- **Score:** ✔️ = **5.0**, ❌ = **0.0**
- **G message:** `"✔️ Jumlah Produk = {value} OK"` or `"❌ Jumlah Produk = {value} NOT OK, nilai disarankan: >=35"`

### Row 46: Status Toko (Store Status)
- **Input:** `products.storeStatus` (string: `"Shopee Mall"`, `"Star+"`, or other)
- **Benchmark:** `Shopee Mall`
- **Verdict and Score:**
  - `"Shopee Mall"` → ✔️, **10.0**
  - `"Star+"` → ✔️, **5.0**
  - Any other non-empty string → ❌, **0.0**
  - Empty → `-`, **0.0**
- **G message:** `"✔️ Status Toko = {value} OK"` or `"❌ Status Toko = {value} Wajib Shopee Mall"`

---

## Category 7: Data Iklan (Rows 48-53)

**Source data:** `manual_data["ads"]` and `manual_data["business"]["salesMonth0"]` (D13)
**Max score:** 10.0

### Row 48: Penjualan (iklan) — Ad Sales
- **Input:** `ads.adSales` (IDR)
- **Score:** 0.0

### Row 49: Biaya (iklan) — Ad Cost
- **Input:** `ads.adCost` (IDR)
- **Benchmark display:** `D49/D13` as percentage
- **Score:** 0.0

### Row 50: ROI
- **Computed:** `adSales / adCost` (0.0 if adCost is 0)
- **Benchmark:** `>8` for Fashion, `>9` for Non-Fashion (**TEMPLATE-SPECIFIC**)
- **Verdict:** `"✔️"` if ROI ≥ threshold, else `"❌"`
- **Score:** ✔️ = **0.0**, ❌ = **5.0** (opportunity — low ad ROI)
- **G message:** `"✔️ ROI = {value:.1f} Sudah Baik"` or `"❌ ROI = {value:.1f} Kurang Baik, nilai disarankan: >{threshold}"`

### Row 51: % GMV Iklan / GMV Toko
- **Computed:** `adSales / D13` (0.0 if D13 is 0)
- **Benchmark:** `<84%`
- **Verdict:** `"✔️"` if value < 0.84, else `"❌"`
- **Score:** ✔️ = **5.0**, ❌ = **0.0**
- **G message special:** If adSales = 0: `"❌ Iklan tidak aktif sama sekali"`

### Row 52: % Biaya Iklan / GMV Toko
- **Computed:** `adCost / D13` (0.0 if D13 is 0)
- **Benchmark:** `<10%`
- **Verdict (special 4-tier):**
  - < 1% → `"❌"` (too low)
  - < 5% → `"❌"` (too minimal)
  - ≤ 10% → `"✔️"` (good range)
  - > 10% → `"❌"` (too high)
- **Score:** 0.0
- **G message special:**
  - If adCost = 0: `"❌ Iklan tidak aktif sama sekali"`
  - If < 5%: `"❌ Penggunaan iklan terlalu minim ({pct}%). Nilai disarankan: 5-8%."`
  - If ❌ (>10%): `"❌ % Biaya Iklan / GMV Toko = {pct}% Biaya terlalu tinggi, nilai disarankan: <10%"`
  - If ✔️: `"✔️ % Biaya Iklan / GMV Toko = {pct}% Sudah Baik"`

### Row 53: Iklan check up
- **Content:** Calculator 1 (Ads Keyword) `output_text` — pasted directly as G message
- **Score:** 0.0

---

## Category 8: Partisipasi Campaign (Rows 55-57)

**Source data:** `manual_data["campaign"]`
**Max score:** 10.0

### Row 55: Sesi dinominasikan (Nominated Sessions)
- **Input:** `campaign.nominatedSessions` (count)
- **Score:** 0.0

### Row 56: Sesi tersedia (Available Sessions)
- **Input:** `campaign.availableSessions` (count)
- **Score:** 0.0

### Row 57: % Partisipasi Campaign
- **Computed:** `nominatedSessions / availableSessions` (0.0 if availableSessions is 0)
- **Benchmark:** `>90%`
- **Verdict:** `"✔️"` if value > 0.90, else `"❌"`
- **Score:** ✔️ = **0.0**, ❌ = **10.0** (opportunity — low campaign participation)
- **G message special:** If value is 0.0 exactly: `"❌Tidak ada Campaign yang dipartisipasikan"` (IFERROR fallback)

---

## Category 9: Kompetisi TOP Produk (Rows 60-63)

**Source data:** `manual_data["competition"]` and `calculator_results["top_sku"]["details"]["output_1"]`
**Max score:** 0.0 (no scores, verdict only)

### Rows 61-63: Product 1-3
- **Selling price:** From Calculator 2's `output_1[i].rata2_harga_jual`
- **Market price:** `competition.product{i}.marketPrice` (manual input)
- **Verdict:** `"❌"` if selling_price > market_price × 1.10, `"✔️"` otherwise, `"-"` if either price is 0
- **Score:** 0.0 each
- **G message:** `"❌tidak kompetitif (harga kisaran pasaran: Rp. {market_price})"` or `"✅kompetitif"`

---

## Category 10: Stok (Row 70)

**Source data:** `calculator_results["top_sku"]["details"]["average_stock"]`
**Max score:** 10.0

### Row 70: Rata² Stok (Average Stock)
- **Computed:** From Calculator 2's `average_stock`, rounded to integer
- **If Calculator 2 not available:** `available = False`, score = 0.0, message = `"Calculator 2 (Top SKU) belum dijalankan"`
- **Scoring (3-tier):**
  - ≥ 24 → ✔️, **10.0**
  - ≥ 12 → ✔️, **5.0**
  - < 12 → ❌, **-5.0** (penalty)

---

## Category 11: Discount (Row 73)

**Source data:** `calculator_results["discount"]["details"]["fake_discount_flag"]` and `calculator_results["discount"]["output_text"]`
**Max score:** 5.0

### Row 73: Discount Check Up
- **If Calculator 3 not available:** `available = False`, score = 0.0
- **Verdict:** `"❌"` if `fake_discount_flag` is True, `"✔️"` otherwise
- **Score:** fake discount detected = **0.0**, no fake discount = **5.0**

---

## Template-Specific Thresholds

| Parameter | Fashion | Non-Fashion |
|-----------|---------|-------------|
| Conversion Rate (Row 20) benchmark | >2% | >3% |
| ROI (Row 50) threshold | >8 | >9 |
| Marketing % upper limit (G72) | 25% (0.20 + 0.05) | 20% (0.20) |
| Marketing % lower bound (G72) | 15% | 12% |
| Default marketing % when no D73 data | 15% | 12% |

---

## Complex Derived Formulas (G-column)

### G66: Conclusion Summary

Multi-line auto-generated text. Built from:

1. **Sales range:** `"- Omset toko di kisaran {min}juta - {max} juta per bulan sejak 6 bulan terakhir"` (from salesMonth0-5, excluding zeros, divided by 1,000,000)
2. **Operational quality:** `"- Kualitas operasional toko sudah cukup baik"` + if Row 10 verdict is ❌: `", hanya tingkat response chat masih dapat ditingkatkan."`
3. **Standard recommendations (always):**
   - `"- Nama produk disarankan untuk dimulai dengan nama brand"`
   - `"- Background foto utama disarankan warna putih"`
4. **Promo check:** If Row 43 effectiveness < 80%: `"- Beberapa fitur promosi masih belum dimanfaatkan secara efektif"`
5. **Campaign check:** If Row 57 participation < 80%: `"- Partisipasi Campaign Shopee belum maksimal."`
6. **Stock/archival (always):**
   - `"- Banyak produk habis stok tidak diarsipkan."`
   - `"- Banyak produk tidak terjual di 30 hari terakhir."`
7. **Discount range:** If G68 exists: `"- Diskon range: {G68}"`

### G68: Marketing Cost Estimation

Parses Calculator 3's D73 output text to extract 5 percentages, then combines with ad cost percentage:

```
Extracted from D73 text:
  t  = "% Diskon TOP SKU: X%"  → X/100
  ra = "Range: X%"              → X/100
  rb = "~ X%"                   → X/100
  v  = "Voucher X%"             → X/100
  p  = "Paket Diskon X%"        → X/100

d52 = adCost / D13 (as fraction)

low  = (ra × t) + v + p + d52 + 0.05
high = (rb × t) + v + p + d52 + 0.05

Result = "{low×100:.1f}% ~ {high×100:.1f}%"

If D73 contains "Berpotensi" or "fake discount":
  append "\n📌 Berpotensi menggunakan 'fake discount'"
```

Returns empty string if D73 is empty.

### G72: Recommended Marketing Percentage

```
If no D73 data → return 0.15 (Fashion) or 0.12 (Non-Fashion)

Parse D73 for t, ra, rb, v, p (same as G68)

avg = ((ra×t + v + p + d52) + (rb×t + v + p + d52)) / 2
base = ROUNDDOWN(avg - 0.03, 2)

upper_limit = 0.20 + (0.05 if Fashion else 0.0)  → 0.25 or 0.20

g68_first = CEILING(first percentage from G68 text) / 100
  (parse first "X%" from G68, ceil to integer, divide by 100)

min_val = MIN(MIN(base, upper_limit), g68_first)  [if g68_first > 0]
        = MIN(base, upper_limit)                     [if g68_first = 0]

result = MAX(MAX(min_val, 0.10), 0.15 if Fashion else 0.12)
```

Returns a fraction (e.g., 0.15 = 15%).

### G73: Marketing Budget Recommendation

```
If verdict starts with "❌" or verdict is "⭕️" → return ""

display_pct = MAX(MIN(g72_value, 0.25), 0.10)   → clamp to 10%-25%
budget = D13 × display_pct

Result = "💡Minimum anggaran marketing yang dibutuhkan AHA untuk meningkatkan
         performa omzet penjualan toko = {display_pct×100:.0f}%
         (± IDR {budget as IDR format}/bulan)"
```

---

## Final Verdict and Closing Messages (Row 75)

**F75** is user-selected. **G75** is auto-generated based on F75:

| F75 Value | G75 Message |
|-----------|-------------|
| `"✔️"` | `"Berdasarkan data analisa diatas, potensi toko masih belum maksimal. Kami mengundang untuk berdiskusi mengenai potensi optimisasi toko melalui link berikut: cal-bd2.ahacommerce.net"` |
| `"❌"` | `"Berdasarkan data analisa diatas, perlu mempertimbangkan potensi keuntungan. Silakan cek AHA Coventures: bit.ly/AHACoventures"` |
| `"❌ Non Mall"` | `"Toko belum berstatus Mall. AHA dapat membantu proses pengajuan Shopee Mall. Persyaratan: HAKI (Merek Terdaftar), NIB, dan dokumen legalitas usaha."` |
| `"❌ No Brand"` | `"Toko bukan merupakan toko yang memiliki brand sendiri. Terima kasih atas waktunya, semoga sukses selalu."` |
| `""` (empty) | `"Performa toko sudah cukup baik. Terima kasih atas waktunya, semoga sukses selalu."` |
| `"❌ Opex"` | `"Tingkat keterlambatan cukup tinggi. Disarankan untuk memperbaiki pengiriman (<2%) dan masa pengemasan (<1 hari) terlebih dahulu."` |
| `"⭕️"` | `""` (empty string) |

---

## Email Assembly

**Subject:** `"🏥 AHA Store Internal Check Up (Store ICU) - {store_name} {period}"`

**Body sections (in order):**

1. `"📊 Performa Operasional Toko:"` → G7, G8, G9, G10, G11
2. `"📈 Performa Penjualan Toko:"` → G13, G20
3. `"📝 Kualitas Konten Produk:"` → G24
4. `"👥 Tinjauan Pengunjung:"` → G28, G29
5. `"🏷️ Tingkat Penggunaan Alat Promosi:"` → G31-G41, G42, G43, G46 (store status from Category 6)
6. `"📣 Performa Iklan:"` → G50, G51, G52, G53
7. `"🎯 Partisipasi Campaign:"` → G57
8. `"🏆 Kompetisi TOP Produk:"` → G61, G62, G63
9. `"📋 Kesimpulan:"` → G66
10. `"📌 {marketing_label}"` → G68
11. G73 (marketing budget)
12. G75 (closing)

Each section is joined by newlines. Empty sections are skipped.

---

## WhatsApp Link

```
Message: "Halo, ini hasil Store Internal Check Up (Store ICU) untuk {store_name} periode {period}. Silakan cek email untuk detail lengkapnya."

Link: "https://api.whatsapp.com/send?text={url_encoded_message}"
```

---

## Score Summary Table

| Row | Category | Metric | Max | Scoring Logic |
|-----|----------|--------|-----|---------------|
| H7 | Operational | Unfulfilled Orders | 4 | ✔️=4, ❌=-(value) |
| H8 | Operational | Late Shipment | 3 | ✔️=3, ❌=-(value) |
| H9 | Operational | Preparation Time | 3 | ✔️=3, ❌=-((v-1)×100) |
| H13 | Business | Current Sales | 10 | 10 if avg < current×110% |
| H19 | Business | 6-Month Average | 10 | 10 if avg > 100M IDR |
| H28 | Visitors | Returning % | 3 | ✔️=3 |
| H29 | Visitors | Followers | 2 | ✔️=2 |
| H42 | Promo | Usage Rate | 5 | ❌=5 (opportunity) |
| H43 | Promo | Effectiveness | 10 | ❌=10 (opportunity) |
| H45 | Products | Product Count | 5 | ✔️=5 |
| H46 | Products | Store Status | 10 | Mall=10, Star+=5 |
| H50 | Ads | ROI | 5 | ❌=5 (opportunity) |
| H51 | Ads | GMV Ratio | 5 | ✔️=5 |
| H57 | Campaign | Participation | 10 | ❌=10 (opportunity) |
| H70 | Stock | Average Stock | 10 | ≥24=10, ≥12=5, <12=-5 |
| H73 | Discount | Fake Discount | 5 | No fake=5, fake=0 |

**Theoretical max:** 100 (all fundamentals good + all opportunity flags triggered)
**Theoretical min:** Negative (from H7, H8, H9 penalties and H70=-5)

**"Opportunity" scores** (H42, H43, H50, H57): Points are awarded when the store has **problems** — these represent areas where AHA can help improve. Higher total = more attractive prospect for AHA partnership.

---

## Worked Examples

### Example 1: Fashion Store — Strong Performance

**Inputs:**
- Template: `"fashion"`
- Verdict: `"✔️"`
- operational: unfulfilledOrderRate=0.3, lateShipmentRate=0.5, preparationTime=0.8, chatResponseRate=96, overallRating=4.8
- business: salesMonth0=150M, salesMonth1=120M, salesMonth2=130M, salesMonth3=110M, salesMonth4=140M, salesMonth5=125M
- visitors: totalVisitors=50000, returningVisitors=15000, totalFollowers=80000
- promoTools: all 11 tools used with values exceeding benchmarks relative to D13
- products: productCount=45, storeStatus="Shopee Mall"
- ads: adSales=800M, adCost=10M
- campaign: nominatedSessions=18, availableSessions=20
- Calculator 2 average_stock=30
- Calculator 3 fake_discount_flag=False

**Scoring walkthrough:**

| Row | Verdict | Score | Reasoning |
|-----|---------|-------|-----------|
| H7 | ✔️ | 4.0 | 0.3 ≤ 1.0 |
| H8 | ✔️ | 3.0 | 0.5 ≤ 1.0 |
| H9 | ✔️ | 3.0 | 0.8 ≤ 1.0 |
| H13 | ✔️ | 10.0 | avg_6mo=129.2M < 150M × 1.10 = 165M |
| H19 | ✔️ | 10.0 | avg_6mo=129.2M > 100M |
| H28 | ✔️ | 3.0 | 15000/50000=30% > 23% |
| H29 | ✔️ | 2.0 | 80000 > 50000 |
| H42 | ✔️ | 0.0 | 11/11=100% > 80% |
| H43 | ✔️ | 0.0 | All pass > 90% |
| H45 | ✔️ | 5.0 | 45 ≥ 35 |
| H46 | ✔️ | 10.0 | Shopee Mall |
| H50 | ✔️ | 0.0 | 800M/10M=80 ≥ 8 (Fashion threshold) |
| H51 | ✔️ | 5.0 | 800M/150M=5.33 < 0.84 (53.3% < 84%) |
| H57 | ✔️ | 0.0 | 18/20=90% > 90%? Actually 90% is NOT > 90%, so ❌ |

Wait — correction on H57: 90% is not > 90% (strict greater than), so:

| H57 | ❌ | 10.0 | 18/20=0.9 is NOT > 0.90 (equal, not greater) |
| H70 | ✔️ | 10.0 | 30 ≥ 24 |
| H73 | ✔️ | 5.0 | No fake discount |

**Total: 4+3+3+10+10+3+2+0+0+5+10+0+5+10+10+5 = 80.0**

### Example 2: Non-Fashion Store — Weak Performance

**Inputs:**
- Template: `"non_fashion"`
- Verdict: `"❌"`
- operational: unfulfilledOrderRate=2.5, lateShipmentRate=3.0, preparationTime=2.0, chatResponseRate=80, overallRating=4.2
- business: salesMonth0=40M, salesMonth1=50M, salesMonth2=45M, salesMonth3=60M, salesMonth4=55M, salesMonth5=50M
- visitors: totalVisitors=10000, returningVisitors=1500, totalFollowers=20000
- promoTools: only 3 of 11 tools used, none meeting benchmarks
- products: productCount=20, storeStatus="Star+"
- ads: adSales=100M, adCost=15M
- campaign: nominatedSessions=5, availableSessions=20
- Calculator 2 average_stock=8
- Calculator 3 fake_discount_flag=True

**Scoring walkthrough:**

| Row | Verdict | Score | Reasoning |
|-----|---------|-------|-----------|
| H7 | ❌ | -2.5 | 2.5 > 1.0, score = -(2.5) |
| H8 | ❌ | -3.0 | 3.0 > 1.0, score = -(3.0) |
| H9 | ❌ | -100.0 | 2.0 > 1.0, score = -((2.0-1)×100) = -100 |
| H13 | ❌ | 0.0 | avg=50M, 50M ≥ 40M × 1.10 = 44M |
| H19 | ❌ | 0.0 | avg=50M ≤ 100M |
| H28 | ❌ | 0.0 | 1500/10000=15% ≤ 23% |
| H29 | ❌ | 0.0 | 20000 ≤ 50000 |
| H42 | ❌ | 5.0 | 3/11=27% ≤ 80% |
| H43 | ❌ | 10.0 | 0/11=0% ≤ 90% |
| H45 | ❌ | 0.0 | 20 < 35 |
| H46 | ✔️ | 5.0 | Star+ |
| H50 | ❌ | 5.0 | 100M/15M=6.67 < 9 (Non-Fashion threshold) |
| H51 | ❌ | 0.0 | 100M/40M=2.5 ≥ 0.84 |
| H57 | ❌ | 10.0 | 5/20=25% ≤ 90% |
| H70 | ❌ | -5.0 | 8 < 12 |
| H73 | ❌ | 0.0 | Fake discount detected |

**Total: -2.5 + -3.0 + -100.0 + 0 + 0 + 0 + 0 + 5 + 10 + 0 + 5 + 5 + 0 + 10 + -5 + 0 = -75.5**

This demonstrates how operational penalties (especially H9) can drive the score deeply negative.

---

_Document created: 2026-02-12_
_Purpose: Pre-Epic 5 snapshot of all hardcoded scoring logic_
_To be verified against source code by QA before scoring calculator refactor_
