# BD Team Onboarding Guide — AHA Store ICU

Welcome to the AHA Store Internal Check Up (Store ICU) production system. This guide walks you through every step of the evaluation workflow, from logging in to saving your final assessment.

> **Quick Reference:** For a streamlined 10-step walkthrough checklist, see [`smoke-tests/MANUAL_CHECKLIST.md`](../smoke-tests/MANUAL_CHECKLIST.md).

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Brand Data & Sync](#2-brand-data--sync)
3. [Starting an Evaluation](#3-starting-an-evaluation)
4. [File Upload Guide](#4-file-upload-guide)
5. [Manual Data Entry](#5-manual-data-entry)
6. [Understanding Calculator Results](#6-understanding-calculator-results)
7. [Final Scoring & Verdict](#7-final-scoring--verdict)
8. [Saving & History](#8-saving--history)
9. [FAQ & Troubleshooting](#9-faq--troubleshooting)

---

## 1. Getting Started

### Production URL

Open your browser and navigate to:

```
https://aha-sicu-prod.web.app
```

### How to Log In

1. You will see the **login page** with email and password fields.
2. Enter the **email address** and **initial password** provided by your team leader.
3. Click **Login**.
4. On successful login, you will be redirected to the **Brands page** (the main dashboard).
5. Your **email address** is displayed in the header to confirm you are logged in.

### First-Time Login

- The first time you log in, the system automatically creates your user profile in the database.
- Your default role is `member`. The team leader has `leader` role and the system owner has `admin` role.
- No additional setup is needed — you can start evaluating brands immediately.

### Password Reset

If you forget your password:

1. On the login page, click **Forgot Password** (or ask your system administrator).
2. Enter your registered email address.
3. Firebase sends a password reset email — check your inbox (and spam folder).
4. Click the reset link and set a new password (minimum 6 characters).

### Recommended Setup

- **Browser:** Use Chrome or Edge for best compatibility.
- **Screen size:** Desktop or laptop recommended (the evaluation workflow has wide tables).
- **Network:** No VPN required — the production system is publicly accessible.

---

## 2. Brand Data & Sync

### Navigating to the Brands Page

After logging in, you land on the **Brands page** (`/brands`). This page displays all brands synced from the master Google Sheet.

### Understanding Sync Status

Each brand row shows:

| Column | Description |
|--------|-------------|
| **Brand Name** | The store/brand name from the master sheet |
| **Category** | Fashion or Non-Fashion classification |
| **Last Synced** | Timestamp of the most recent data sync |

The page header shows the **overall sync status** — when the last successful sync occurred.

### Triggering a Manual Sync

1. Click the **Sync** button (usually at the top of the brands page).
2. A progress indicator appears — you'll see toast notifications as the sync progresses.
3. Wait for the **sync complete** notification.
4. The brand list refreshes automatically with the latest data.

> **Note:** Brands are synced from the master Google Sheet. If a brand is missing, verify it exists in the source spreadsheet first, then trigger a sync.

### Searching for a Brand

Use the **search bar** at the top of the brands page:

- Type part of a brand name (e.g., "MOON" to find "MOON DAE Official Store").
- The list filters in real-time as you type.
- Search is case-insensitive.

---

## 3. Starting an Evaluation

### Selecting a Brand

1. On the Brands page, find the brand you want to evaluate.
2. Click on the brand row or the **Start Evaluation** button.
3. The system creates a new evaluation and navigates you to the **Evaluation page**.

### Understanding the Evaluation Page Layout

The evaluation page is organized into these main areas:

| Area | Purpose |
|------|---------|
| **Brand Header** | Shows the selected brand name, category, and evaluation metadata |
| **File Upload Slots** | 4 upload areas — one for each required file type (see [Section 4](#4-file-upload-guide)) |
| **Manual Data Input** | Form fields organized by scoring category (see [Section 5](#5-manual-data-entry)) |
| **Calculator Results** | Output from the 3 automated calculators (see [Section 6](#6-understanding-calculator-results)) |
| **Final Score & Verdict** | Total score, per-category breakdown, and verdict (see [Section 7](#7-final-scoring--verdict)) |

The workflow follows a linear sequence:

```
Upload Files → Enter Manual Data → Review Calculator Results → Generate Final Score → Save
```

---

## 4. File Upload Guide

You need to upload **4 files** exported from Shopee Seller Center for the brand being evaluated. Each file feeds into specific calculators.

### Overview

| # | File Type | Format | Used By |
|---|-----------|--------|---------|
| 1 | CPC Ad Report | CSV | Ads Keyword Calculator |
| 2 | Keyword Report | CSV | Ads Keyword Calculator |
| 3 | Order Export | XLSX | Discount Check + Top SKU Calculators |
| 4 | Mass Update (Sales Info) | XLSX | Top SKU Calculator |

### How to Upload

1. Click the **upload area** for the corresponding file slot.
2. Select the file from your computer.
3. Wait for the upload to complete — a success indicator appears when done.
4. Repeat for all 4 file types.

Files are uploaded via signed URLs to cloud storage and automatically processed by the backend.

> **Tip:** Upload all 4 files before entering manual data. The calculators can auto-execute once all required files are present.

---

### File 1: CPC Ad Report (CSV)

**Source:** Shopee Seller Center → Iklan Shopee → Unduh Laporan → Laporan Iklan CPC

**Required Columns:**

| Column Name | Description | Example Values |
|-------------|-------------|----------------|
| `Status` | Ad status | "Berjalan", "Dijeda", "Berakhir" |
| `Jenis Iklan` | Ad type | "Iklan Produk", "Iklan Toko" |
| `Nama Iklan` | Ad/product name | "Dress Wanita Casual [Kode: ABC]" |
| `Penempatan Iklan` | Ad placement | "Halaman Pencarian", "Halaman Rekomendasi", "Semua Penempatan" |
| `Mode Bidding` | Bidding mode | "Otomatis", "Manual" |

**Notes:**
- Product names with `[` brackets are automatically cleaned (text after `[` is removed).
- All rows are used — active, paused, and ended ads each contribute to different metrics.

---

### File 2: Keyword Report (CSV)

**Source:** Shopee Seller Center → Iklan Shopee → Unduh Laporan → Laporan Kata Kunci/Penempatan

**Required Columns:**

| Column Name | Description | Example Values |
|-------------|-------------|----------------|
| `Nama Iklan` | Ad name | "Dress Wanita Casual" |
| `Jenis Iklan` | Ad type (empty = shop-level) | "" or "Iklan Produk" |
| `Omzet Penjualan` | GMV / sales revenue | 5250000 |
| `Efektifitas Iklan` | ROAS (return on ad spend) | 8.5 |
| `Biaya` | Ad cost | 617647 |
| `Mode Bidding` | Bidding mode | "Otomatis", "Manual" |
| `Penempatan Iklan` | Placement | "Halaman Pencarian" |
| `Kata Pencarian/Penempatan` | Keyword text | "dress wanita" |

**Notes:**
- When `Jenis Iklan` is empty, it indicates a shop-level ad (vs. product-level).
- ROAS and cost values are used to rank top and bottom performing ads.

---

### File 3: Order Export (XLSX)

**Source:** Shopee Seller Center → Pesanan Saya → Export → Pesanan Selesai

**Required Columns:**

| Column Name | Description | Example Values |
|-------------|-------------|----------------|
| `No. Pesanan` | Order number | "2401150ABCDEFG" |
| `Nama Produk` | Product name | "Dress Wanita Casual" |
| `Nama Variasi` | Variant name | "Merah - M" |
| `Nomor Referensi SKU` | SKU reference | "DWC-RED-M" |
| `Harga Awal` | Original price | "125.000" |
| `Harga Setelah Diskon` | Discounted price | "99.000" |
| `Jumlah` | Quantity per line item | 2 |
| `Jumlah Produk di Pesan` | Total items in order | 3 |
| `Voucher Ditanggung Penjual` | Seller-borne voucher | "15.000" |
| `Cashback Koin` | Coin cashback | "5.000" |
| `Diskon Dari Shopee` | Shopee-subsidized discount | "0" |
| `Paket Diskon (Diskon dari Penjual)` | Seller bundle discount | "10.000" |

**Important — Indonesian number format:**
- Prices use `.` (dot) as thousands separator: `125.000` = Rp 125,000.
- The system automatically converts this format during processing.
- Do NOT modify the exported file — upload as-is from Shopee.

---

### File 4: Mass Update / Sales Info (XLSX)

**Source:** Shopee Seller Center → Produk Saya → Mass Update → Download File

**Required Columns (headers at row 3):**

| Column Name | Description | Example Values |
|-------------|-------------|----------------|
| `Nama Produk` | Product name | "Dress Wanita Casual" |
| `Nama Variasi` | Variant name | "Merah - M" |
| `Kode Variasi` | Variant code (unique ID) | "DWC-RED-M-001" |
| `Stok` | Current stock level | 45 |

**Notes:**
- This file provides stock data for the Top SKU calculator.
- Headers are on **row 3** (not row 1) — the system accounts for this.
- The `Kode Variasi` is used as the unique product identifier in output tables.
- If a product's Kode Variasi cannot be matched, the system shows "Kode Variasi tidak ditemukan".

---

## 5. Manual Data Entry

After uploading files, enter manual data for each scoring category. These values come from the brand's Shopee Seller Center dashboard and analytics.

### Important Conventions

| Convention | Rule | Example |
|------------|------|---------|
| **Percentages** | Enter as-is: `0.5` means **0.5%** (not 50%) | Tingkat Keterlambatan = `0.8` means 0.8% |
| **Currency (IDR)** | Enter the number without formatting | `26433781` for Rp 26,433,781 |
| **Counts** | Enter whole numbers | `150` for 150 products |
| **Ratings** | Enter with decimals | `4.85` for a 4.85 star rating |

> **Warning:** The most common mistake is percentage entry. Remember: `0.5` = 0.5%, NOT 50%. If the Shopee dashboard shows "0.8%", enter `0.8`.

---

### Fields by Scoring Category

#### Category 1: Kesehatan Operasional Toko (Store Operational Health)

| Field | Indonesian Label | Input Type | Benchmark | Where to Find |
|-------|-----------------|------------|-----------|---------------|
| Tingkat Pesanan Tidak Terselesaikan | Pesanan Tidak Terselesaikan | % (decimal) | < 1% | Seller Center → Performa Toko |
| Tingkat Keterlambatan Pengiriman | Keterlambatan Pengiriman | % (decimal) | < 1% | Seller Center → Performa Toko |
| Masa Pengemasan | Waktu Pengemasan | Days (decimal) | < 1 day | Seller Center → Performa Toko |
| Persentase Chat Dibalas | Chat Dibalas | % (integer) | > 95% | Seller Center → Performa Toko |
| Keseluruhan Penilaian | Rating Toko | Rating (decimal) | > 4.7 | Store page → overall rating |

#### Category 2: Bisnis Analisis (Business Analysis)

| Field | Indonesian Label | Input Type | Benchmark | Where to Find |
|-------|-----------------|------------|-----------|---------------|
| Penjualan (current month) | Omzet bulan ini | IDR | > 6-month avg | Seller Center → Bisnis Saya |
| Penjualan (past 5 months) | Omzet 5 bulan sebelumnya | IDR × 5 fields | — | Seller Center → Bisnis Saya |
| Tingkat Konversi | Conversion Rate | % (decimal) | > 2% (Fashion) / > 3% | Seller Center → Bisnis Saya |

> **Note:** Enter 6 months of sales data (current + 5 previous). The system calculates the 6-month average automatically.

#### Category 3: Tinjauan Pengunjung (Visitor Overview)

| Field | Indonesian Label | Input Type | Benchmark | Where to Find |
|-------|-----------------|------------|-----------|---------------|
| Total Pengunjung | Pengunjung total | Count | — | Seller Center → Bisnis Saya → Pengunjung |
| Pengunjung Lama | Returning visitors | Count | — | Seller Center → Bisnis Saya → Pengunjung |
| Total Pengikut | Followers | Count | > 50,000 | Store page → follower count |

The system calculates `% Pengunjung Lama` automatically (benchmark: > 23%).

#### Category 4: Promo Toko (Store Promotions)

Enter **revenue generated** (IDR) by each promotional tool:

| Tool | Indonesian Label | Benchmark | Where to Find |
|------|-----------------|-----------|---------------|
| Promo Toko | Revenue dari Promo Toko | 8% of sales | Seller Center → Marketing Center |
| Paket Diskon | Revenue dari Paket Diskon | 16% of sales | Seller Center → Marketing Center |
| Kombo Hemat | Revenue dari Kombo Hemat | 1% of sales | Seller Center → Marketing Center |
| Flash Sale Toko Saya | Revenue dari Flash Sale | 1% of sales | Seller Center → Marketing Center |
| Voucher | Revenue dari Voucher | 84% of sales | Seller Center → Marketing Center |
| Shopee Live | Revenue dari Shopee Live | 15% of sales | Seller Center → Marketing Center |
| Game Toko | Revenue dari Game Toko | 1% of sales | Seller Center → Marketing Center |
| Brand Membership | Revenue dari Brand Membership | 1% of sales | Seller Center → Marketing Center |
| Gratis Ongkir XTRA | Revenue dari Gratis Ongkir | Any > 0 | Seller Center → Marketing Center |
| Chat Broadcast | Revenue dari Chat Broadcast | 1% of sales | Seller Center → Marketing Center |
| Program Afiliasi | Revenue dari Afiliasi | 18% of sales | Seller Center → Marketing Center |

> **Note:** Enter `0` if the brand does not use a particular promotional tool. The system counts usage and effectiveness percentages automatically.

#### Category 5: Jumlah Produk & Status Toko (Products & Store Status)

| Field | Indonesian Label | Input Type | Benchmark | Where to Find |
|-------|-----------------|------------|-----------|---------------|
| Jumlah Produk | Total active products | Count | >= 35 | Seller Center → Produk Saya |
| Status Toko | Store badge level | Text | "Shopee Mall" | Store page |

Valid values for Status Toko: `Shopee Mall`, `Star+`, or other text.

#### Category 6: Data Iklan (Advertising Data)

| Field | Indonesian Label | Input Type | Benchmark | Where to Find |
|-------|-----------------|------------|-----------|---------------|
| Penjualan (iklan) | GMV from ads | IDR | — | Seller Center → Iklan Shopee → Ringkasan |
| Biaya (iklan) | Total ad spend | IDR | — | Seller Center → Iklan Shopee → Ringkasan |

The system auto-calculates ROI (benchmark: > 8 Fashion / > 9 Non-Fashion), % GMV Iklan, and % Biaya Iklan.

#### Category 7: Partisipasi Campaign (Campaign Participation)

| Field | Indonesian Label | Input Type | Benchmark | Where to Find |
|-------|-----------------|------------|-----------|---------------|
| Sesi dinominasikan | Nominated sessions | Count | — | Seller Center → Marketing Center → Campaign |
| Sesi tersedia | Available sessions | Count | — | Seller Center → Marketing Center → Campaign |

The system calculates `% Partisipasi Campaign` (benchmark: > 90%).

#### Category 8: Kompetisi TOP Produk (Top Product Competition)

For the top 3 products (from Calculator 2 output):

| Field | Indonesian Label | Input Type | Where to Find |
|-------|-----------------|------------|---------------|
| Product name | Nama Produk (top 3) | Text | Auto-filled from calculator |
| Search keyword | Kata kunci pencarian | Text | Your market research |
| Market average price | Harga rata-rata pasar | IDR | Search Shopee for comparable products |

#### Category 10-11: Stok & Discount

These categories use **calculator outputs** — no manual data entry needed:
- **Stok** (Row 70): Uses average stock from Top SKU Calculator
- **Discount** (Row 73): Uses Discount Check Calculator output text

---

## 6. Understanding Calculator Results

After files are uploaded and processed, the system runs **3 calculators** automatically. Here's how to read each output.

### Calculator 1: Ads Keyword (Iklan Kata Kunci)

This calculator analyzes CPC ad performance. The output is a **text narrative** with multiple sections:

#### AK2 — Ad Overview

Shows a summary of your advertising activity:

```
Dari total X iklan (Y berjalan, Z dijeda, W berakhir),
N produk (P%) dari total Q produk aktif beriklan.
```

- **X** = Total ads across all statuses
- **Y/Z/W** = Count by status (running/paused/ended)
- **N** = Unique products with active ads
- **P%** = Product participation rate (ideally > 50%)

#### AK3 — Ad Type Breakdown

Details how ads are distributed across placement types:

- **Halaman Pencarian** (Search Page): Manual vs automatic bidding counts
- **Halaman Rekomendasi** (Recommendation Page): Manual vs automatic counts
- **Semua Penempatan** (All Placements): Total count
- **Iklan Toko** (Shop Ads): Manual vs automatic counts

#### AK4 — Seven Recommendation Flags

Seven yes/no assessments. Each flag identifies an area for improvement:

| Flag | Checks For |
|------|-----------|
| 1 | Product participation < 50% |
| 2 | Active ad ratio < 50% |
| 3 | Search page ads not used at all |
| 4 | No manual bidding on search page |
| 5 | Recommendation page ads not used |
| 6 | No manual bidding on recommendation page |
| 7 | Shop ads not used |

#### Top & Bottom Keyword Lists

- **TOP Ads** (AL2): Best-performing ads ranked by GMV and ROAS. Shows ad name, revenue, ROAS, bidding mode, and keyword.
- **BOTTOM Ads** (AL5): Worst-performing ads with high cost but low ROAS. These are candidates for optimization or pausing.

---

### Calculator 2: Top SKU (Penjualan / Sales)

This calculator ranks products by revenue and provides stock analysis. Output is displayed as **tables** (not text).

#### Revenue Ranking Table (Output 1)

| Column | Description |
|--------|-------------|
| **Kode Variasi** | Unique product variant code |
| **Product Name** | Product + variant name |
| **Total Omzet** | Total revenue (IDR, rounded) |
| **Rata-rata Harga Jual** | Average selling price (IDR, rounded) |

The table shows the **top 20%** of products by revenue (minimum 20 products if enough exist).

#### Stock Ranking Table (Output 2)

| Column | Description |
|--------|-------------|
| **Kode Variasi** | Variant code |
| **Nama Produk** | Product name |
| **Varian** | Variant name |
| **Stok** | Current stock level |

#### Average Stock

A single number shown below the tables — the mean stock level across all top products. This feeds into the Stok scoring category:
- ≥ 24 units average = Excellent (10 points)
- ≥ 12 units average = Good (5 points)
- < 12 units average = Low (-5 points penalty)

---

### Calculator 3: Discount Check (Pengecekan Diskon)

This calculator analyzes discount patterns and detects potential abuse. Output is a **4-5 line text block**:

```
% Diskon TOP SKU: 12.5%
Range: 8.2% ~ 15.3%
Voucher 3.9%
Paket Diskon 0.2%
📌 Berpotensi menggunakan 'fake discount'     ← only appears if flagged
```

| Line | What It Means |
|------|---------------|
| **% Diskon TOP SKU** | Overall discount rate on top-selling products |
| **Range** | Min ~ Max discount percentage range across products |
| **Voucher** | Seller-borne voucher as % of discounted sales |
| **Paket Diskon** | Bundle discount as % of discounted sales |
| **Fake discount flag** | Appears if total discount exceeds 20% of total paid — indicates potential fake discount usage |

**Validation tolerances** (expected variance from manual Google Sheets calculation):
- Discount percentages: ±0.5%
- Stock averages: ±2 units
- Final score: ±1 point

---

## 7. Final Scoring & Verdict

### How Scoring Works

The system scores the brand across **11 categories**, producing a total score that determines the verdict.

### Per-Category Score Breakdown

| Category | Max Points | Type |
|----------|-----------|------|
| 1. Kesehatan Operasional Toko | 10 | Penalty (deducted if fail) |
| 2. Bisnis Analisis | 20 | Performance |
| 3. Tinjauan Pengunjung | 5 | Performance |
| 4. Promo Toko | 15 | Opportunity (earned on fail) |
| 5. Jumlah Produk & Status | 15 | Performance |
| 6. Data Iklan | 10 | Mixed |
| 7. Partisipasi Campaign | 10 | Opportunity |
| 8. Kompetisi TOP Produk | 0 | Informational only |
| 9. Stok | 10 | Performance + penalty |
| 10. Discount | 5 | Performance |

> **Important — "Opportunity" scoring:** Categories 5, 7 (partial), and 8 award points when the brand **fails** the benchmark. This is because under-performance represents a business opportunity for AHA to help improve the brand. Higher total score = more attractive prospect for partnership.

### Category Adjustments

The unified "default" template adjusts scoring based on the brand's category type:

| Aspect | Fashion | Non-Fashion |
|--------|---------|-------------|
| Conversion rate benchmark | > 2% | > 3% |
| Ad ROI benchmark | > 8 | > 9 |
| Marketing floor | 15% | 12% |
| Marketing ceiling | 25% | 20% |

### Verdict Meanings

The final verdict is set in cell F75:

| Verdict | Symbol | Meaning |
|---------|--------|---------|
| Approved | ✔️ | Good candidate — potential not yet maximized, invite to consultation |
| Rejected | ❌ | Needs to reconsider profit potential — suggest AHA Coventures |
| Non Mall | ❌ Non Mall | Not a Shopee Mall store — offer Mall application assistance |
| No Brand | ❌ No Brand | Not a brand store — polite decline |
| Opex Issues | ❌ Opex | Operational issues too severe — ask to fix shipping/packaging first |
| Neutral | ⭕️ | No recommendation |
| Empty | (blank) | Performance already good — polite acknowledgment |

### Email Output

After scoring, the system generates:

- **Email body:** A formatted report covering all 11 categories with emoji headers, benchmarks, and the conclusion. Subject line: "🏥 AHA Store Internal Check Up (Store ICU) - [Store Name] [Period]"

---

## 8. Saving & History

### Saving an Evaluation

1. After reviewing the final score and verdict, click **Save Evaluation**.
2. A success message confirms the evaluation has been saved.
3. The evaluation is now permanent and appears in the History page.

> **Note:** Saved evaluations cannot be edited. If you need to re-evaluate, start a new evaluation for the same brand.

### Viewing History

1. Navigate to the **History page** (`/history`).
2. The list shows all saved evaluations, newest first.

Each row displays:
- **Brand name**
- **Evaluation date**
- **Final score**
- **Verdict**

### Searching by Brand Name

- Use the **search bar** at the top of the History page.
- Type part of the brand name to filter results.
- Search is case-insensitive and matches partial names.

### Filtering by Date Range

- Use the **date picker** controls to set a "from" and "to" date.
- The list filters to show only evaluations within the selected range.

### Filtering by Category

- Use the **category filter** to show only Fashion or Non-Fashion evaluations.

### Evaluation Detail View

1. Click on any evaluation in the history list.
2. The detail view shows:
   - All input data (manual fields + uploaded file summaries)
   - Calculator results (all 3 calculator outputs)
   - Per-category scores with benchmarks and verdicts
   - Final score and overall verdict
   - Generated email body

---

## 9. FAQ & Troubleshooting

### Login Issues

**Q: I can't log in — "Invalid email or password"**
- Double-check your email address (case-sensitive).
- Ensure you're using the password provided by your team leader.
- If you've changed your password and forgotten it, use the password reset flow.
- Contact the system administrator if the problem persists.

**Q: I get redirected back to the login page after logging in**
- Clear your browser cookies and cache, then try again.
- Ensure you're using the production URL: `https://aha-sicu-prod.web.app`
- Try a different browser or incognito/private window.

---

### Upload Issues

**Q: File upload fails with an error**
- Verify the file format matches exactly: CSV for ad/keyword reports, XLSX for order/mass update.
- Ensure the file is not corrupted — try re-downloading from Shopee Seller Center.
- Check the file size — very large files may take longer to upload.
- Ensure you have a stable internet connection.

**Q: "Column not found" error after upload**
- The file may be missing required columns. Compare your file's header row against the [File Upload Guide](#4-file-upload-guide) above.
- Shopee may have changed column names in their export. Contact the system administrator.

**Q: I uploaded the wrong file**
- Re-upload the correct file to the same slot — it will replace the previous upload.

---

### Sync Issues

**Q: Brand sync is stuck or taking too long**
- Wait at least 60 seconds — large brand lists take time to sync.
- If no progress after 2 minutes, refresh the page and try again.
- Check if the master Google Sheet is accessible (not restricted/deleted).

**Q: A brand I expect to see is not in the list**
- Verify the brand exists in the master Google Sheet.
- Trigger a manual sync to pull the latest data.
- Brand names must match exactly between the sheet and the system.

---

### Scoring Questions

**Q: Why does a failing metric INCREASE the total score?**
- Categories like Promo Toko and Campaign Participation use **opportunity scoring**. A failing metric means there's room for improvement — this makes the brand a more attractive prospect for AHA's services. Higher score = more potential value AHA can add.

**Q: The percentage I entered seems wrong in the results**
- Remember the percentage convention: `0.5` = 0.5%. If you entered `50` thinking it means 50%, the system interprets it as 5000%. Always enter the number as it appears in Shopee (e.g., if Shopee shows 0.8%, enter `0.8`).

**Q: Calculator results don't match my manual spreadsheet exactly**
- Small variances are expected due to floating-point arithmetic differences between the system (Python/Polars) and Google Sheets (Excel engine). Accepted tolerances: percentages ±0.5%, stock ±2 units, final score ±1 point.
- If the difference exceeds these tolerances, document it in the [validation report](validation-report-template.md).

**Q: What does the "fake discount" flag mean?**
- This appears when the total discount percentage exceeds 20% of total paid amount. It indicates the brand may be using artificially inflated original prices to create an illusion of large discounts — a practice Shopee discourages.

---

### General Issues

**Q: The page is slow or unresponsive**
- Refresh the browser page.
- Check your internet connection.
- Try clearing browser cache.
- If the problem persists across all users, the backend service may need attention — contact the system administrator.

**Q: I see stale/old data**
- Trigger a manual sync from the Brands page.
- Refresh the browser page after sync completes.

**Q: Can I evaluate the same brand twice?**
- Yes. Each evaluation is independent and saved separately in history. This is useful for tracking brand performance over time (e.g., monthly evaluations).

---

## Quick Reference Links

| Resource | Path |
|----------|------|
| Production Frontend | https://aha-sicu-prod.web.app |
| Manual Smoke Test Checklist | [`smoke-tests/MANUAL_CHECKLIST.md`](../smoke-tests/MANUAL_CHECKLIST.md) |
| Validation Report Template | [`docs/validation-report-template.md`](validation-report-template.md) |
| Launch Readiness | [`docs/launch-readiness.md`](launch-readiness.md) |
