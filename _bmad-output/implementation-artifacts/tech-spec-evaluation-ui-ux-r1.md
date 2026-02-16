---
title: 'Evaluation UI/UX Revision R1'
slug: 'evaluation-ui-ux-r1'
created: '2026-02-16'
status: 'implementation-complete'
stepsCompleted: [1, 2, 3, 4]
tech_stack: ['React 19', 'TypeScript', 'TailwindCSS', 'Radix UI', 'React Query', 'Python/FastAPI', 'PostgreSQL', 'Vitest', 'Pytest']
files_to_modify:
  - 'frontend/src/components/evaluation/forms/formConfig.ts'
  - 'frontend/src/components/evaluation/forms/OperationalForm.tsx'
  - 'frontend/src/components/evaluation/forms/BusinessForm.tsx'
  - 'frontend/src/components/evaluation/forms/VisitorsForm.tsx'
  - 'frontend/src/components/evaluation/forms/PromoToolsForm.tsx'
  - 'frontend/src/components/evaluation/forms/ProductsStatusForm.tsx'
  - 'frontend/src/components/evaluation/forms/AdsForm.tsx'
  - 'frontend/src/components/evaluation/forms/CampaignForm.tsx'
  - 'frontend/src/components/evaluation/forms/CompetitionForm.tsx'
  - 'frontend/src/components/evaluation/EvaluationSections.tsx'
  - 'frontend/src/components/evaluation/SectionNav.tsx'
  - 'frontend/src/pages/EvaluationPage.tsx'
  - 'backend/app/calculators/scoring.py'
  - 'frontend/src/components/evaluation/forms/formConfig.test.ts'
  - 'backend/tests/test_scoring.py'  # new file
code_patterns:
  - 'Form components: props = { data, onChange, onBlur }; onChange(category, key, value)'
  - 'Field components: NumberField, CurrencyField, SelectField — props = { name, label, unit, benchmark, value, onChange, onBlur }'
  - 'Section headers: hardcoded strings in each form component'
  - 'Labels: centralized in formConfig.ts field arrays (OPERATIONAL_FIELDS, BUSINESS_FIELDS, etc.)'
  - 'Competition dot notation: onChange("competition", "product1.keyword", value) — handled by useAutoSaveForm split logic'
  - 'No external links exist in any form currently — new pattern needed'
  - 'ManualData 1:1 mapping: frontend formConfig.ts ↔ backend JSONB structure'
test_patterns:
  - 'Frontend: Vitest 4 + Testing Library, globals enabled (no imports), vi.mock() for hooks'
  - 'Frontend: QueryClientProvider + MemoryRouter wrapper for page tests'
  - 'Frontend: Test files co-located as *.test.tsx'
  - 'Backend: Pytest with asyncio_mode="auto", pure function testing for calculators'
---

# Tech-Spec: Evaluation UI/UX Revision R1

**Created:** 2026-02-16

## Overview

### Problem Statement

The evaluation form labels, computed fields, and reference links don't match the Shopee Seller Center structure, making it harder for BD team to cross-reference data when performing brand evaluations.

### Solution

Rename labels to match Shopee Seller Center terminology, add computed auto-calculated fields (averages, percentages, ROI, competitiveness), add clickable Shopee reference links per section, add a month selector dropdown for dynamic sales period labels, restructure competition fields to include more product details with auto-computed competitiveness results, and remove the unused Content section from the UI.

### Scope

**In Scope:**

- **Step 1 (Brand Info & Operational):** Rename section header "Operational" → "Kesehatan Operasional Toko", rename "Category Type" → "Kategori Toko", rename 4 field labels (Tingkat Pesanan Tidak Terselesaikan, Tingkat Keterlambatan Pengiriman, Persentase Chat Dibalas, Keseluruhan Penilaian), add clickable reference link to Shopee account health page
- **Step 2 (Business, Content & Visitors):** Rename "Business" → "Bisnis Analisis", rename "Visitors" → "Tinjauan Pengunjung", add month selector dropdown for dynamic sales labels (e.g., "Penjualan Bulan Jan 2026"), add "Rata-rata Penjualan 6 Bulan Terakhir" computed field, add "% Pengunjung Lama" computed field (Pengunjung Lama / Total Pengunjung), add store link (from brand raw_data "Link Shopee") to Total Pengikut, add reference links, remove Content form from UI
- **Step 3 (Promo Tools & Products/Status):** Rename all 11 promo tool labels with "Penjualan dari" prefix, add per-tool reference links (Brand Membership, Gratis Ongkir XTRA, Chat Broadcast, Program Afiliasi), add section-level reference link, add "% Penggunaan alat promosi" computed field (count of tools with value > 0 / total tools), add "% Efektifitas alat promosi" computed field (count of tools exceeding benchmark threshold / total tools), add store link to Products/Status section
- **Step 5 (Ads, Campaign, Competition & Review):** Rename "Ads" → "Data Iklan", "Campaign" → "Partisipasi Campaign", "Competition" → "Kompetisi TOP Produk", add reference links, add ROI computed field (Penjualan Iklan / Biaya Iklan), add "% GMV Iklan / GMV Toko" computed field, add "% Biaya Iklan / GMV Toko" computed field, add "% Partisipasi Campaign" computed field, restructure competition to 5 fields per product (Nama Produk, Harga Jual, Kata kunci pencarian, LINK, Harga rata-rata pasaran) + computed competitiveness result

**Out of Scope:**

- Step 4 (File Upload) — no changes
- Step 6 (Final Score) — no changes
- Backend scoring engine changes beyond dynamic month labels in `_score_business()` (content stays in scoring with zeros, competition scoring untouched)
- Backend API schema changes (no changes to `ScoringRequest`, `service.py`, or `router.py` — scoring reads `salesStartMonth` directly from `manual_data`)

## Context for Development

### Codebase Patterns

- **Form component pattern:** Each form receives `{ data, onChange, onBlur }` props. `onChange(category, key, value)` updates `localOverrides` in `useAutoSaveForm`, `onBlur()` triggers debounced save (500ms).
- **Field components:** `NumberField`, `CurrencyField`, `SelectField` — each takes `{ name, label, unit, benchmark, value, onChange, onBlur }`.
- **Label source:** All field labels centralized in `formConfig.ts` arrays (`OPERATIONAL_FIELDS`, `BUSINESS_FIELDS`, etc.). Section headers are hardcoded strings in each form component.
- **Competition dot notation:** `onChange('competition', 'product1.keyword', value)` — `useAutoSaveForm` splits on `.` to handle nested objects.
- **ManualData 1:1 mapping:** Frontend `formConfig.ts` TypeScript interfaces must stay in sync with the backend JSONB `manual_data` structure. Adding/changing fields requires updates on both sides.
- **No external links in forms currently** — adding clickable reference links is a new UI pattern across all forms.
- **Brand raw_data:** `useBrandDetail(brandId)` returns `brand.raw_data` (JSONB from Google Sheets sync). "Link Shopee" is a key in this dict.
- **Category display names:** `MANUAL_DATA_FIELDS` array in `formConfig.ts` maps category keys to display names (used in progress tracking).
- **IntersectionObserver:** `EvaluationSections.tsx` uses `IntersectionObserver` to track active section for sidebar highlighting.

### Files to Reference

| File | Purpose |
| ---- | ------- |
| `frontend/src/components/evaluation/forms/formConfig.ts` | Central field definitions — all labels, types, benchmarks, interfaces, defaults |
| `frontend/src/components/evaluation/forms/OperationalForm.tsx` | Step 1 — header: "Operational", 5 NumberFields |
| `frontend/src/components/evaluation/forms/BusinessForm.tsx` | Step 2 — header: "Business", 6 CurrencyFields + 1 NumberField, props: `{ data, onChange, onBlur }`. **Note:** `BusinessForm.test.tsx` passes a `categoryType` prop for benchmark switching (Fashion vs Non-Fashion) but the component interface doesn't declare it — pre-existing bug to fix in Task 6. |
| `frontend/src/components/evaluation/forms/ContentForm.tsx` | Step 2 — header: "Content", 2 NumberFields (to be removed from UI) |
| `frontend/src/components/evaluation/forms/VisitorsForm.tsx` | Step 2 — header: "Visitors", 3 NumberFields |
| `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` | Step 3 — header: "Promo Tools", 11 CurrencyFields |
| `frontend/src/components/evaluation/forms/ProductsStatusForm.tsx` | Step 3 — header: "Products / Status", 1 NumberField + 1 SelectField |
| `frontend/src/components/evaluation/forms/AdsForm.tsx` | Step 5 — header: "Ads", 2 CurrencyFields |
| `frontend/src/components/evaluation/forms/CampaignForm.tsx` | Step 5 — header: "Campaign", 2 NumberFields |
| `frontend/src/components/evaluation/forms/CompetitionForm.tsx` | Step 5 — header: "Competition", 3 product groups × 2 fields (keyword text + marketPrice currency) |
| `frontend/src/components/evaluation/EvaluationSections.tsx` | Main sections container — renders all forms, passes props, IntersectionObserver |
| `frontend/src/components/evaluation/SectionNav.tsx` | Left sidebar — section labels with progress counts |
| `frontend/src/pages/EvaluationPage.tsx` | Top-level page — hooks orchestration, brand data, auto-save, scoring |
| `frontend/src/hooks/useAutoSaveForm.ts` | Debounced save, localOverrides merge, competition dot-notation handling |
| `frontend/src/hooks/useBrandDetail.ts` | BrandDetail interface — `raw_data: Record<string, unknown>` |
| `frontend/src/components/evaluation/forms/NumberField.tsx` | Numeric input with unit, benchmark display |
| `frontend/src/components/evaluation/forms/CurrencyField.tsx` | IDR currency input with formatting |
| `docs/project-context.md` | Project conventions and rules |

### Technical Decisions

- **Month selector:** Simple select dropdown persisted as `manual_data.business.salesStartMonth` (format: `"2026-01"`). Labels for salesMonth0-5 and conversionRate dynamically generated from this value. **Important:** `salesMonth0` means "the month the user selected as starting month", not literally "current month." This semantic applies everywhere `salesMonth0` is referenced (scoring, promo %, ads % calculations).
- **Computed fields — visual distinction:** Computed/read-only fields (ROI, % Pengunjung Lama, % Penggunaan, % Efektifitas, % Partisipasi, % GMV, competition results, Rata-rata Penjualan) must be visually distinct from editable inputs. Render as plain text with a muted background (e.g., `bg-muted` / `bg-secondary` Tailwind class) instead of input boxes. The user should never wonder "can I type here?"
- **Content removal — 4 touchpoints:** (1) Remove `ContentForm` render from `EvaluationSections.tsx`, (2) Update `SectionNav.tsx` label to remove "Content" from Section 2, (3) Remove `content` entry from `MANUAL_DATA_FIELDS` in `formConfig.ts` so progress tracking excludes it, (4) Update `EvaluationForms.test.tsx` to remove content label assertions. **Keep `content` in `ManualData` interface, `EMPTY_MANUAL_DATA`, `buildManualData`, and `mergeWithOverrides`** for backward compatibility with existing saved data and the backend scoring engine (processes zeros). Only remove from UI render, navigation labels, and progress tracking.
- **Store link:** Extract from `brand.raw_data["Link Shopee"]` in `EvaluationPage.tsx`, pass down through `EvaluationSections` → relevant forms as a `storeLink` prop. Validate that the value starts with `https://` before using it as an `href` — if it doesn't, treat it as `null` (don't render the link icon). This prevents rendering broken or potentially unsafe URLs from raw external data.
- **Reference links — two placement levels:** (1) **Section-level links** go next to the section header as a small external-link icon (e.g., "Kesehatan Operasional Toko 🔗"). (2) **Field-level links** go next to the individual field label (e.g., "Penjualan dari Brand Membership 🔗"). Both use the same icon pattern (`ExternalLink` from lucide-react, `target="_blank" rel="noopener noreferrer"`).
- **Competition restructure:** Expand `CompetitionData` interface from `{ keyword, marketPrice }` to `{ productName, sellingPrice, keyword, link, marketPrice }` per product. Each product rendered as a card/group with the computed competitiveness result displayed as read-only text below the fields. Computed result: if sellingPrice > marketPrice × 1.1 → "❌tidak kompetitif", else "✅kompetitif". **Note:** The frontend `sellingPrice` (manual input) is for the competitiveness display only. The backend `_score_competition()` sources its `selling_price` from Calculator 2 output (`rata2_harga_jual`), NOT from manual input. This is intentional — competition scoring contributes 0 points and uses calculator data for the score breakdown text. The two data sources serve different purposes and should not be merged.
- **Promo thresholds — numeric property:** Add a `threshold` numeric property to each promo tool field config alongside the display `benchmark` string. Example: `{ key: 'promoToko', label: '...', benchmark: '>8% dari penjualan', threshold: 0.08 }`. The `% Efektifitas` computation uses `threshold` (not parsed from `benchmark` string). This separates display concerns from computation.
- **Cross-category data dependency:** `PromoToolsForm` and `AdsForm` need `salesMonth0` to compute percentage-based fields (% Penggunaan, % Efektifitas, % GMV Iklan, % Biaya Iklan). Since these forms only receive their own category `data`, the computed values should be calculated in `EvaluationSections.tsx` (which has access to all `manualData`) and passed down as additional props to each form.
- **Backend impact — backward compatibility:** Competition field expansion adds new keys (`productName`, `sellingPrice`, `link`) to existing JSONB structure. The frontend's `buildManualData` deep-merges with `EMPTY_MANUAL_DATA` — new defaults won't clobber existing saved data since the merge is additive. Add a test case to verify existing competition data (`{ keyword, marketPrice }`) still loads correctly after the schema expansion. No backend migration needed.

## Implementation Plan

### Tasks

#### Task 1: Update formConfig.ts — types, labels, thresholds, defaults

- File: `frontend/src/components/evaluation/forms/formConfig.ts`
- Action:
  1. **Update `OperationalData` labels** in `OPERATIONAL_FIELDS`:
     - `'Pesanan Tidak Terselesaikan'` → `'Tingkat Pesanan Tidak Terselesaikan'`
     - `'Keterlambatan'` → `'Tingkat Keterlambatan Pengiriman'`
     - `'Chat Dibalas'` → `'Persentase Chat Dibalas'`
     - `'Penilaian'` → `'Keseluruhan Penilaian'`
  2. **Update `BusinessData` interface** — add `salesStartMonth: string | null` field. **Important:** `salesStartMonth` is a UI control field, NOT a data input — it must be excluded from `computeSectionProgress` field counting. In `computeSectionProgress`, destructure `salesStartMonth` out before passing business data to `countFilledInFlat`: `const { salesStartMonth, ...bizData } = data.business; const biz = countFilledInFlat(bizData);`
  3. **Update `BUSINESS_FIELDS`** labels:
     - `'Penjualan Bulan Ini'` → `'Penjualan Bulan Ini'` (label will be dynamically overridden in BusinessForm, keep as fallback)
     - `'Tingkat Konversi'` → `'Tingkat Konversi'` (same — dynamically overridden)
  4. **Update `EMPTY_MANUAL_DATA.business`** — add `salesStartMonth: null`
  5. **Update `PROMO_TOOLS_FIELDS`** labels — add `'Penjualan dari '` prefix to all 11 labels:
     - `'Promo Toko'` → `'Penjualan dari Promo Toko'`
     - `'Paket Diskon'` → `'Penjualan dari Paket Diskon'`
     - `'Kombo Hemat'` → `'Penjualan dari Kombo Hemat'`
     - `'Flash Sale Toko Saya'` → `'Penjualan dari Flash Sale Toko Saya'`
     - `'Voucher'` → `'Penjualan dari Voucher'`
     - `'Shopee Live'` → `'Penjualan dari Shopee Live'`
     - `'Game Toko'` → `'Penjualan dari Game Toko'`
     - `'Brand Membership'` → `'Penjualan dari Brand Membership'`
     - `'Gratis Ongkir XTRA'` → `'Penjualan dari Gratis Ongkir XTRA'`
     - `'Chat Broadcast'` → `'Penjualan dari Chat Broadcast'`
     - `'Program Afiliasi'` → `'Penjualan dari Program Afiliasi'`
  6. **Add `threshold` numeric property** to each promo tool field config:
     - `promoToko: threshold: 0.08` (from ">8% dari penjualan")
     - `paketDiskon: threshold: 0.16`
     - `komboHemat: threshold: 0.01`
     - `flashSale: threshold: 0.01`
     - `voucher: threshold: 0.84`
     - `shopeeLive: threshold: 0.15`
     - `gameToko: threshold: 0.01`
     - `brandMembership: threshold: 0.01`
     - `gratisOngkir: threshold: 0` (benchmark is ">0", threshold is absolute not percentage)
     - `chatBroadcast: threshold: 0.01`
     - `programAfiliasi: threshold: 0.18`
  7. **Add `link` property** to relevant promo tool fields:
     - `brandMembership: link: 'https://seller.shopee.co.id/datacenter/marketing/membership'`
     - `gratisOngkir: link: 'https://seller.shopee.co.id/portal/marketing/cmt/campaign?tab=2&sort=9'`
     - `chatBroadcast: link: 'https://seller.shopee.co.id/datacenter/services/crm'`
     - `programAfiliasi: link: 'https://seller.shopee.co.id/portal/web-seller-affiliate/dashboard'`
  8. **Update `FieldDefinition` interface** (note: the actual interface name in the codebase is `FieldDefinition`, not `FieldConfig`) — add optional `threshold?: number` and `link?: string` properties
  9. **Update `CompetitionData` interface** — change per-product type from `{ keyword: string | null; marketPrice: number | null }` to `{ productName: string | null; sellingPrice: number | null; keyword: string | null; link: string | null; marketPrice: number | null }`
  10. **Update `COMPETITION_FIELDS`** — replace existing 6 entries with 15 (5 fields × 3 products):
      - Per product: `productN.productName` ("Produk Kompetitor N — Nama Produk"), `productN.sellingPrice` ("Produk Kompetitor N — Harga Jual", currency), `productN.keyword` ("Produk Kompetitor N — Kata kunci pencarian", text), `productN.link` ("Produk Kompetitor N — LINK", text), `productN.marketPrice` ("Produk Kompetitor N — Harga rata-rata pasaran", currency)
  11. **Update `EMPTY_MANUAL_DATA.competition`** — add `productName: null, sellingPrice: null, link: null` to each product default
  12. **Update `MANUAL_DATA_FIELDS`** display names:
      - `'Operasional'` → `'Kesehatan Operasional Toko'`
      - `'Bisnis'` → `'Bisnis Analisis'`
      - Remove `content` entry entirely
      - `'Pengunjung'` → `'Tinjauan Pengunjung'`
      - `'Alat Promo'` → `'Alat Promosi'`
      - `'Iklan'` → `'Data Iklan'`
      - `'Kampanye'` → `'Partisipasi Campaign'`
      - `'Kompetisi'` → `'Kompetisi TOP Produk'`
  13. **Add reference link constants** (exported):
      ```typescript
      export const SECTION_LINKS = {
        operational: 'https://seller.shopee.co.id/portal/accounthealth/home',
        business: 'https://seller.shopee.co.id/datacenter/dashboard',
        visitors: 'https://seller.shopee.co.id/datacenter/traffic/overview',
        promoTools: 'https://seller.shopee.co.id/datacenter/marketing/tools/discount',
        ads: 'https://seller.shopee.co.id/portal/marketing/pas/assembly?&type=all&group=last-thirty-days',
        campaign: 'https://seller.shopee.co.id/portal/marketing/cmt-product/campaign?tab=AllCampaign',
      } as const;
      ```
  14. **Add month generation helper** (exported):
      ```typescript
      const INDO_MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
      const GENERIC_LABELS = ["Bulan Ini", "Bulan -1", "Bulan -2", "Bulan -3", "Bulan -4", "Bulan -5"];

      export function generateMonthLabels(startMonth: string | null): string[] {
        // 1. If null, return GENERIC_LABELS
        // 2. Parse "YYYY-MM" → year (int), month (int 1-12)
        //    - Validate with regex /^\d{4}-(0[1-9]|1[0-2])$/
        //    - If invalid format, return GENERIC_LABELS
        // 3. For i = 0..5: subtract i months from (year, month)
        //    - monthIndex = ((month - 1 - i) % 12 + 12) % 12
        //    - yearOffset = Math.floor((month - 1 - i) / 12) — handle negative correctly
        //    - label = `${INDO_MONTHS[monthIndex]} ${year + yearOffset}`
        // 4. Return array of 6 labels in descending order
        // Example: "2026-01" → ["Jan 2026", "Des 2025", "Nov 2025", "Okt 2025", "Sep 2025", "Agu 2025"]
      }
      ```
- Notes: This is the foundation task. All other tasks depend on these type/label changes compiling correctly. Update the `FieldDefinition` type first, then update each field array. Run `tsc --noEmit` after to verify no type errors. The `generateMonthLabels` helper must validate input — if the string doesn't match `YYYY-MM` format or is otherwise invalid, return generic fallback labels (`["Bulan Ini", "Bulan -1", ...]`) instead of crashing.

#### Task 2: Update EvaluationPage.tsx — extract store link, pass down

- File: `frontend/src/pages/EvaluationPage.tsx`
- Action:
  1. Extract `storeLink` from `brand.raw_data["Link Shopee"]` as `string | null`. Validate that the value starts with `https://` — if not, set `storeLink` to `null`.
  2. Pass `storeLink` as a new prop to `EvaluationSections`
- Notes: Simple prop threading. Ensure `storeLink` is `null` when brand data is loading, key is missing, or URL doesn't start with `https://`.

#### Task 3: Update EvaluationSections.tsx — wire props, remove content, compute cross-category values

- File: `frontend/src/components/evaluation/EvaluationSections.tsx`
- Action:
  1. **Add `storeLink: string | null` to props interface**
  2. **Remove `ContentForm` import and render** from Section 2
  3. **Compute cross-category values** before rendering:
     ```typescript
     const salesMonth0 = manualData.business?.salesMonth0 ?? 0;
     ```
  4. **Pass `storeLink` to** `VisitorsForm` and `ProductsStatusForm`
  5. **Pass `salesMonth0` to** `PromoToolsForm` and `AdsForm`
  6. **Pass `categoryType` to** `BusinessForm` (needed for conversion rate benchmark switching — see Task 6 action 2). Note: `salesStartMonth` does NOT need a separate prop — BusinessForm already receives it via its `data` prop (`manualData.business`).
  7. **Rename `"Category Type"` label** (hardcoded at line ~122) to `"Kategori Toko"` in the RadioGroup section
- Notes: This is the wiring hub. All computed values flow from here to child forms.

#### Task 4: Update SectionNav.tsx — rename section labels

- File: `frontend/src/components/evaluation/SectionNav.tsx`
- Action:
  1. Update section label strings:
     - `'Brand Info & Operational'` → `'Brand Info & Kesehatan Operasional'`
     - `'Business, Content & Visitors'` → `'Bisnis Analisis & Tinjauan Pengunjung'`
     - `'Ads, Campaign, Competition, Stock, Discount & Review'` → `'Data Iklan, Campaign, Kompetisi & Review'`
  2. **Update `computeSectionProgress` in `formConfig.ts`** (not `SectionNav.tsx` — the progress function lives in `formConfig.ts` lines ~231-260):
     - **Remove content from Section 2 progress:** Delete the `content = countFilledInFlat(data.content)` line and remove `content.filled` / `content.total` from the s2 calculation.
     - **Fix competition nested field counting:** The competition section uses a custom reduce (NOT `countFilledInFlat`) that currently counts only `keyword` and `marketPrice` per product (= 6 total, hardcoded). Expand the reduce to count all 5 nested fields per product (`productName`, `sellingPrice`, `keyword`, `link`, `marketPrice`) and change the hardcoded total from `6` to `15`.
- Notes: Progress counts must match actual rendered fields after content removal and competition expansion. Section 2 loses 2 fields (content removed). Section 5 competition changes from 6 to 15 fields.

#### Task 5: Update OperationalForm.tsx — header rename, add reference link

- File: `frontend/src/components/evaluation/forms/OperationalForm.tsx`
- Action:
  1. Change section header from `"Operational"` to `"Kesehatan Operasional Toko"`
  2. Add clickable external link icon next to header pointing to `SECTION_LINKS.operational`
- Notes: Import `ExternalLink` from lucide-react. Pattern: `<a href={SECTION_LINKS.operational} target="_blank" rel="noopener noreferrer"><ExternalLink className="size-4 text-muted-foreground" /></a>`

#### Task 6: Update BusinessForm.tsx — header, month selector, dynamic labels, computed average, link

- File: `frontend/src/components/evaluation/forms/BusinessForm.tsx`
- Action:
  1. Change section header from `"Business"` to `"Bisnis Analisis"`
  2. **Fix pre-existing bug:** Add `categoryType: string | null` to BusinessForm's props interface. The existing test (`BusinessForm.test.tsx`) already passes this prop for conversion rate benchmark switching (Fashion >2% vs Non-Fashion >3%), but the component never declared it. Add it now alongside the other new props.
  3. **Update `onChange` prop type** from `value: number | null` to `value: number | string | null` to accommodate the string-typed `salesStartMonth` value (e.g., `"2026-01"`). The parent `EvaluationSections.onFieldChange` already accepts `number | string | null`, so this aligns the child type with the parent.
  4. Add clickable reference link next to header → `SECTION_LINKS.business`
  5. **Add month selector dropdown** at the top of the form:
     - Render a `<select>` or Radix `Select` with month options (last 12 months from current date)
     - Default: current month (e.g., "2026-02")
     - On change: call `onChange('business', 'salesStartMonth', value)` then `onBlur()` to persist
  6. **Dynamically generate labels** for salesMonth0-5 using `generateMonthLabels(data.salesStartMonth)`:
     - Override each CurrencyField's `label` prop with `"Penjualan Bulan " + monthLabels[i]`
     - Override conversionRate label with `"Tingkat Konversi " + monthLabels[0]`
  7. **Add computed "Rata-rata Penjualan 6 Bulan Terakhir"** displayed as read-only text below the sales fields:
     - Calculation: `(salesMonth0 + salesMonth1 + ... + salesMonth5) / 6` — always divide by 6, treating null/empty values as 0. This matches the backend scoring engine which also divides by 6 with nulls coerced to 0. Show "—" when all 6 months are null/empty (i.e., user hasn't entered any data). If all months are explicitly 0, show "Rp 0" (that's valid data, not missing data).
     - Display: formatted as IDR currency with `bg-muted rounded-md p-2` styling
- Notes: Most complex form change. The month selector state persists via the standard auto-save mechanism. The `generateMonthLabels` helper from formConfig.ts handles Indonesian month name formatting.

#### Task 7: Update VisitorsForm.tsx — header, computed %, store link, reference link

- File: `frontend/src/components/evaluation/forms/VisitorsForm.tsx`
- Action:
  1. Change section header from `"Visitors"` to `"Tinjauan Pengunjung"`
  2. Add clickable reference link next to header → `SECTION_LINKS.visitors`
  3. **Add `storeLink` prop** to component interface
  4. **Add store link** next to "Total Pengikut" field — render as clickable external link icon using `storeLink` URL
  5. **Add computed "% Pengunjung Lama"** displayed as read-only text:
     - Calculation: `(returningVisitors / totalVisitors) * 100` (show "—" if totalVisitors is 0 or null)
     - Display: `bg-muted rounded-md p-2` with `%` unit
- Notes: Store link may be null — only render the link icon when `storeLink` is truthy.

#### Task 8: Update PromoToolsForm.tsx — header, labels (from config), field-level links, computed fields, section link

- File: `frontend/src/components/evaluation/forms/PromoToolsForm.tsx`
- Action:
  1. Change section header from `"Promo Tools"` to `"Alat Promosi"`
  2. Add clickable reference link next to header → `SECTION_LINKS.promoTools`
  3. **Add `salesMonth0` prop** to component interface
  4. **Render field-level links**: For each field that has a `link` property in its config, render a small `ExternalLink` icon next to the field label. Fields with links: `brandMembership`, `gratisOngkir`, `chatBroadcast`, `programAfiliasi`
  5. **Add computed "% Penggunaan alat promosi"** displayed as read-only text:
     - Calculation: count fields where value > 0, divide by total number of promo tool fields (11)
     - Display: `bg-muted rounded-md p-2` with `%` unit, formatted as percentage
  6. **Add computed "% Efektifitas alat promosi"** displayed as read-only text:
     - Calculation: for each field, check if `value > salesMonth0 * field.threshold` (for percentage-based thresholds) or `value > field.threshold` (for `gratisOngkir` which is absolute). Count passing fields, divide by 11. **If salesMonth0 is 0 or null, display "—"** instead of computing (percentage-based thresholds are meaningless without store revenue).
     - Display: `bg-muted rounded-md p-2` with `%` unit
- Notes: The labels are already updated in formConfig (Task 1). The form iterates over `PROMO_TOOLS_FIELDS` so label changes propagate automatically. The `threshold` check for `gratisOngkir` is special — its benchmark `">0"` means absolute value > 0, not percentage of sales.

#### Task 9: Update ProductsStatusForm.tsx — add store link

- File: `frontend/src/components/evaluation/forms/ProductsStatusForm.tsx`
- Action:
  1. **Add `storeLink` prop** to component interface
  2. Add store link next to "Products / Status" header — render as clickable external link icon using `storeLink` URL
- Notes: Header text can stay as "Products / Status" or be kept as-is. Store link may be null.

#### Task 10: Update AdsForm.tsx — header, computed fields, reference link

- File: `frontend/src/components/evaluation/forms/AdsForm.tsx`
- Action:
  1. Change section header from `"Ads"` to `"Data Iklan"`
  2. Add clickable reference link next to header → `SECTION_LINKS.ads`
  3. **Add `salesMonth0` prop** to component interface
  4. **Add computed "ROI"** displayed as read-only text:
     - Calculation: `adSales / adCost` (show "—" if adCost is 0 or null)
     - Display: `bg-muted rounded-md p-2`, formatted as decimal (e.g., `"4.00"`)
  5. **Add computed "% GMV Iklan / GMV Toko"** displayed as read-only text:
     - Calculation: `(adSales / salesMonth0) * 100` (show "—" if salesMonth0 is 0 or null)
     - Display: `bg-muted rounded-md p-2` with `%` unit
  6. **Add computed "% Biaya Iklan / GMV Toko"** displayed as read-only text:
     - Calculation: `(adCost / salesMonth0) * 100` (show "—" if salesMonth0 is 0 or null)
     - Display: `bg-muted rounded-md p-2` with `%` unit
- Notes: All 3 computed fields are derived from existing input values + `salesMonth0` prop.

#### Task 11: Update CampaignForm.tsx — header, computed field, reference link

- File: `frontend/src/components/evaluation/forms/CampaignForm.tsx`
- Action:
  1. Change section header from `"Campaign"` to `"Partisipasi Campaign"`
  2. Add clickable reference link next to header → `SECTION_LINKS.campaign`
  3. **Add computed "% Partisipasi Campaign"** displayed as read-only text:
     - Calculation: `(nominatedSessions / availableSessions) * 100` (show "—" if availableSessions is 0 or null)
     - Display: `bg-muted rounded-md p-2` with `%` unit
- Notes: No new props needed — all values come from existing `data` prop.

#### Task 12: Update CompetitionForm.tsx — header, expand fields, computed result

- File: `frontend/src/components/evaluation/forms/CompetitionForm.tsx`
- Action:
  1. Change section header from `"Competition"` to `"Kompetisi TOP Produk"`
  2. **Update PRODUCTS const** labels (no change needed — keep "Produk Kompetitor 1/2/3")
  3. **Expand each product group** from 2 fields to 5 fields, rendered in order:
     - `productName` — text input, label: "Nama Produk"
     - `sellingPrice` — CurrencyField, label: "Harga Jual"
     - `keyword` — text input, label: "Kata kunci pencarian"
     - `link` — text input, label: "LINK"
     - `marketPrice` — CurrencyField, label: "Harga rata-rata pasaran"
  4. **Add computed competitiveness result** below each product group as read-only text:
     - Condition: only show when both `sellingPrice` and `marketPrice` have values
     - If `sellingPrice > marketPrice * 1.1`:
       `"• {productName} (Rp. {sellingPrice}) = ❌tidak kompetitif (harga kisaran pasaran: Rp. {marketPrice})"`
     - Else:
       `"• {productName} (Rp. {sellingPrice}) = ✅kompetitif"`
     - Append on new line: `"↪{keyword}"`
     - Display: `bg-muted rounded-md p-2 text-sm` with conditional text color (red for ❌, green for ✅)
  5. **onChange calls** use existing dot-notation pattern: `onChange('competition', 'product1.productName', value)`, etc.
- Notes: The `useAutoSaveForm` dot-notation split logic already handles new nested keys generically — no changes needed there. Each product group can be a visual card with `border rounded-lg p-4` styling to reduce visual clutter (Sally's recommendation).

#### Task 13: Backend — dynamic month labels in scoring engine

- File: `backend/app/calculators/scoring.py`
- Action:
  1. **Add Python month label helper** in `scoring.py`:
     ```python
     INDO_MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

     def _generate_month_labels(start_month: str | None) -> list[str]:
         """Given '2026-01', returns ['Jan 2026', 'Des 2025', 'Nov 2025', ...] for 6 months.
         If None or invalid, returns ['Bulan Ini', 'Bulan -1', ..., 'Bulan -5']."""
     ```
  2. **Update `_score_business()`** — extract `sales_start_month` from `manual_data["business"]["salesStartMonth"]` (already available via function's existing `manual_data` parameter), generate dynamic labels:
     - Row 13 metric: `f"Penjualan Bulan {labels[0]}"` (was `"Penjualan"`)
     - Rows 14-18 metric: `f"Penjualan Bulan {labels[i]}"` (was `f"Penjualan Bulan -{i}"`)
- Notes: **No API schema changes needed.** The `sales_start_month` value lives in `manual_data["business"]["salesStartMonth"]`, which the scoring engine already receives as part of the evaluation data. Extract it directly — no changes to `ScoringRequest`, `service.py`, or `router.py`.

#### Task 14: Update test files

- Files:
  - `frontend/src/components/evaluation/forms/CompetitionForm.test.tsx`
  - `frontend/src/components/evaluation/EvaluationForms.test.tsx`
  - `frontend/src/pages/EvaluationPage.test.tsx`
- Action:
  1. **CompetitionForm.test.tsx:**
     - Update `emptyData` mock to include new fields: `{ productName: null, sellingPrice: null, keyword: null, link: null, marketPrice: null }` per product
     - Update field count assertions (from 6 to 15 inputs)
     - Update pre-filled data test to include new field values
     - Add test for computed competitiveness result rendering
     - Add test for backward compatibility: existing `{ keyword, marketPrice }` data loads correctly (verify `useAutoSaveForm`'s `buildManualData` shallow merge doesn't clobber existing keyword/marketPrice when new defaults include productName/sellingPrice/link)
  2. **EvaluationForms.test.tsx:**
     - Remove content label assertions (`"Perlu Ditingkatkan"`, `"Kualitas Baik"`)
     - Update label assertions to match renamed labels (e.g., `"Tingkat Pesanan Tidak Terselesaikan"`)
     - Update section header assertions to match new names
     - Update field count expectations after content removal
  3. **EvaluationPage.test.tsx:**
     - Update `SAMPLE_BRAND` mock to include `raw_data: { "Link Shopee": "https://shopee.co.id/store" }`
     - Add section nav label assertions for renamed labels (new assertions, not updating existing ones since there are currently no nav label tests)
     - Update save payload structure if competition data shape changed in manual_inputs
  4. **BusinessForm.test.tsx** (if exists):
     - **Fix pre-existing broken assertion:** Change `screen.getByLabelText(/Conversion Rate/)` to `screen.getByLabelText(/Tingkat Konversi/)` — the label was already Indonesian in formConfig but the test was never updated
     - Add test for month selector rendering and onChange callback
     - Add test for dynamic label generation
     - Add test for computed average display
     - Add test for all-null sales months → average shows "—"
     - Add test for invalid `salesStartMonth` → fallback labels used
     - Add test for `categoryType` prop acceptance (pre-existing test already covers this, just verify it still passes)
  5. **formConfig.test.ts** (new):
     - Add test for `generateMonthLabels("2026-01")` → correct Indonesian month names in descending order
     - Add test for `generateMonthLabels(null)` → generic fallback labels
     - Add test for `generateMonthLabels("invalid")` → generic fallback labels
  6. **PromoToolsForm.test.tsx** (if exists):
     - Add test for `salesMonth0=0` → % Efektifitas computes without division error
  7. **CompetitionForm.test.tsx** (additional):
     - Add test for null `productName` with valid prices → fallback "—" in result text
  8. **Backend scoring tests** (if exist, e.g., `test_scoring.py`):
     - Add test for `_generate_month_labels("2026-01")` → correct Indonesian labels
     - Add test for `_generate_month_labels(None)` → generic fallback
     - Add test for `_score_business()` with `salesStartMonth="2026-01"` → row metrics use dynamic labels
     - Add test for `_score_business()` with `salesStartMonth=None` → row metrics use generic labels

### Acceptance Criteria

- [x] AC 1: Given the evaluation form is loaded, when the user views Step 1, then the section header reads "Kesehatan Operasional Toko" with a clickable link to `seller.shopee.co.id/portal/accounthealth/home`, and field labels show "Tingkat Pesanan Tidak Terselesaikan", "Tingkat Keterlambatan Pengiriman", "Persentase Chat Dibalas", "Keseluruhan Penilaian"
- [x] AC 2: Given the evaluation form is loaded, when the user views Step 1, then the category type label reads "Kategori Toko"
- [x] AC 3: Given the evaluation form is loaded, when the user views Step 2 Business section, then the header reads "Bisnis Analisis" with a clickable reference link, and a month selector dropdown is present
- [x] AC 4: Given the month selector is set to "Jan 2026", when the user views the sales fields, then labels show "Penjualan Bulan Jan 2026", "Penjualan Bulan Des 2025", "Penjualan Bulan Nov 2025", etc. in descending order, and the conversion rate label shows "Tingkat Konversi Jan 2026"
- [x] AC 5: Given salesMonth0=50M, salesMonth1=48M, salesMonth2=45M, salesMonth3=40M, salesMonth4=42M, salesMonth5=44M, when the user views Step 2 Business section, then "Rata-rata Penjualan 6 Bulan Terakhir" displays "Rp 44.833.333" as read-only text with muted background
- [x] AC 6: Given the Content section previously visible in Step 2, when the user views Step 2, then no Content form fields are rendered (no "Perlu Ditingkatkan" or "Kualitas Baik")
- [x] AC 7: Given totalVisitors=10000 and returningVisitors=3000, when the user views Step 2 Visitors section, then "% Pengunjung Lama" displays "30%" as read-only text
- [x] AC 8: Given the brand has `raw_data["Link Shopee"] = "https://shopee.co.id/store"`, when the user views the "Total Pengikut" field, then a clickable store link icon is visible next to it
- [x] AC 9: Given the evaluation form is loaded, when the user views Step 3 Promo Tools section, then all 11 field labels start with "Penjualan dari" prefix (e.g., "Penjualan dari Promo Toko")
- [x] AC 10: Given Brand Membership, Gratis Ongkir XTRA, Chat Broadcast, and Program Afiliasi fields, when the user views them, then each has a clickable external link icon pointing to its respective Shopee URL
- [x] AC 11: Given 7 of 11 promo tools have values > 0, when the user views Step 3, then "% Penggunaan alat promosi" displays "63.6%" as read-only text
- [x] AC 12: Given salesMonth0=100M and promoToko=10M (threshold 8%, required > 8M, passes) and paketDiskon=5M (threshold 16%, required > 16M, fails), when the user views Step 3, then "% Efektifitas alat promosi" correctly reflects count of tools exceeding their threshold / 11
- [x] AC 13: Given adSales=20M and adCost=5M and salesMonth0=100M, when the user views Step 5 Ads, then ROI shows "4.00", "% GMV Iklan / GMV Toko" shows "20%", "% Biaya Iklan / GMV Toko" shows "5%"
- [x] AC 14: Given nominatedSessions=5 and availableSessions=8, when the user views Step 5 Campaign, then "% Partisipasi Campaign" displays "62.5%"
- [x] AC 15: Given a competitor product with productName="Sepatu A", sellingPrice=150000, keyword="sepatu murah", marketPrice=100000, when the user views Step 5 Competition, then the result shows "• Sepatu A (Rp. 150.000) = ❌tidak kompetitif (harga kisaran pasaran: Rp. 100.000)" with "↪sepatu murah" on the next line
- [x] AC 16: Given a competitor product with sellingPrice=90000, marketPrice=100000, when the user views the result, then it shows "✅kompetitif"
- [x] AC 17: Given an existing evaluation with old competition data `{ keyword: "shoes", marketPrice: 50000 }`, when loaded, then the form populates keyword and marketPrice correctly, and new fields (productName, sellingPrice, link) show as empty/null without data loss
- [x] AC 18: Given the month selector value is changed, when the user blurs, then the selected month persists via auto-save and reloads correctly on page refresh
- [x] AC 19: Given all computed fields (ROI, %, averages, competitiveness), when values update, then computed displays refresh in real-time without requiring manual save or page reload
- [x] AC 20: Given all reference links, when clicked, then they open in a new tab (`target="_blank"`) and have `rel="noopener noreferrer"` for security
- [x] AC 21: Given all 6 sales months are null/empty, when the user views Step 2 Business section, then "Rata-rata Penjualan 6 Bulan Terakhir" displays "—" (not "Rp 0" or NaN)
- [x] AC 22: Given salesMonth0=0, when "% Efektifitas alat promosi" is computed, then it displays "—" instead of computing (since percentage-based thresholds are meaningless without store revenue). "% Penggunaan alat promosi" still computes normally (it doesn't depend on salesMonth0). Similarly, "% GMV Iklan / GMV Toko" and "% Biaya Iklan / GMV Toko" in AdsForm display "—" when salesMonth0=0.
- [x] AC 23: Given a competitor product with `productName` is null but `sellingPrice=150000` and `marketPrice=100000` have values, when the result is computed, then it uses a fallback display (e.g., "• — (Rp. 150.000) = ❌tidak kompetitif") instead of showing "null"
- [x] AC 24: Given `salesStartMonth` is set to an invalid string (e.g., "abc" or ""), when labels are generated, then fallback generic labels are used ("Bulan Ini", "Bulan -1", etc.) without errors
- [x] AC 25: Given content section was removed from UI, when Section 2 progress is calculated, then it counts only business + visitors fields (excludes content and excludes `salesStartMonth` which is a UI control, not a data input), and Section 5 progress counts the expanded 15 competition fields correctly
- [x] AC 26: Given `salesStartMonth` is set to "2026-01" and scoring is generated, when the score breakdown is returned, then row 13 metric reads "Penjualan Bulan Jan 2026", row 14 reads "Penjualan Bulan Des 2025", etc., matching the frontend labels
- [x] AC 27: Given `salesStartMonth` is null and scoring is generated, then row metrics fall back to generic labels ("Bulan Ini", "Bulan -1", etc.)

## Additional Context

### Dependencies

- No new npm packages needed — `ExternalLink` icon from lucide-react (already installed), select dropdown uses native HTML `<select>` or existing Radix UI `Select` component
- No database migrations needed — `manual_data` is untyped JSONB, new fields accepted automatically
- No backend API schema changes needed — computed fields are frontend-only, competition field expansion is accepted by JSONB, and `salesStartMonth` is read directly from `manual_data` in the scoring engine
- Backend scoring change is limited to dynamic month labels in `_score_business()` within `scoring.py` — content scoring untouched, competition scoring reads `keyword` and `marketPrice` which remain in the same structure

### Testing Strategy

**Unit Tests (Vitest + Testing Library):**
- Each form component: verify renamed headers render correctly
- Each form component: verify reference links render with correct `href`
- BusinessForm: verify month selector renders, onChange fires with correct value, dynamic labels update
- BusinessForm: verify computed average calculation and display
- VisitorsForm: verify % Pengunjung Lama computation and edge case (0 visitors → "—")
- PromoToolsForm: verify field-level links render for the 4 fields that have them
- PromoToolsForm: verify % Penggunaan and % Efektifitas computations
- AdsForm: verify ROI, % GMV, % Biaya computations and edge cases (0 division → "—")
- CampaignForm: verify % Partisipasi computation
- CompetitionForm: verify 5 fields per product render, computed result logic, edge cases
- CompetitionForm: backward compatibility — old `{ keyword, marketPrice }` data loads without error
- EvaluationForms integration: verify content section no longer renders
- formConfig: verify `generateMonthLabels()` produces correct Indonesian month names in correct order

**Manual Testing:**
- Load an existing evaluation with old competition data → verify no data loss
- Select a starting month → verify all 6 sales labels + conversion rate label update
- Fill in promo tool values → verify % Penggunaan and % Efektifitas update in real-time
- Fill in ads values → verify ROI and % GMV fields update
- Click all reference links → verify they open correct Shopee Seller Center pages in new tabs
- Verify computed fields are visually distinct (muted background, not editable)
- Verify section nav progress counts are correct after content removal

### Notes

- **Competition result formula:** `IF(sellingPrice > marketPrice × 1.1) → "• productName (Rp. sellingPrice) = ❌tidak kompetitif (harga kisaran pasaran: Rp. marketPrice)" ELSE "• productName (Rp. sellingPrice) = ✅kompetitif"` + newline + `"↪keyword"`
- **"% Penggunaan alat promosi"** = COUNTIF(promo values > 0) / COUNT(all promo tools) = count / 11
- **"% Efektifitas alat promosi"** = COUNTIF(promo values > salesMonth0 × threshold) / COUNT(all promo tools). Exception: `gratisOngkir` threshold is absolute (> 0), not percentage-based.
- **Sales month labels** auto-populate in descending order from user-selected starting month using Indonesian month names (Jan, Feb, Mar, Apr, Mei, Jun, Jul, Agu, Sep, Okt, Nov, Des)
- **"Rata-rata Penjualan 6 Bulan Terakhir"** = average of salesMonth0 through salesMonth5. Always divide by 6 (nulls coerced to 0) to match backend scoring engine behavior. Show "—" only when all 6 months are null/empty.
- **Section progress counts** in SectionNav will change: Section 2 loses 2 fields (content), Section 5 gains 9 fields (competition expansion from 6 to 15)
- **High-risk item:** Month selector persistence — ensure `salesStartMonth` survives the auto-save round-trip (save to JSONB → reload → display). The `buildManualData` merge in `useAutoSaveForm` must include `salesStartMonth` in the `BusinessData` type.
- **Scoring engine month labels:** Task 13 updates `scoring.py` to use dynamic month labels (e.g., "Penjualan Bulan Jan 2026") instead of static "Penjualan Bulan -1" labels. The `salesStartMonth` value is extracted from `manual_data["business"]["salesStartMonth"]` within the scoring function — no API changes needed. This ensures consistency between the frontend form labels and the generated score breakdown / email output.
