# Validation Report: {Brand Name}

**Evaluator:** ____________________
**Date:** ____________________
**Brand:** ____________________
**Category:** Fashion / Non-Fashion
**Production URL:** https://aha-sicu-prod.web.app

---

## 1. Evaluation Summary

| Item | Details |
|------|---------|
| Brand name | |
| Evaluation date | |
| Files uploaded | CPC Ad ☐ / Keyword ☐ / Order ☐ / Mass Update ☐ |
| Manual data entered | Yes / Partial / No |
| All 3 calculators executed | Yes / No |
| Final score generated | Yes / No |
| Evaluation saved | Yes / No |

---

## 2. Ads Keyword Calculator Validation

**Reference spec:** `logic/calculator-1-kata-kunci-iklan-shopee.md`

### AK2 — Ad Overview

| Metric | System Output | Manual Calculation | Match? | Notes |
|--------|--------------|-------------------|--------|-------|
| Total ads count | | | ☐ | |
| Active (Berjalan) count | | | ☐ | |
| Paused (Dijeda) count | | | ☐ | |
| Ended (Berakhir) count | | | ☐ | |
| Unique products with ads | | | ☐ | |
| Product participation % | | | ☐ | |

### AK3 — Ad Type Breakdown

| Placement Type | System Output | Manual Calculation | Match? | Notes |
|----------------|--------------|-------------------|--------|-------|
| Halaman Pencarian (manual) | | | ☐ | |
| Halaman Pencarian (auto) | | | ☐ | |
| Halaman Rekomendasi (manual) | | | ☐ | |
| Halaman Rekomendasi (auto) | | | ☐ | |
| Semua Penempatan (total) | | | ☐ | |
| Iklan Toko (manual) | | | ☐ | |
| Iklan Toko (auto) | | | ☐ | |

### AK4 — Seven Recommendation Flags

| Flag # | Description | System Flag | Manual Flag | Match? | Notes |
|--------|-------------|------------|-------------|--------|-------|
| 1 | Product participation < 50% | | | ☐ | |
| 2 | Active ratio < 50% | | | ☐ | |
| 3 | No search page ads | | | ☐ | |
| 4 | No manual bidding on search | | | ☐ | |
| 5 | No recommendation page ads | | | ☐ | |
| 6 | No manual bidding on reco | | | ☐ | |
| 7 | No shop ads | | | ☐ | |

### Top & Bottom Keyword Lists

| Metric | System Output | Manual Calculation | Match? | Notes |
|--------|--------------|-------------------|--------|-------|
| Top ads list (up to 5) | | | ☐ | Compare product names + order |
| Top ads ROAS values | | | ☐ | |
| Bottom ads list (up to 5) | | | ☐ | Compare product names + order |
| Bottom ads cost/ROAS values | | | ☐ | |
| ROAS median flag | | | ☐ | |

---

## 3. Discount Check Calculator Validation

**Reference spec:** `logic/calculator-3-discount-checkup.md`
**Tolerance:** ±0.5% for percentages

| Metric | System Output | Manual Calculation | Delta | Within Tolerance? | Notes |
|--------|--------------|-------------------|-------|-------------------|-------|
| % Diskon TOP SKU | | | | ☐ (±0.5%) | |
| Range min | | | | ☐ (±0.5%) | |
| Range max | | | | ☐ (±0.5%) | |
| Voucher % | | | | ☐ (±0.5%) | |
| Paket Diskon % | | | | ☐ (±0.5%) | |
| Fake discount flag | | | | ☐ (exact match) | Yes/No must agree |

### Detailed Checks

| Check | Result | Notes |
|-------|--------|-------|
| Urutan (item position) calculation correct? | ☐ | First item in order = 1 |
| Voucher/Paket only on Urutan=1? | ☐ | Prevents double-counting |
| Indonesian price format parsed correctly? | ☐ | "125.000" → 125000 |
| Top SKU filter threshold correct? | ☐ | qty > avg_qty AND discount < 100% |

---

## 4. Top SKU Calculator Validation

**Reference spec:** `logic/calculator-2-penjualan.md`
**Tolerance:** ±2 for stock average

### Revenue Ranking (Output 1)

| Metric | System Output | Manual Calculation | Match? | Notes |
|--------|--------------|-------------------|--------|-------|
| Number of top products | | | ☐ | Should be top 20% (min 20) |
| Product #1 (name) | | | ☐ | |
| Product #1 (omzet) | | | ☐ | |
| Product #2 (name) | | | ☐ | |
| Product #2 (omzet) | | | ☐ | |
| Product #3 (name) | | | ☐ | |
| Product #3 (omzet) | | | ☐ | |
| Revenue ranking order | | | ☐ | Same products in same order? |

### Stock Ranking (Output 2)

| Metric | System Output | Manual Calculation | Match? | Notes |
|--------|--------------|-------------------|--------|-------|
| Kode Variasi lookup | | | ☐ | All codes found? |
| Stock values | | | ☐ | Match Mass Update data? |
| Average stock | | | | ☐ (±2 units) | |

### Detailed Checks

| Check | Result | Notes |
|-------|--------|-------|
| Revenue formula correct? | ☐ | (Price × Qty) - Voucher/items - Cashback/items + Shopee Discount/items |
| Order-level discounts split evenly? | ☐ | Voucher, Cashback, Shopee Discount / items_in_order |
| Product grouping matches? | ☐ | "{Nama Produk} - {Nama Variasi}" exact match |
| Indonesian price format handled? | ☐ | "." stripped before parsing |

---

## 5. Final Scoring Validation

**Reference spec:** `logic/scoring-system-template-sicu.md`
**Tolerance:** ±1 point for total score

### Per-Category Scores

| Category | System Score | Manual Score | Delta | Match? | Notes |
|----------|-------------|-------------|-------|--------|-------|
| 1. Kesehatan Operasional | | | | ☐ | |
| 2. Bisnis Analisis | | | | ☐ | |
| 3. Kesehatan Konten | | | | ☐ (info only) | |
| 4. Tinjauan Pengunjung | | | | ☐ | |
| 5. Promo Toko | | | | ☐ | |
| 6. Jumlah Produk & Status | | | | ☐ | |
| 7. Data Iklan | | | | ☐ | |
| 8. Partisipasi Campaign | | | | ☐ | |
| 9. Kompetisi TOP Produk | | | | ☐ (info only) | |
| 10. Stok | | | | ☐ | |
| 11. Discount | | | | ☐ | |

### Total Score & Verdict

| Metric | System Output | Manual Calculation | Delta | Match? |
|--------|--------------|-------------------|-------|--------|
| **Total Score** | | | | ☐ (±1 point) |
| **Verdict (F75)** | | | | ☐ (exact match) |
| **Template used** | Fashion / Non-Fashion | Fashion / Non-Fashion | | ☐ |

### Email Output Sanity Check

| Check | Result | Notes |
|-------|--------|-------|
| Email subject includes store name? | ☐ | |
| All 11 categories present in email? | ☐ | |
| Conclusion (G66) generated? | ☐ | |
| Marketing budget recommendation present? | ☐ | Only if verdict ≠ ❌ or ⭕️ |
| Closing message matches verdict? | ☐ | |

---

## 6. Discrepancy Log

Document ALL discrepancies found between system output and manual calculations.

| # | Calculator | Field | Expected Value | Actual Value | Delta | Severity | Root Cause | GitHub Issue |
|---|-----------|-------|---------------|--------------|-------|----------|------------|-------------|
| 1 | | | | | | Critical / Minor / Cosmetic | | |
| 2 | | | | | | | | |
| 3 | | | | | | | | |
| 4 | | | | | | | | |
| 5 | | | | | | | | |

### Severity Definitions

| Severity | Definition | Action Required |
|----------|-----------|-----------------|
| **Critical** | Output is materially wrong; affects scoring/verdict; blocks launch | Create GitHub issue with `bug/critical` label → fix → re-validate |
| **Minor** | Output differs slightly beyond tolerance but does not affect verdict | Document; fix in future sprint if feasible |
| **Cosmetic** | Display/formatting difference only; no impact on data or scoring | Document; low-priority fix |

---

## 7. Overall Validation Result

| Criteria | Met? |
|----------|------|
| All 4 files uploaded successfully | ☐ |
| All 3 calculators executed without error | ☐ |
| Ads Keyword output matches manual | ☐ |
| Discount Check output within tolerance | ☐ |
| Top SKU output within tolerance | ☐ |
| Final score within ±1 point | ☐ |
| Verdict agrees (exact match) | ☐ |
| Zero critical discrepancies | ☐ |
| Evaluation saved to history | ☐ |

**Validation Result:** PASS / FAIL

**Notes:**

---

**Validated by:** ____________________
**Date:** ____________________
