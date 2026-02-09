# Sprint Change Proposal — 2026-02-09

**Project:** Store ICU
**Author:** Mr. Door
**Date:** 2026-02-09
**Status:** Approved
**Change Scope:** Minor — Direct Adjustment (artifact updates, no code changes)

---

## 1. Issue Summary

### What Happened

The BD team's calculator specifications were documented in detail during the Epic 2 retrospective, captured in 4 specification files (`logic/` folder):

- `calculator-1-kata-kunci-iklan-shopee.md` — Ads Keyword Calculator (2 sheets, CSV inputs)
- `calculator-2-penjualan.md` — Sales/Top SKU Calculator (Order Export + Mass Update Excel)
- `calculator-3-discount-checkup.md` — Discount Check Calculator (Order Export Excel)
- `scoring-system-template-sicu.md` — 75-row Scoring System Template

### Core Problem

The current planning artifacts (PRD, Architecture, Epics) describe calculators and scoring in **generic, placeholder terms**. Each calculator was assumed to return a numeric JSON `{ score: 75.5, details: {...} }` from a single Excel file upload. The actual specifications reveal a fundamentally different system:

| Aspect | Planning Artifacts Assume | Actual Spec (`logic/`) |
|--------|--------------------------|----------------------|
| File inputs | 1 Excel file → all calculators | 4 files: 2 CSVs + 2 Excels, routed per calculator |
| Calculator outputs | Numeric score + JSON details | Text blocks, ranked tables, percentage summaries |
| Scoring system | Simple "combine results" formula | 75-row evaluation with ~40+ manual fields, complex derived formulas, Fashion/Non-Fashion thresholds, email/WA output |
| File types | `.xlsx` / `.xls` only | CSV (Calculator 1) + Excel (Calculators 2 & 3) |

### What's NOT Affected

- All Epic 1 work (auth, project structure) — safe
- All Epic 2 work (brand sync, SSE, scheduler) — safe
- VP Sheet and Meeting Sheet data model — unchanged
- Epic goals and overall MVP scope — unchanged

### What IS Affected

- PRD functional requirements FR6–FR17 (calculator and input descriptions)
- Architecture (upload flow, calculator interfaces, database schema, data flow)
- UX Design (guided steps, upload UI, results display, score panel)
- Epic 3 Stories 3.1–3.10 (acceptance criteria)
- Epic 4–5 stories (minor adjustments)

---

## 2. Impact Analysis

### Epic Impact

| Epic | Status | Impact Level | Details |
|------|--------|-------------|---------|
| Epic 1 | Done | None | Historical record unchanged |
| Epic 2 | Done | None | All work safe, Story 2.6 (accessibility) unaffected |
| Epic 3 | Backlog | **High** | Stories 3.4–3.6 need complete AC rewrites; 3.1–3.3, 3.7–3.10 need significant updates |
| Epic 4 | Backlog | Low | Evaluation detail view needs minor updates for actual data structure |
| Epic 5 | Backlog | Medium | Rule configuration needs to reflect actual scoring thresholds |

### Artifact Conflicts

| Artifact | Changes Required | Nature |
|----------|-----------------|--------|
| PRD | 10 FR updates | Text corrections to match actual calculator inputs/outputs |
| Architecture | 8 updates | Schema, upload flow, calculator interface, data flow |
| UX Design | 4 updates | Step organization, upload UI, results display, score panel |
| Epics/Stories | 10 stories | 3 complete rewrites (3.4–3.6), 7 significant updates |

### Technical Impact

- **Database:** `brand_uploads` table needs multi-file support (UNIQUE constraint change). `calculator_results` table needs schema update (remove numeric score column).
- **Backend code:** No existing code affected — Epic 3 hasn't started.
- **Frontend code:** No existing code affected.
- **Infrastructure:** No changes needed.

---

## 3. Recommended Approach

### Selected: Direct Adjustment

Update planning artifacts to match the authoritative calculator specifications from `logic/`. No rollbacks, no scope reduction, no new epics.

### Rationale

| Factor | Assessment |
|--------|-----------|
| Implementation effort | Low — artifact text updates only, zero code changes |
| Timeline impact | None — Epic 3 hasn't started. Correcting specs NOW prevents rework. |
| Technical risk | Low — `logic/` provides authoritative specs with sample data for validation |
| Team momentum | Preserved — no rollbacks, no scope cuts |
| Long-term sustainability | Significantly improved — stories will have precise, testable ACs |
| Business value | Unchanged — all MVP features still delivered |

### Alternatives Considered

| Option | Verdict | Why |
|--------|---------|-----|
| Rollback | Not viable | No Epic 3 code exists to roll back |
| MVP scope reduction | Unnecessary | All features still deliverable |
| New epic for calculators | Rejected | Calculator work fits within Epic 3's existing goal |

---

## 4. Detailed Change Proposals

### 4.1 PRD Updates (10 edits)

**Edit 1 — FR6:**
- OLD: "BD team member can upload Excel files for a specific brand's calculator processing"
- NEW: "BD team member can upload data files (CSV and Excel) for a specific brand's calculator processing — multiple files per evaluation, each routed to its target calculator"

**Edit 2 — FR7:**
- OLD: "System can parse uploaded Excel files using Polars"
- NEW: "System can parse uploaded data files (CSV and Excel) using Polars"

**Edit 3 — FR8:**
- OLD: "BD team member can enter manual data values for a specific brand"
- NEW: "BD team member can enter manual data values for a specific brand, organized by scoring system categories (~40+ fields across operational, business, content, visitors, promo, ads, campaign, competition, stock, and discount sections)"

**Edit 4 — FR9:**
- OLD: "System can validate uploaded file format before processing"
- NEW: "System can validate uploaded file format and per-calculator column schema before processing"

**Edit 5 — FR12:**
- OLD: "System can execute Ads Keyword Calculator on a brand's uploaded data"
- NEW: "System can execute Ads Keyword Calculator using CPC Ad Report CSV and Keyword Placement Report CSV, producing text-based ad analysis with overview, type breakdown, recommendations, top/bottom performers, and flags"

**Edit 6 — FR13:**
- OLD: "System can execute Discount Check Calculator on a brand's uploaded data"
- NEW: "System can execute Discount Check Calculator using Order Export data, producing discount percentage analysis, range, voucher/bundle percentages, and fake discount detection flag"

**Edit 7 — FR14:**
- OLD: "System can execute Top SKU Calculator on a brand's uploaded data"
- NEW: "System can execute Top SKU Calculator using Order Export and Mass Update data, producing top 20% selling SKU tables (with revenue and stock) and average stock metric"

**Edit 8 — FR15:**
- OLD: "System can execute all calculators automatically after file upload for a brand"
- NEW: "System can execute applicable calculators when their required input files become available for a brand"

**Edit 9 — FR16:**
- OLD: "BD team member can view individual calculator results for a brand"
- NEW: "BD team member can view individual calculator results for a brand — text summaries with flags (Ads Keyword), ranked product tables (Top SKU), and discount analysis text (Discount Check)"

**Edit 10 — FR17:**
- OLD: "System can combine calculator results with manual input data for a brand"
- NEW: "System can combine calculator results with manual input data for a brand using the 75-row scoring system template (Fashion/Non-Fashion variants) to produce final score, category breakdowns, and output messages"

### 4.2 Architecture Updates (8 edits)

**Edit 1 — `brand_uploads` table schema:**
- OLD: `UNIQUE(brand_id)` — one active upload per brand
- NEW: `UNIQUE(brand_id, file_type)` — one file per type per brand. Add columns: `file_type VARCHAR(50)` (values: `cpc_ad_report`, `keyword_report`, `order_export`, `mass_update`), `calculator_target VARCHAR(50)`

**Edit 2 — Supported Upload Types:**
- OLD: `.xlsx`, `.xls`, `.zip` only
- NEW: Add `.csv` to supported types. Document 4 file types: CPC Ad Report CSV, Keyword Placement Report CSV, Order Export Excel (.xlsx), Mass Update Excel (.xlsx)

**Edit 3 — Calculator base interface:**
- OLD: All calculators return `{ score: Decimal, details: JSONB }`
- NEW: Polymorphic results — `AdsKeywordResult` (text blocks), `TopSkuResult` (tables + avg stock integer), `DiscountCheckResult` (text values + flag), `ScoringResult` (numeric score + breakdown + output messages)

**Edit 4 — Calculator module descriptions:**
- `ads_keyword.py`: "Processes 2 CSVs (CPC Ad Report + Keyword Report) + manual product count. Returns multi-section text analysis (overview, type breakdown, 7 recommendation flags, top/bottom performers with fallbacks)."
- `discount.py`: "Processes Order Export data. Returns 5 text values: % Diskon TOP SKU, discount range, voucher %, bundle discount %, fake discount flag (>20% threshold)."
- `top_sku.py`: "Processes Order Export + Mass Update data. Returns 2 ranked tables (top 20% by revenue with Kode Variasi enrichment, top 20% with stock levels) + average stock integer."
- `scoring.py`: "75-row scoring system with 11 categories. Fashion/Non-Fashion thresholds. Marketing estimation formulas. Verdict system. Email and WhatsApp output generation. Score range: negative to 100."

**Edit 5 — `calculator_results` table schema:**
- OLD: `score DECIMAL(10,2)` + `details JSONB`
- NEW: Remove `score` column. Keep `details JSONB` as primary storage. Add `output_text TEXT` for text-based outputs.

**Edit 6 — Upload processing flow:**
- OLD: Upload → Parse → Run all 3 calculators in parallel
- NEW: Upload file → Detect type → Store with file_type tag → Check if calculator's required files are all available → Run applicable calculator(s) → Store results

**Edit 7 — Data flow diagram:**
- OLD: Upload → Parse → Calculate → Score → Save
- NEW: Multiple file uploads → Per-calculator file routing → Calculator-specific outputs (text/tables/metrics) → Manual input (40+ fields by scoring category) → Scoring system template → Final score + email/WA output → Save

**Edit 8 — Evaluation data model:**
- `evaluations.score_breakdown` JSONB structure: Per-category scores (operational H7-H9 max 10pts, business H13/H19 max 20pts, visitors H28-H29 max 5pts, promo H42-H43 penalty 15pts, products/status H45-H46 max 15pts, ads H50-H51 penalty+5pts, campaign H57 penalty 10pts, stock H70 -5 to 10pts, discount H73 0 or 5pts), verdict (F75), output messages (G-column values)

### 4.3 UX Design Updates (4 edits)

**Edit 1 — Guided workflow steps:**
- OLD: 5 steps (Brand Info → Store Data → Products → Upload → Review)
- NEW: Revise to align with scoring categories: Step 1 (Brand Info + Operational), Step 2 (Business + Content + Visitors), Step 3 (Promo Tools + Products/Status), Step 4 (File Upload — multi-file with 4 slots per calculator), Step 5 (Ads + Campaign + Competition + Stock + Discount + Review). Exact grouping TBD during story creation.

**Edit 2 — File Upload component:**
- OLD: Single file drop zone accepting `.xlsx/.xls/.zip`
- NEW: 4 file upload slots (CPC Ad Report CSV, Keyword Report CSV, Order Export Excel, Mass Update Excel) with per-slot status indicators and calculator routing labels. Accept `.csv` in addition to Excel.

**Edit 3 — Calculator Results Display:**
- OLD: Score cards showing numeric values per calculator (78, 85, 72)
- NEW: Calc 1 → multi-line text output with flag icons. Calc 2 → product ranking tables (revenue + stock). Calc 3 → discount percentage summary with flag.

**Edit 4 — Score Panel breakdown:**
- OLD: Per-calculator scores (Ads: 78, Discount: 85, Top SKU: 72)
- NEW: Per-category scores matching scoring system (Operational: 10, Business: 20, Promo: -15, Stock: 10, etc.). Final score (0–100 range, can go negative).

### 4.4 Epic/Story Updates (10 stories)

**Story 3.1 — Start Evaluation (Significant update):**
- Evaluation page structure maps to scoring system categories
- Show 4 file upload slots for different calculator inputs
- Brand info populated from VP data + Meeting data enrichment
- Multi-section navigation matching scoring categories

**Story 3.2 — File Upload (Major rework):**
- Support 4 file types: CPC Ad Report CSV, Keyword Report CSV, Order Export Excel, Mass Update Excel
- Per-file-type upload slots with calculator routing
- `brand_uploads` table: `UNIQUE(brand_id, file_type)` instead of `UNIQUE(brand_id)`
- CSV parsing support alongside Excel
- Per-calculator column schema validation

**Story 3.3 — Manual Input (Major rework):**
- ~40+ specific fields organized by scoring categories:
  - Operational (rows 7-11): Pesanan Tidak Terselesaikan, Keterlambatan, Masa Pengemasan, Chat Dibalas, Penilaian
  - Business (rows 13-20): Monthly sales (6 months), conversion rate
  - Content (rows 22-24): Perlu ditingkatkan count, Kualitas baik count
  - Visitors (rows 26-29): Total, Lama, Pengikut
  - Promo (rows 31-41): 11 promo tools with IDR revenue values
  - Products/Status (rows 45-46): Jumlah Produk, Status Toko
  - Ads (rows 48-49): Penjualan iklan, Biaya iklan
  - Campaign (rows 55-56): Sesi dinominasikan, Sesi tersedia
  - Competition (rows 60-63): Top 3 products with prices, keywords, market prices
- Each field with appropriate input type, validation, and benchmark display
- Fashion/Non-Fashion category selection affects thresholds

**Story 3.4 — Ads Keyword Calculator (Complete rewrite):**
- Input: CPC Ad Report CSV + Keyword Placement Report CSV + manual total products (AK1)
- Sheet 1 processing: Column mapping with blank F offset, CleanName helper, AK2 (ad overview with unique product count), AK3 (ad type breakdown by placement/bidding), AK4 (7 recommendation flags)
- Sheet 2 processing: Threshold calculation (AM6-AM10 with caps), TOP ads query (primary + fallback with halved thresholds), BOTTOM ads query (primary + fallback), AL3/AL6-AL9 flags
- Output: Combined text (AK2+AK3+AK4+AL2+AL3+AL5+AL6+AL7+AL8+AL9)
- Test fixtures: MND (AK1=80) and KYPSO (AK1=54) sample data from spec

**Story 3.5 — Discount Check Calculator (Complete rewrite):**
- Input: Order Export Excel (same file as Calculator 2)
- Processing: Urutan calculation (item position within order), price cleaning (remove `.` thousands separator), voucher/paket applied only at Urutan=1, total discount (price diff + voucher + paket), discount % = N/Harga Awal, product summary grouped by Nama Produk, TOP SKU filter (qty > avg AND disc < 100%, top 20% by qty)
- Output: 5 values — % Diskon TOP SKU, Range (min~max of top SKU avg disc), Voucher %, Paket Diskon %, fake discount flag (if total disc/total paid > 20%)
- Test fixtures: SUKA, KYPSO, MND sample outputs from spec

**Story 3.6 — Top SKU Calculator (Complete rewrite):**
- Input: Order Export Excel + Mass Update Excel
- Processing: Per-line extraction (SKU, product+variant label, qty, revenue with order-level discount splitting by Jumlah Produk di Pesan), aggregate by product+variant, rank top 20% by revenue (limit = MAX(ROUND(unique×20%), 20)), enrich with Kode Variasi via XLOOKUP against mass_update, avg selling price (MAXIFS), stock lookup by Kode Variasi
- Output 1: Top selling SKU with revenue table (Kode Variasi, product name, total omzet, rata2 harga jual)
- Output 2: Top selling SKU with stock table (Kode Variasi, nama produk, varian, stock)
- Average stock = ROUND(AVERAGE(all top SKU stocks))
- Test fixtures: KYPSO Oct 2025, MND Nov 2025 sample data from spec

**Story 3.7 — Orchestration (Significant update):**
- Track per-file-type upload status per brand
- Run calculator when ALL its required files are available:
  - Calc 1: needs cpc_ad_report + keyword_report + manual product count
  - Calc 2: needs order_export + mass_update
  - Calc 3: needs order_export (shared with Calc 2)
- When order_export uploaded: run Calc 3 immediately, run Calc 2 only if mass_update also present
- Partial results supported — show completed calculators, indicate pending ones

**Story 3.8 — Results Display (Significant update):**
- Calc 1 display: Multi-line text output preserving formatting (bullet points, flag icons, TOP/BOTTOM ad listings)
- Calc 2 display: Two sortable tables (revenue ranking, stock ranking) with average stock header
- Calc 3 display: Discount summary with percentage values, range, and fake discount flag
- No numeric score cards per calculator — only the final scoring system produces a numeric score

**Story 3.9 — Final Scoring (Complete rewrite):**
- 75-row scoring system with 11 evaluation categories
- Score computation per category with specific benchmarks and point values:
  - Operational (H7-H9): max 10pts, can go negative
  - Business (H13/H19): max 20pts
  - Visitors (H28-H29): max 5pts
  - Promo (H42-H43): penalty scoring up to 15pts (opportunity flags)
  - Products/Status (H45-H46): max 15pts (Mall=10, Star+=5)
  - Ads (H50-H51): penalty 5pts + positive 5pts
  - Campaign (H57): penalty 10pts
  - Stock (H70): -5 to 10pts (from Calculator 2 average stock)
  - Discount (H73): 0 or 5pts (from Calculator 3 fake discount flag)
- Fashion-specific thresholds: ROI >8 (vs >9), marketing G72 +5%, conversion >2% (vs >3%)
- Complex derived formulas: G68 (marketing cost estimation from discount data), G72 (recommended marketing %), G73 (marketing budget recommendation)
- Verdict system (F75): ✔️, ❌, ❌ Non Mall, ❌ No Brand, ❌ Opex, ⭕️, empty
- Output generation: G-column text per metric, G66 conclusion summary, G75 closing message
- Email output (G1): mailto link with structured body from all G-column values
- WhatsApp output (E1): api.whatsapp.com link
- Score range: negative to 100
- **Consider splitting:** 3.9a (scoring calculation + per-category logic) + 3.9b (output generation: email, WA, verdict messages)

**Story 3.10 — Save Evaluation (Update):**
- Save complete evaluation snapshot:
  - All manual inputs organized by scoring category
  - All calculator outputs (text/tables for Calc 1-3)
  - Final score + per-category score breakdown
  - Verdict (F75 value)
  - Scoring template used (Fashion/Non-Fashion)
  - Rule version
  - Generated email output text
  - Evaluator and timestamp

---

## 5. Implementation Handoff

### Change Scope Classification: Minor

All changes are **documentation/artifact updates**. No code changes required — Epic 3 hasn't started. This is the ideal time to correct specifications.

### Action Plan

| # | Action | Priority | Status |
|---|--------|----------|--------|
| 1 | Apply PRD FR updates (10 edits) | P1 | Pending |
| 2 | Apply Architecture updates (8 edits) | P1 | Pending |
| 3 | Apply UX Design updates (4 edits) | P2 | Pending |
| 4 | Rewrite Stories 3.4–3.6 with calculator specs from `logic/` | P1 | Pending |
| 5 | Update Stories 3.1–3.3, 3.7–3.10 | P1 | Pending |
| 6 | Update Epic 4 stories (minor — evaluation data structure) | P2 | Deferred to Epic 4 sprint |
| 7 | Update Epic 5 stories (medium — actual scoring rules) | P2 | Deferred to Epic 5 sprint |

### Success Criteria

- [ ] All PRD FRs (FR6–FR17) updated to match `logic/` specs
- [ ] Architecture reflects multi-file upload, polymorphic calculator results, updated schemas
- [ ] UX spec reflects multi-file upload slots and text-based calculator results
- [ ] Stories 3.4–3.6 have complete ACs based on `logic/` calculator specifications
- [ ] Stories 3.1–3.3, 3.7–3.10 have updated ACs reflecting actual system
- [ ] `logic/` folder referenced as authoritative calculator spec source
- [ ] sprint-status.yaml updated if needed

### Next Steps

1. Apply all approved edits to planning artifacts (PRD, Architecture, UX spec)
2. Rewrite Epic 3 stories in `epics.md` with corrected ACs
3. Complete Story 2.6 (accessibility retrofit) — unrelated, parallel track
4. Begin Epic 3 implementation with corrected stories

### Reference Documents

- `logic/calculator-1-kata-kunci-iklan-shopee.md` — Ads Keyword Calculator spec
- `logic/calculator-2-penjualan.md` — Sales/Top SKU Calculator spec
- `logic/calculator-3-discount-checkup.md` — Discount Check Calculator spec
- `logic/scoring-system-template-sicu.md` — Scoring System Template spec

---

Author: Mr. Door
