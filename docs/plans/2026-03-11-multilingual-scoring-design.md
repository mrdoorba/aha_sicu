# Multilingual Scoring Engine — Design Document

**Date:** 2026-03-11
**Status:** Approved
**Approach:** Structured data (translation keys + variables) stored in JSONB

---

## Problem

The frontend i18n system supports ID/EN/TH for UI labels, but all backend-generated text (scoring verdicts, ad analysis, conclusions, recommendations) is hardcoded in Indonesian. When users switch language via toggle, these sections remain in Indonesian.

## Solution

Replace pre-rendered Indonesian text with **structured translatable data** (`translation key + variables + Indonesian fallback`). The frontend renders the final text using i18next based on the user's language preference.

### Why This Approach

- **Adding a new language** = add a frontend translation file only. Zero backend/DB changes.
- **Fixing a translation** = update translation file, deploy frontend only.
- **No storage bloat** — one set of structured data serves all languages.
- **No DB migration** — all scoring data lives in JSONB columns; we add keys, not columns.

---

## Architecture

```
Scoring Engine (backend)
  Currently: { "message": "✔️ Masa Pengemasan = 0.56 hari [Sudah Baik]" }
  New:       { "message": "✔️ Masa Pengemasan = 0.56 hari [Sudah Baik]",
               "message_i18n": { "key": "scoring.preparationTime.pass",
                                 "vars": { "value": "0.56" } } }

Frontend (i18next)
  en.json → "scoring.preparationTime.pass": "✔️ Preparation Time = {{value}} days [Good]"
  th.json → "scoring.preparationTime.pass": "✔️ ระยะเวลาจัดเตรียม = {{value}} วัน [ดี]"
  id.json → "scoring.preparationTime.pass": "✔️ Masa Pengemasan = {{value}} hari [Sudah Baik]"

Display logic:
  if (field_i18n) → t(field_i18n.key, field_i18n.vars)
  else            → field (raw Indonesian fallback)
```

---

## Dual-Format Storage (Backward Compatible)

Every text field gets a companion `_i18n` field:

```python
@dataclass
class TranslatableText:
    key: str              # i18n translation key
    vars: dict[str, str]  # interpolation variables

@dataclass
class RowScore:
    metric: str                              # "Masa Pengemasan" (fallback)
    metric_i18n: TranslatableText | None     # { key, vars }
    message: str                             # "✔️ Masa Pengemasan = 0.56 hari [Sudah Baik]" (fallback)
    message_i18n: TranslatableText | None    # { key, vars }
    benchmark: str                           # "<1" (fallback)
    benchmark_i18n: TranslatableText | None  # { key, vars }
    # ... existing fields unchanged
```

**Why dual-format:**
- Old evaluations (no `_i18n` fields) → frontend shows Indonesian fallback. No crash.
- New evaluations → frontend uses `_i18n` for translated rendering.
- Works on both dev and prod regardless of data state.

---

## Deploy Strategy (Dev & Prod Safe)

```
Phase 1: Ship new system
  ├── Backend: scoring engine writes dual format (text + _i18n)
  ├── Frontend: renderTranslatable() helper + new translation keys
  ├── New evaluations get full translation support immediately
  └── Old evaluations gracefully fall back to Indonesian text

Phase 2: Backfill existing data (separate task, per-environment)
  ├── Script reads existing evaluations, re-runs scoring engine on stored inputs
  ├── Writes _i18n fields alongside existing text (additive, non-destructive)
  ├── Idempotent (skips if _i18n already exists)
  ├── Run on dev first → verify → run on prod
  └── All evaluations now support language switching
```

**No database migration needed** — all data lives in JSONB columns (`evaluations.score_breakdown`, `evaluations.calculator_results`, `calculator_results.details`).

---

## Complete Scope — Backend Text Inventory

### 1. Per-Row Scoring Messages (`messages.py`)

#### Operational Health (Rows 7-11)

| Row | Metric Key | Indonesian Metric Name |
|-----|-----------|----------------------|
| 7 | `scoring.unfulfilledOrderRate` | Tingkat Pesanan Tidak Terselesaikan |
| 8 | `scoring.lateShipmentRate` | Tingkat Keterlambatan Pengiriman |
| 9 | `scoring.preparationTime` | Masa Pengemasan |
| 10 | `scoring.chatResponseRate` | Persentase Chat Dibalas |
| 11 | `scoring.overallRating` | Keseluruhan Penilaian |

#### Business Analysis (Rows 13-20)

| Row | Metric Key | Indonesian Metric Name |
|-----|-----------|----------------------|
| 13 | `scoring.monthlySales` | Penjualan Bulan |
| 20 | `scoring.conversionRate` | Tingkat Konversi |

#### Visitor Review (Rows 28-29)

| Row | Metric Key | Indonesian Metric Name |
|-----|-----------|----------------------|
| 28 | `scoring.returningVisitorPct` | % Pengunjung Lama |
| 29 | `scoring.totalFollowers` | Total Pengikut |

#### Promo Tools (Rows 31-43)

| Row | Metric Key | Indonesian Metric Name |
|-----|-----------|----------------------|
| 31 | `scoring.promoShopPromo` | Promo Toko |
| 32 | `scoring.promoBundleDeal` | Paket Diskon |
| 33 | `scoring.promoComboSaver` | Kombo Hemat |
| 34 | `scoring.promoFlashSale` | Flash Sale Toko Saya |
| 35 | `scoring.promoVoucher` | Voucher |
| 36 | `scoring.promoShopeeLive` | Shopee Live |
| 37 | `scoring.promoShopGame` | Game Toko |
| 38 | `scoring.promoBrandMembership` | Brand Membership |
| 39 | `scoring.promoFreeShipping` | Gratis Ongkir XTRA |
| 40 | `scoring.promoChatBroadcast` | Chat Broadcast |
| 41 | `scoring.promoAffiliate` | Program Afiliasi |
| 42 | `scoring.promoUsageRate` | Penggunaan alat promosi |
| 43 | `scoring.promoEffectiveness` | Efektifitas alat promosi |

#### Products & Store (Rows 45-46)

| Row | Metric Key | Indonesian Metric Name |
|-----|-----------|----------------------|
| 45 | `scoring.productCount` | Jumlah Produk |
| 46 | `scoring.storeStatus` | Status Toko |

#### Ads Performance (Rows 50-53)

| Row | Metric Key | Indonesian Metric Name |
|-----|-----------|----------------------|
| 50 | `scoring.adsROI` | ROI |
| 51 | `scoring.adsGMVPct` | % GMV Iklan / GMV Toko |
| 52 | `scoring.adsCostPct` | % Biaya Iklan / GMV Toko |
| 53 | `scoring.adsCheckup` | Iklan check up |

#### Campaign (Row 57)

| Row | Metric Key | Indonesian Metric Name |
|-----|-----------|----------------------|
| 57 | `scoring.campaignParticipation` | % Partisipasi Campaign |

#### Competition (Rows 61-63)

| Row | Metric Key | Indonesian Metric Name |
|-----|-----------|----------------------|
| 61-63 | `scoring.competitionProduct` | (dynamic product names) |

#### Stock (Rows 70-71)

| Row | Metric Key | Indonesian Metric Name |
|-----|-----------|----------------------|
| 70 | `scoring.avgStockTop20` | Rata² Stok TOP 20% SKU |
| 71 | `scoring.stockAvailability` | % Ketersediaan Stok |

#### Discount (Row 73)

| Row | Metric Key | Indonesian Metric Name |
|-----|-----------|----------------------|
| 73 | `scoring.discountRange` | Diskon range |

### 2. Category Names (`categories.py`)

| Key | Indonesian | English | Thai |
|-----|-----------|---------|------|
| `category.operational` | Kesehatan Operasional Toko | Store Operational Health | สุขภาพการดำเนินงานร้าน |
| `category.business` | Bisnis Analisis | Business Analysis | การวิเคราะห์ธุรกิจ |
| `category.visitors` | Tinjauan Pengunjung | Visitor Review | ภาพรวมผู้เยี่ยมชม |
| `category.promo` | Promo Toko | Store Promos | โปรโมชั่นร้าน |
| `category.products` | Jumlah Produk & Status Toko | Products & Store Status | สินค้าและสถานะร้าน |
| `category.ads` | Data Iklan | Ads Data | ข้อมูลโฆษณา |
| `category.campaign` | Partisipasi Campaign | Campaign Participation | การเข้าร่วมแคมเปญ |
| `category.competition` | Kompetisi TOP Produk | TOP Product Competition | การแข่งขันสินค้ายอดนิยม |
| `category.stock` | Stok | Stock | สต็อก |
| `category.discount` | Discount | Discount | ส่วนลด |

### 3. Verdict Labels

| Key | Indonesian | English | Thai |
|-----|-----------|---------|------|
| `verdict.good` | Sudah Baik | Good | ดี |
| `verdict.bad` | Kurang Baik | Needs Improvement | ต้องปรับปรุง |
| `verdict.ok` | OK | OK | โอเค |
| `verdict.sufficient` | cukup baik | Fairly Good | ค่อนข้างดี |
| `verdict.competitive` | kompetitif | Competitive | แข่งขันได้ |
| `verdict.notCompetitive` | tidak kompetitif | Not Competitive | แข่งขันไม่ได้ |

### 4. Computed Sections (`computations.py`)

#### Conclusion (G66) — `_compute_g66()`

| Key | Indonesian Template |
|-----|-------------------|
| `conclusion.salesRange` | Omset toko di kisaran {{min}} juta - {{max}} juta per bulan sejak 6 bulan terakhir |
| `conclusion.operationalGood` | Kualitas operasional toko sudah cukup baik |
| `conclusion.operationalChatIssue` | ...hanya tingkat response chat masih dapat ditingkatkan |
| `conclusion.productNaming` | Nama produk disarankan untuk dimulai dengan nama brand |
| `conclusion.photoBackground` | Background foto utama disarankan warna putih |
| `conclusion.promoUnderutilized` | Beberapa fitur promosi masih belum dimanfaatkan secara efektif |
| `conclusion.campaignLow` | Partisipasi Campaign Shopee belum maksimal |
| `conclusion.stockNotArchived` | Banyak produk habis stok tidak diarsipkan |
| `conclusion.unsoldProducts` | Banyak produk tidak terjual di 30 hari terakhir |
| `conclusion.discountRange` | Diskon range: {{min}} ~ {{max}} |
| `conclusion.fakeDiscount` | Berpotensi menggunakan 'fake discount' |

#### Marketing Budget (G73) — `_compute_g73()`

| Key | Indonesian Template |
|-----|-------------------|
| `marketing.budgetRecommendation` | Minimum anggaran marketing yang dibutuhkan AHA untuk meningkatkan performa omzet penjualan toko = {{pct}} |

#### Closing Message (G75) — `_compute_g75()`

| Key | Indonesian Template |
|-----|-------------------|
| `closing.potential` | Kami melihat bahwa potensi dari Toko {{store}} masih belum maksimal... |
| `closing.valueAdd` | Kami sangat yakin bahwa sistem AHA dapat memberikan nilai tambah... |
| `closing.directAnalysis` | Kami telah melakukan analisa pada toko {{store}} secara langsung... |
| `closing.experience` | Melalui pengalaman kami dengan ratusan toko online... |

### 5. Ads Keyword Calculator (`ads_keyword.py`)

| Key | Indonesian Template |
|-----|-------------------|
| `ads.summary` | Total Iklan: {{active}} Aktif, {{paused}} Dijeda dan {{ended}} Berakhir |
| `ads.productCoverage` | Melibatkan {{count}} ({{pct}}%) produk dari total jumlah produk: {{total}} |
| `ads.activeTypes` | Jenis Iklan yang aktif digunakan: ... |
| `ads.productParticipationLow` | Jumlah produk yang dipartisipasikan ke dalam iklan kurang maksimal |
| `ads.productParticipationGood` | Jumlah produk yang dipartisipasikan ke dalam iklan sudah cukup baik |
| `ads.activeAdsGood` | Jumlah iklan dengan status aktif sudah cukup baik |
| `ads.topAdsHeader` | TOP Iklan (GMV tertinggi dengan ROAS terbaik): |
| `ads.bottomAdsHeader` | BOTTOM Iklan (biaya tertinggi dengan ROAS terendah): |
| `ads.autoSettingWarning` | Iklan dengan performa terbaik mengandalkan pengaturan otomatis... |
| `ads.uncontrolledAuto` | Terdapat iklan dengan pengaturan otomatis yang tidak terkontrol biayanya... |
| `ads.uncontrolledManual` | Terdapat iklan dengan pengaturan manual yang tidak terkontrol biayanya... |
| `ads.uncontrolledKeyword` | Terdapat kata kunci dengan pengaturan manual yang tidak terkontrol biayanya... |

### 6. Email Assembly (`computations.py` — `_assemble_email_body()`)

| Key | Indonesian |
|-----|-----------|
| `email.subject` | AHA Store Internal Check Up (Store ICU) - {{store}} {{period}} |
| `email.sectionOperational` | Performa Operasional Toko: |
| `email.sectionSales` | Performa Penjualan Toko: |
| `email.sectionVisitors` | Tinjauan Pengunjung: |
| `email.sectionPromo` | Tingkat Penggunaan Alat Promosi: |
| `email.sectionProducts` | Jumlah Produk & Status Toko: |
| `email.sectionAds` | Performa Iklan: |
| `email.sectionCampaign` | Partisipasi Campaign: |
| `email.sectionCompetition` | Kompetisi TOP Produk: |
| `email.sectionConclusion` | Kesimpulan: |
| `email.sectionMarketing` | Estimasi persentase biaya marketing {{brand}} sekarang: |

---

## Not In Scope

- Frontend UI labels (already translated via i18n)
- Product names, brand names, store names (user data)
- Tab headers (already working)
- Numbers and percentages (universal)

---

## Backend Changes Summary

| File | Change |
|------|--------|
| `calculators/scoring/models.py` | Add `TranslatableText` dataclass; add `_i18n` fields to `RowScore`, `CategoryScore`, `ScoringResult` |
| `calculators/scoring/messages.py` | Return `TranslatableText` alongside existing text for all message generators |
| `calculators/scoring/categories.py` | Add `_i18n` fields for metric names, benchmarks, category names |
| `calculators/scoring/computations.py` | Add `_i18n` fields for G66, G68, G72, G73, G75, email body |
| `calculators/scoring/_calculator.py` | Pass through `_i18n` fields in final `ScoringResult` |
| `calculators/ads_keyword.py` | Return structured data alongside `output_text` |
| `calculators/discount.py` | Return structured data alongside `output_text` |
| `modules/evaluations/schemas.py` | Update response schemas to include `_i18n` fields |

## Frontend Changes Summary

| File | Change |
|------|--------|
| `locales/en.json` | Add all `scoring.*`, `category.*`, `verdict.*`, `conclusion.*`, `ads.*`, `email.*` keys |
| `locales/th.json` | Add all translation keys with Thai text |
| `locales/id.json` | Add all translation keys with Indonesian text |
| `components/dashboard/CategoryMetricCard.tsx` | Use `renderTranslatable()` helper |
| New: `utils/renderTranslatable.ts` | Helper: if `_i18n` exists → `t(key, vars)`, else → raw fallback text |
| All components displaying backend text | Switch to `renderTranslatable()` |

---

## Key Files

- Backend models: `backend/app/calculators/scoring/models.py`
- Scoring messages: `backend/app/calculators/scoring/messages.py`
- Computations: `backend/app/calculators/scoring/computations.py`
- Categories: `backend/app/calculators/scoring/categories.py`
- Ads calculator: `backend/app/calculators/ads_keyword.py`
- Frontend i18n config: `frontend/src/i18n.ts`
- Translation files: `frontend/src/locales/{en,id,th}.json`
- Metric card component: `frontend/src/components/dashboard/CategoryMetricCard.tsx`
