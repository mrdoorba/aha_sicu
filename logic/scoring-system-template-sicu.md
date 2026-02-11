# Scoring System: Template SICU (Store Internal Check Up)

This is the main scoring sheet that combines manual inputs and calculator outputs to produce a comprehensive store health report with scores and an email summary.

---

## Overview

The scoring system evaluates a Shopee store across multiple categories. Each metric gets:
- **D column**: Raw value (manually input or calculated)
- **E column**: Benchmark/threshold (e.g., "<1%", ">95%")
- **F column**: Pass/Fail verdict ("✔️" or "❌")
- **G column**: Text summary for email output
- **H column**: Score points

**Total Score** = SUM(H7:H75) in cell H4.

---

## Sheet Structure

### Rows 1-5: Store Metadata

| Cell | Content | Source |
|------|---------|--------|
| A1 | "Periode Data: Jan 2026" | Manual |
| G2 | Store name (e.g., "MOON DAE Official Store") | Manual — this is the main identifier |
| H2 | Short brand name used in labels | Manual |
| B2 | BD (Business Development person) | Lookup from VP sheet |
| D2 | PIC name | Lookup from VP sheet |
| B3 | Store link | Lookup from VP sheet |
| G3 | Email | Manual |
| B4 | Company name | Lookup from VP sheet |
| G5 | Category | Manual (used to determine Fashion-specific thresholds) |
| F75 | Final verdict | Manual: "✔️", "❌", "❌ Non Mall", "❌ No Brand", "❌ Opex", or empty |

### Row 6: Column Headers

```
A: Link | B: Kategori | C: Metrik | D: Nilai | E: Rata² AHA | F: Hasil Analisa | G: (text output) | H: Score
```

---

## Evaluation Categories

### 1. Kesehatan Operasional Toko (Rows 7-11)

All values in D column are **manual input**.

| Row | Metric | Benchmark | Score Formula |
|-----|--------|-----------|---------------|
| 7 | Tingkat Pesanan Tidak Terselesaikan | <1% | ✔️=4, >1%=-(D7×100), ❌=0 |
| 8 | Tingkat Keterlambatan Pengiriman | <1% | ✔️=3, >1%=-(D8×100), ❌=0 |
| 9 | Masa Pengemasan | <1 | ✔️=3, >1=-((D9-1)×100), ❌=0 |
| 10 | Persentase Chat Dibalas | >95% | (no score) |
| 11 | Keseluruhan Penilaian | >4.7 | (no score) |

> **F10 special**: Uses `ROUNDUP(D10, 2)` before comparing to threshold (rounds up to 2 decimal places).

**F column logic** (generic for most rows):
```
IF benchmark starts with "<": pass if D <= threshold
IF benchmark starts with ">": pass if D >= threshold
IF benchmark is "-": skip (show "-")
```

**G column logic** (generic for most rows):
```
IF ❌: "[❌] [Metric] = [value] [Kurang Baik, nilai disarankan: [benchmark]]"
IF ✔️: "[✔️] [Metric] = [value] [Sudah Baik]"
```

**G column number formats by row:**
- G7, G8: TEXT(D, "0.0%") — percentage with 1 decimal
- G9: TEXT(D, "0.00") — number with 2 decimals
- G10: TEXT(D, "0%") — percentage no decimal
- G11: TEXT(D, "0.00") — number with 2 decimals

### 2. Bisnis Analisis (Rows 13-20)

| Row | Metric | D Value | Benchmark | Score |
|-----|--------|---------|-----------|-------|
| 13 | Penjualan [current month] | Manual (IDR) | >[avg 6mo] | 10 if D19 < D13×110%, else 0 |
| 14-18 | Penjualan [past 5 months] | Manual (IDR) | — | — |
| 19 | Rata² Penjualan 6 bulan terakhir | =AVERAGE(D13:D18) | — | 10 if >100,000,000, else 0 |
| 20 | Tingkat Konversi [month] | Manual (%) | >3% (or >2% for Fashion) | (no score) |

**E13** = `=">"&TEXT(D19,"0,0")` — benchmark is dynamically set to the 6-month average.

**E49** = `=D49/D13` — shows ad cost as percentage of current month sales (display only).

**G13 special logic:**
```
IF ❌: "❌ [Penjualan month] = IDR [value] [Menurun [%] dibandingkan dengan rata² 6 bulan terakhir: IDR [avg]]"
IF ✔️: "✔️ [Penjualan month] = IDR [value] [Meningkat [%] dibandingkan dengan rata² 6 bulan terakhir: IDR [avg]]"
IF decline > 25%: append "❗️ Potensi peningkatan harga jual signifikan atau terdapat event abnormal."
```

### 3. Skor Kesehatan Konten (Rows 22-24)

| Row | Metric | D Value | Benchmark |
|-----|--------|---------|-----------|
| 22 | Perlu ditingkatkan | Manual (count) | - |
| 23 | Kualitas baik | Manual (count) | - |
| 24 | % Konten baik | =D23/(D23+D22) | >95% |

### 4. Tinjauan Pengunjung (Rows 26-29)

| Row | Metric | D Value | Benchmark | Score |
|-----|--------|---------|-----------|-------|
| 26 | Total Pengunjung | Manual | - | — |
| 27 | Pengunjung Lama | Manual | - | — |
| 28 | % Pengunjung Lama | =D27/D26 | >23% | ✔️=3, ❌=0 |
| 29 | Total Pengikut | Manual | >50000 | ✔️=2, ❌=0 |

### 5. Promo Toko (Rows 31-43)

Individual promotion tools (rows 31-41). D value = revenue from each tool (manual input IDR).

| Row | Tool | Benchmark |
|-----|------|-----------|
| 31 | Promo Toko | >8% |
| 32 | Paket Diskon | >16% |
| 33 | Kombo Hemat | >1% |
| 34 | Flash Sale Toko Saya | >1% |
| 35 | Voucher | >84% |
| 36 | Shopee Live | >15% |
| 37 | Game Toko | >1% |
| 38 | Brand Membership | >1% |
| 39 | Gratis Ongkir XTRA | >0 |
| 40 | Chat Broadcast | >1% |
| 41 | Program Afiliasi | >18% |

**F column for promo rows 31-41** (special logic):
```
IF D=0: "❌"
IF D/D$13 >= 50%: "❌" (too dependent on promo)
IF D >= benchmark_% × D$13: "✔️"
ELSE: "❌"
```

> **Note**: Promo benchmarks (E31-E41) are percentages like ">8%". The F formula compares D (absolute IDR) against benchmark × D$13 (current month sales). E.g., for >8%: pass if D31 >= 8% × D13.

**G column for promo rows 31-41** (special logic):
```
IF D=0: "[F] [tool name] nil pendapatan"
IF D/D$13 >= 50%: "[F] [tool] = [%] [Terlalu mengandalkan promo, nilai disarankan: 15%-50%]"
IF ❌: "[F] [tool] = [%] [Kurang Efektif, nilai disarankan: [benchmark]]"
IF ✔️: "[F] [tool] ([%]) digunakan & persentase penggunaan baik"
```

> **Note**: G31 (Promo Toko) has an additional "Terlalu mengandalkan promo" message at >=50%. G41 (Program Afiliasi) uses "digunakan" without "& persentase penggunaan baik" for ✔️.

**Summary rows:**

| Row | Metric | Formula | Benchmark | Score |
|-----|--------|---------|-----------|-------|
| 42 | % Penggunaan alat promosi | COUNTIF(D31:D41,">0")/COUNTA(D31:D41) | >80% | ✔️=0, ❌=5 (penalty) |
| 43 | % Efektifitas alat promosi | COUNTIF(F31:F41,"✔️")/COUNTA(F31:F41) | >90% | ✔️=0, ❌=10 (penalty) |

### 6. Jumlah Produk & Status Toko (Rows 45-46)

| Row | Metric | D Value | Benchmark | Score |
|-----|--------|---------|-----------|-------|
| 45 | Jumlah Produk | Manual | >=35 | ✔️=5, ❌=0 |
| 46 | Status Toko | Manual text | Shopee Mall | Mall=10, Star+=5, ❌=0 |

**F45 special**: Benchmark ">=35" uses `LEN(E)-2` (strips ">=" prefix, not just ">").

**F46 special**: `IFS(D46="Shopee Mall", "✔️", D46="Star+", "✔️", D46<>"", "❌")`

**G45**: `IF ❌: "[NOT OK, nilai disarankan: >=35]"` / `IF ✔️: "[OK]"`

**G46**: `IF ❌: "[Wajib Shopee Mall]"` / `IF ✔️: "[OK]"`

### 7. Data Iklan (Rows 48-53)

| Row | Metric | D Value | Benchmark | Score |
|-----|--------|---------|-----------|-------|
| 48 | Penjualan (iklan) | Manual (IDR) | - | — |
| 49 | Biaya (iklan) | Manual (IDR) | E49=D49/D13 | — |
| 50 | ROI | =D48/D49 | >9 (or >8 for Fashion) | ✔️=0, ❌=5 (penalty) |
| 51 | % GMV Iklan / GMV Toko | =D48/D13 | <84% | ✔️=5, ❌=0 |
| 52 | % Biaya Iklan / GMV Toko | =D49/D13 | <10% | Special (see below) |

**F52 special logic:**
```
IF D52 < 1%: "❌"
IF D52 < 5%: "❌"
IF D52 <= 10%: "✔️"
ELSE: "❌"
```

**G51 special logic:**
```
IF D48=0: "❌ Iklan tidak aktif sama sekali"
IF ❌: "❌ [metric] = [%] [Terlalu bergantung terhadap Iklan, nilai disarankan: <84%]"
IF ✔️: "✔️ [metric] = [%] [Sudah Baik]"
```

**G52 special logic:**
```
IF D49=0: "❌ Iklan tidak aktif sama sekali"
IF D52 < 5%: "❌ Penggunaan iklan terlalu minim ([%]). Nilai disarankan: 5-8%."
IF ❌ (>10%): "❌ [metric] = [%] [Biaya terlalu tinggi, nilai disarankan: <10%]"
IF ✔️: "✔️ [metric] = [%] [Sudah Baik]"
```

**E53**: Label "Iklan check up"
**G53**: **Calculator 1 output** (combined Sheet 1 + Sheet 2 text) — pasted manually.

### 8. Partisipasi Campaign (Rows 55-57)

| Row | Metric | D Value | Benchmark | Score |
|-----|--------|---------|-----------|-------|
| 55 | Sesi dinominasikan | Manual | — | — |
| 56 | Sesi tersedia | Manual | — | — |
| 57 | % Partisipasi Campaign | =D55/D56 | >90% | ✔️=0, ❌=10 (penalty) |

**G57 special logic:**
```
IF ❌: "❌ [metric] = [%] [Kurang Baik, nilai disarankan: >90%]"
IF ✔️: "✔️ [metric] = [%] [Sudah Baik]"
FALLBACK (IFERROR): "❌Tidak ada Campaign yang dipartisipasikan"
```

### 9. Kompetisi TOP Produk (Rows 60-63)

**All manual input** — not from calculators.

| Column | Content |
|--------|---------|
| B61-B63 | Product name (top 3 products) |
| C61-C63 | Selling price (from Calculator 2's "Rata2 Harga Jual") |
| D61-D63 | Search keyword |
| E61-E63 | Auto-generated Shopee search link |
| F61-F63 | Market average price (manual input) |

**G61-G63 logic:**
```
IF selling price > market price × 110%: "❌tidak kompetitif (harga kisaran pasaran: Rp. [market price])"
ELSE: "✅kompetitif"
```

### 10. Stock Analysis (Row 70)

**D70**: **Calculator 2 output** — average stock number. If value has comma (decimal), round to integer.

| Check | Score |
|-------|-------|
| D70 >= 24 | 10 |
| D70 >= 12 | 5 |
| D70 < 12 | -5 (penalty) |

F70: "✔️" if D70 >= 12, else "❌"

### 11. Discount Check Up (Row 73)

**D73**: **Calculator 3 output** — full text pasted, e.g.:
```
% Diskon TOP SKU: 102.9%
Range: 42.2% ~ 50.4%
Voucher 3.9%
Paket Diskon 0.2%
📌 Berpotensi menggunakan 'fake discount'
```

**H73 score:**
```
IF D73 contains "Berpotensi menggunakan 'fake discount'": 0
ELSE: 5
```

---

## Complex Formulas

### G68 — Marketing Cost Estimation

**C68** label: `="📌 Estimasi persentase biaya marketing " & H2 & " sekarang:"`

Parses D73 text using REGEXEXTRACT and combines with D52 (ad cost %):

```
LET(
  i = D52,                                          // % Biaya Iklan / GMV
  t = extract "% Diskon TOP SKU: X%" from D73 / 100,
  ra = extract "Range: X%" (min) from D73 / 100,
  rb = extract "~ X%" (max) from D73 / 100,
  v = extract "Voucher X%" from D73 / 100,
  p = extract "Paket Diskon X%" from D73 / 100,

  result = TEXT((ra*t)+v+p+i+5%, "0.0%") & " ~ " & TEXT((rb*t)+v+p+i+5%, "0.0%")
)
```

If D73 contains fake discount flag → appends:
```
\n📌 Berpotensi menggunakan 'fake discount'
```

Output example: `"43.0% ~ 56.0%\n📌 Berpotensi menggunakan 'fake discount'"`

### G72 — Marketing Percentage Calculation

Complex formula that calculates a recommended marketing percentage:

```
MAX(
  MAX(
    MIN(
      MIN(
        ROUNDDOWN(
          LET(
            i, D52,
            t, extract TOP SKU %,
            ra, extract Range min %,
            rb, extract Range max %,
            v, extract Voucher %,
            p, extract Paket Diskon %,
            avg = ((ra*t)+v+p+i + (rb*t)+v+p+i) / 2,
            TEXT(avg - 3%, "0.0%")
          ), 2
        ),
        20% + IF(Fashion, 5%, 0)
      ),
      VALUE(LEFT(G68, FIND("~",G68)-1))
    ),
    10%
  ),
  IF(Fashion, 15%, 12%)
)

> CEILING(extract first number from G68 / 100, 0.01)
```

Returns TRUE/FALSE — used by G73 to determine which marketing budget to recommend.

### G73 — Marketing Budget Recommendation

```
IF F75="❌" or "⭕️": skip
ELSE:
  "💡Minimum anggaran marketing yang dibutuhkan AHA untuk meningkatkan performa omzet penjualan toko = "
  & TEXT(MAX(MIN([G72 calculation], 25%), 10%), "0%")
```

Output example: `"💡Minimum anggaran marketing yang dibutuhkan AHA = 12%"`

### G66 — Conclusion Summary

Auto-generated text that combines:
```
"- Omset toko di kisaran [min] juta - [max] juta per bulan sejak 6 bulan terakhir"
"- Kualitas operasional toko sudah cukup baik"
  + IF chat response ❌: ", hanya tingkat response chat masih dapat ditingkatkan."
"- Nama produk disarankan untuk dimulai dengan nama brand..."
"- Background foto utama disarankan warna putih..."
  + IF promo effectiveness <80%: "- Beberapa fitur promosi masih belum dimanfaatkan..."
  + IF campaign <80%: "- Partisipasi Campaign Shopee belum maksimal."
"- Banyak produk habis stok tidak diarsipkan."
"- Banyak produk tidak terjual di 30 hari terakhir."
"- Diskon range: " & G68 & " (disarankan...)"
```

---

## Final Verdict (Row 75)

**F75** = Manual input. Possible values:
- `"✔️"` — Prospect worth pursuing
- `"❌"` — Not worth pursuing (too good / low margin)
- `"❌ Non Mall"` — Rejected because not Shopee Mall
- `"❌ No Brand"` — Rejected because no brand ownership
- `"❌ Opex"` — Rejected because operational issues
- `""` (empty) — Store performing too well for AHA to add value
- `"⭕️"` — Special case (suppresses G73 marketing budget)

**G75** = Auto-generated closing message based on F75:

| F75 Value | Message Theme |
|-----------|---------------|
| ✔️ | "Potensi masih belum maksimal" — invite to consultation via cal-bd2.ahacommerce.net |
| ❌ | "Perlu mempertimbangkan potensi keuntungan" — suggest AHA Coventures (bit.ly/AHACoventures) |
| ❌ Non Mall | "Belum berstatus Mall" — offer to help with Mall application process, list HAKI requirements |
| ❌ No Brand | "Bukan toko yang memiliki brand sendiri" — polite decline, leave door open |
| (empty) | "Performa toko sudah cukup baik" — polite decline, leave door open |
| ❌ Opex | "Tingkat keterlambatan cukup tinggi" — ask to fix shipping <2% and packaging <1 day first |

---

## Email Output (G1)

G1 generates a `mailto:` link that compiles ALL G-column outputs into a structured email:

```
Subject: 🏥 AHA Store Internal Check Up (Store ICU) - [Store Name] [Period]

Body sections:
1. Performa Operasional Toko: G7, G8, G9, G10, G11
2. Performa Penjualan Toko: G13, G20
3. Kualitas Konten Produk: G24
4. Tinjauan Pengunjung: G28, G29
5. Tingkat Penggunaan Alat Promosi: G31-G41, G42, G43, G46
6. Performa Iklan: G50, G51, G52, G53 (Calculator 1 output)
7. Partisipasi Campaign: G57
8. Kompetisi TOP Produk: G61, G62, G63
9. Kesimpulan: G66
10. Marketing estimation: C68, G68
11. Marketing budget: G73
12. Closing: G75
```

---

## WhatsApp Output (E1)

E1 generates a WhatsApp `api.whatsapp.com` link with a pre-formatted message referencing the store name and period.

---

## Calculator Output Integration Summary

| Calculator | Output Cell | What's Pasted | Used By |
|-----------|------------|---------------|---------|
| Calculator 1 (Kata Kunci Iklan) | **G53** | Combined text from Sheet 1 (AK2+AK3+AK4) and Sheet 2 (AL2+AL3+AL5+AL6+AL7+AL8+AL9) | Email via G1 |
| Calculator 2 (Penjualan) | **D70** | Average stock number (integer) | F70 (✔️/❌), H70 (score: 10/5/-5) |
| Calculator 3 (Disc Check Up) | **D73** | Full text output (% Diskon, Range, Voucher, Paket, flag) | G68 (marketing %), G72, G73 (budget), H73 (score: 0 or 5) |

> **Note**: C61-C63 (product prices in Kompetisi TOP Produk) are **not** from any calculator. They are separate data provided directly by the store, entered manually.

---

## Score Summary

| Row | Category | Points | Logic |
|-----|----------|--------|-------|
| H7 | Pesanan Tidak Terselesaikan | 4 | ✔️=4, ❌=0, can go negative if >1% |
| H8 | Keterlambatan Pengiriman | 3 | ✔️=3, ❌=0, can go negative if >1% |
| H9 | Masa Pengemasan | 3 | ✔️=3, ❌=0, can go negative if >1 day |
| H13 | Current vs Avg Sales | 10 | 10 if current month not inflated (D19 < D13×110%), else 0 |
| H19 | Average Monthly Sales | 10 | 10 if avg >100M IDR, else 0 |
| H28 | % Pengunjung Lama | 3 | ✔️=3, ❌=0 |
| H29 | Total Pengikut | 2 | ✔️=2, ❌=0 |
| H42 | Promo Tool Usage | 5 | ✔️=0, **❌=5** (opportunity: underused promos) |
| H43 | Promo Effectiveness | 10 | ✔️=0, **❌=10** (opportunity: ineffective promos) |
| H45 | Jumlah Produk | 5 | ✔️=5, ❌=0 |
| H46 | Status Toko | 10 | Mall=10, Star+=5, ❌=0 |
| H50 | ROI Iklan | 5 | ✔️=0, **❌=5** (opportunity: low ad ROI) |
| H51 | % GMV Iklan | 5 | ✔️=5, ❌=0 |
| H57 | Campaign Participation | 10 | ✔️=0, **❌=10** (opportunity: low campaign usage) |
| H70 | Stock Analysis | 10/5/-5 | ≥24=10, ≥12=5, <12=-5 |
| H73 | Fake Discount | 5 | No fake discount=5, detected=0 |

> **Scoring logic**: Some cells (H42, H43, H50, H57) give points when the store has problems — these represent **opportunities for AHA to help improve**. Higher total score = more attractive prospect for AHA partnership.
>
> **Score range**: Can go negative (from H7-H9 penalties and H70=-5). Maximum possible score = **100** (all fundamentals good + all opportunity flags triggered).
