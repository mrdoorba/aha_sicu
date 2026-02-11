# AHA Store ICU — System Overview

This system analyzes a Shopee store's health and produces a scored report with actionable recommendations.

---

## Files in This Spec

| File | Purpose |
|------|---------|
| `calculator-1-kata-kunci-iklan-shopee.md` | Ad keyword & placement analysis |
| `calculator-2-penjualan.md` | Sales & stock analysis |
| `calculator-3-discount-checkup.md` | Discount health analysis |
| `scoring-system-template-sicu.md` | Main scoring sheet that combines everything |

---

## Data Flow

```
INPUT FILES                    CALCULATORS                 SCORING SYSTEM
─────────────                  ───────────                 ──────────────

Ad Keyword CSV ──────────►  Calculator 1  ──► G53 (text)
Ad Overview CSV ─────────►  (Kata Kunci)       │
                                               │
Order Export XLSX ───────►  Calculator 2  ──► D70 (avg stock number)
Mass Update XLSX ────────►  (Penjualan)        │
                                               ├──►  Template SICU
Order Export XLSX ───────►  Calculator 3  ──► D73 (text)     │
(same file as Calc 2)       (Disc Check)       │             │
                                               │             ▼
Manual inputs ─────────────────────────────────────►  Total Score (H4)
(store metrics from                                   Email (G1)
 Shopee Seller Center)                                WhatsApp (E1)
```

---

## Calculator → Scoring Connections

| Calculator | Output | Destination Cell | What Happens |
|-----------|--------|-----------------|--------------|
| Calculator 1 | Combined text (Sheet 1 + Sheet 2 results) | **G53** | Included in email, no score |
| Calculator 2 | Average stock number | **D70** | Scored: ≥24=10pts, ≥12=5pts, <12=-5pts |
| Calculator 3 | Full text (% Diskon, Range, Voucher, Paket, flag) | **D73** | Parsed for marketing %, scored: no fake discount=5pts |

---

## Input Files Summary

| File | Used By | Key Columns |
|------|---------|-------------|
| Shopee Ad Keyword Placement CSV | Calculator 1 Sheet 2 | Kata Kunci, Biaya, Klik, Pesanan, Penjualan |
| Shopee Ad Overview CSV | Calculator 1 Sheet 1 | Status, Jenis Iklan, Mode Bidding, Penempatan Iklan |
| Shopee Order Export XLSX | Calculator 2, Calculator 3 | Nama Produk, Harga Awal, Harga Setelah Diskon, Jumlah, Voucher, etc. |
| Shopee Mass Update XLSX | Calculator 2 | Kode Variasi, SKU, Stok, Harga |

---

## Manual Inputs in Scoring System

These values are entered manually from Shopee Seller Center (not from calculators):

- Rows 7-11: Operational health (order issues, shipping, packaging, chat, ratings)
- Rows 13-18: Monthly sales for 6 months
- Row 20: Conversion rate
- Rows 22-23: Content quality counts
- Rows 26-27, 29: Visitor and follower counts
- Rows 31-41: Revenue per promotion tool
- Row 45: Product count
- Row 46: Store status (Mall/Star+/etc.)
- Rows 48-49: Ad revenue and cost
- Rows 55-56: Campaign sessions
- Rows 61-63: Top product competition data (prices, keywords, market prices)
- G2: Store name
- G5: Category
- F75: Final verdict
