# Story 3.4: Ads Keyword Calculator

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system**,
I want **to execute the Ads Keyword Calculator on uploaded CSV data**,
so that **the BD team gets the ads keyword analysis as part of the brand evaluation**.

## Acceptance Criteria

1. **Sheet 1 — CPC Ad Report processing (AK2, AK3, AK4)**
   **Given** a brand has uploaded a CPC Ad Report CSV (`cpc_ad_report` in `brand_uploads`)
   **And** the user has provided the manual input `total_products` (AK1) from `evaluation_inputs.manual_data.products.productCount`
   **When** the calculator is executed
   **Then** produce the following outputs from the parsed CSV data:

   **AK2 — Ad Overview Summary:**
   - Count ads by status: Active (`Berjalan`), Paused (`Dijeda`), Ended (`Berakhir`)
   - Count unique products with non-ended ads where `Jenis Iklan = "Iklan Produk"` using CleanName deduplication (remove text from `[` onward in ad name)
   - Calculate participation percentage: `unique_products / AK1`, formatted as `"0.0%"`
   - Format: `"• Total Iklan: X Aktif, Y Dijeda dan Z Berakhir.\n• Melibatkan N (P%) produk dari total jumlah produk: AK1."`

   **AK3 — Ad Type Breakdown (non-ended ads only, C<>'Berakhir'):**
   - Count by Penempatan Iklan × Mode Bidding × Jenis Iklan:
     - Search Page (`Halaman Pencarian`): total, Otomatis, Manual
     - Recommendation Page (`Halaman Rekomendasi`): total, Otomatis, Manual
     - All Placements (`Semua Penempatan`): total count (NO Jenis Iklan filter — includes shop-level)
     - Shop Ads (`Iklan Toko`): total, Otomatis, Manual
   - Format as multi-line text matching spec exactly

   **AK4 — 7 Recommendation Flags:**
   - Flag 1: Product participation < 50% → "kurang maksimal" else "sudah cukup baik"
   - Flag 2: Active ratio < 50% → "kurang maksimal"; else if product_pct >= 50% → "sudah cukup baik"; else suppressed
   - Flags 3-7: Check ALL ads (including ended) for missing ad types:
     - Flag 3: No `Halaman Pencarian` ads
     - Flag 4: No `Halaman Pencarian` + `Bidding Manual` ads
     - Flag 5: No `Halaman Rekomendasi` ads
     - Flag 6: No `Halaman Rekomendasi` + `Bidding Manual` ads
     - Flag 7: No `Iklan Toko` ads

2. **Sheet 2 — Keyword/Placement Report processing (AL2, AL3, AL5, AL6-AL9)**
   **Given** a brand has uploaded a Keyword Placement Report CSV (`keyword_report` in `brand_uploads`)
   **When** the calculator is executed
   **Then** produce the following outputs:

   **Thresholds (calculated from ALL rows including shop-level):**
   - AM6: `ROUND(AVERAGEIF(GMV > 0))` — GMV threshold for TOP
   - AM7: `MIN(ROUND(AVERAGEIF(ROAS > 0)), 10)` — ROAS threshold for TOP (capped at 10)
   - AM9: `ROUND(AVERAGEIF(Cost > 0))` — Cost threshold for BOTTOM
   - AM10: `MIN(ROUND(AVERAGEIF(ROAS > 0)), 3)` — ROAS threshold for BOTTOM (capped at 3)

   **AL2 — TOP Ads (best performers):**
   - Primary query: `D<>'' AND GMV > AM6 AND ROAS > AM7`, order by GMV desc, limit 5
   - Fallback: `D<>'' AND GMV > AM6/2 AND ROAS > MAX(AM7/2, 6)`, order by GMV desc, limit 5
   - Format per ad: CleanName, `GMV: IDR [formatted "0,0"] {ROAS: [value]}`, Mode Bidding, Jenis + Penempatan + Kata Pencarian

   **AL3 — Top Ads Recommendation:**
   - Count "Bidding Otomatis" substrings in AL2 text: if >= 3 → auto flag
   - Count "GMV Max" substrings in AL2 text: if >= 3 → auto flag
   - Else → "sudah mengandalkan pengaturan manual"

   **AL5 — BOTTOM Ads (worst performers):**
   - Primary query: `D<>'' AND Cost > 100000 AND Cost > AM9 AND ROAS < AM10 AND ROAS < 5`, order by Cost desc, limit 5
   - Fallback: `D<>'' AND Cost > 100000 AND Cost > AM9 AND ROAS < MIN(ROUND(AM10*2), 5) AND ROAS < 5`, order by Cost desc, limit 5
   - Primary format: 4-line per ad; Fallback format: 3-line per ad (Mode Bidding merged with Jenis line)

   **AL6-AL9 — Bottom Bidding Flags (substring checks on AL5 text):**
   - AL6: "Otomatis" in AL5 >= 1 → auto bidding flag
   - AL7: "Bidding Manual" in AL5 >= 1 → manual bidding flag
   - AL8: "Iklan Pencarian Produk: " in AL5 >= 3 → keyword flag
   - AL9: "Auto Bidding" in AL5 >= 1 → auto bidding variant flag

3. **Combined output in correct order**
   **Given** both Sheet 1 and Sheet 2 processing complete
   **When** combining results
   **Then** stack outputs in this exact order for scoring system cell G53:
   1. AK2 (Ad Overview)
   2. AK3 (Ad Type Breakdown)
   3. AK4 (Recommendations)
   4. AL2 (TOP Ads)
   5. AL3 (Top Recommendation)
   6. AL5 (BOTTOM Ads)
   7. AL6 (Bottom Auto Flag)
   8. AL7 (Bottom Manual Flag)
   9. AL8 (Bottom Keywords Flag)
   10. AL9 (Bottom Auto Variant Flag)

4. **Calculator API endpoint**
   **Given** I am authenticated
   **When** I call `POST /api/v1/evaluations/brands/{brand_id}/calculators/ads_keyword`
   **Then** the system loads `cpc_ad_report` and `keyword_report` parsed data from `brand_uploads`
   **And** loads `total_products` from `evaluation_inputs.manual_data.products.productCount`
   **And** executes the Ads Keyword Calculator
   **And** stores results in `calculator_results` table
   **And** returns the calculator output:
   ```json
   {
     "calculator_type": "ads_keyword",
     "output_text": "<combined text>",
     "details": {
       "ak2": "<overview text>",
       "ak3": "<breakdown text>",
       "ak4": "<flags text>",
       "al2": "<top ads text>",
       "al3": "<top recommendation text>",
       "al5": "<bottom ads text>",
       "al6": "<bottom auto flag>",
       "al7": "<bottom manual flag>",
       "al8": "<bottom keywords flag>",
       "al9": "<bottom auto variant flag>",
       "thresholds": { "am6": 3786348, "am7": 5, "am9": 451559, "am10": 3 }
     },
     "calculated_at": "2026-02-11T10:30:00Z"
   }
   ```

5. **Error handling for missing data**
   **Given** the calculator is triggered for a brand
   **When** `cpc_ad_report` or `keyword_report` is not yet uploaded
   **Then** return error with code `CALC_MISSING_DATA` and detail specifying which file(s) are missing

   **Given** the calculator is triggered
   **When** `total_products` (AK1) is not set in manual data
   **Then** return error with code `CALC_MISSING_DATA` and detail: "Manual input 'total_products' (productCount) is required for Ads Keyword Calculator"

6. **Database migration — calculator_results table**
   **Given** the migration is applied
   **When** checking the schema
   **Then** the `calculator_results` table exists with:
   - `id` SERIAL PRIMARY KEY
   - `brand_id` INTEGER REFERENCES brand_vp_data(id)
   - `calculator_type` VARCHAR(50) — `ads_keyword`, `discount`, `top_sku`
   - `details` JSONB (structured intermediate values)
   - `output_text` TEXT (formatted combined text output)
   - `calculated_at` TIMESTAMPTZ DEFAULT NOW()
   - UNIQUE(brand_id, calculator_type) — upsert on recalculation
   - Indexes: `idx_calculator_results_brand_id`, `idx_calculator_results_type`

7. **Test fixtures match spec**
   **Given** MND sample data (AK1=80, Nov 2025)
   **When** the calculator runs
   **Then** AK2 output matches: `"• Total Iklan: 4 Aktif, 1 Dijeda dan 44 Berakhir.\n• Melibatkan 4 (5.0%) produk dari total jumlah produk: 80."`
   **And** thresholds match: AM6=3,786,348, AM7=5, AM9=451,559, AM10=3

   **Given** KYPSO sample data (AK1=54, Nov 2025)
   **When** the calculator runs
   **Then** AK2 output matches: `"• Total Iklan: 3 Aktif, 0 Dijeda dan 7 Berakhir.\n• Melibatkan 2 (3.7%) produk dari total jumlah produk: 54."`

## Tasks / Subtasks

- [x] Task 1: Create database migration for `calculator_results` table (AC: #6)
  - [x] 1.1 Create `backend/app/db/migrations/versions/008_create_calculator_results_table.py`
    - Schema: id, brand_id (FK → brand_vp_data), calculator_type, details JSONB, output_text TEXT, calculated_at
    - UNIQUE constraint on (brand_id, calculator_type)
    - Indexes: brand_id, calculator_type
  - [x] 1.2 Create `backend/app/db/queries/calculator_results.py`
    - `get_results_by_brand(conn, brand_id)` → all calculator results for a brand
    - `get_result_by_type(conn, brand_id, calculator_type)` → single result
    - `upsert_result(conn, brand_id, calculator_type, details, output_text)` → insert/update

- [x] Task 2: Implement Sheet 1 calculator logic (AC: #1)
  - [x] 2.1 Create `backend/app/calculators/ads_keyword.py` with pure function `calculate_ads_keyword(cpc_data, keyword_data, total_products)`
  - [x] 2.2 Implement helper `clean_name(ad_name)`: extract text before first `[` (strip whitespace)
  - [x] 2.3 Implement `calculate_sheet1(rows, total_products)`:
    - AK2: Count by status, count unique products (non-ended, Iklan Produk, CleanName dedup), calculate percentage
    - AK3: Count by type × placement × bidding (non-ended only), format multi-line text
    - AK4: 7 flags (flags 1-2 use non-ended; flags 3-7 use ALL ads)
    - Return dict with ak2, ak3, ak4 text strings
  - [x] 2.4 Implement CSV column mapping: map CSV column positions to semantic names (handle blank column F offset)

- [x] Task 3: Implement Sheet 2 calculator logic (AC: #2)
  - [x] 3.1 Implement `calculate_sheet2(rows)`:
    - Calculate thresholds AM6, AM7, AM9, AM10 from all rows (including shop-level)
    - Implement TOP ads query with primary + fallback, format output text (AL2)
    - Implement AL3 recommendation flag (substring counting on AL2 text)
    - Implement BOTTOM ads query with primary + fallback, format output text (AL5)
    - Implement AL6-AL9 flags (substring counting on AL5 text)
    - Return dict with al2, al3, al5, al6-al9 text strings and thresholds
  - [x] 3.2 Implement `format_top_ad(row)` and `format_bottom_ad(row, is_fallback)` formatters
    - Primary format: 4-line (name, GMV/Cost+ROAS, Mode Bidding, Jenis+Penempatan+Kata)
    - Fallback bottom format: 3-line (Mode Bidding merged with Jenis line)
  - [x] 3.3 Implement `combine_output(sheet1_result, sheet2_result)` → concatenated text in correct order

- [x] Task 4: Create API endpoint and service layer (AC: #4, #5)
  - [x] 4.1 Create `backend/app/modules/evaluations/calculator_service.py`:
    - `run_ads_keyword_calculator(conn, brand_id, user_id)`:
      - Load cpc_ad_report and keyword_report parsed_data from brand_uploads
      - Load total_products from evaluation_inputs.manual_data
      - Validate all required data present (raise CALC_MISSING_DATA if not)
      - Call pure calculator function
      - Upsert result to calculator_results table
      - Return result
  - [x] 4.2 Add endpoint to `backend/app/modules/evaluations/router.py`:
    - `POST /api/v1/evaluations/brands/{brand_id}/calculators/ads_keyword`
    - Response schema matching AC #4 JSON structure
  - [x] 4.3 Add request/response schemas to `backend/app/modules/evaluations/schemas.py`:
    - `CalculatorResultResponse`: calculator_type, output_text, details (dict), calculated_at
    - `CalculatorErrorResponse`: code, detail

- [x] Task 5: Write backend unit tests for calculator (AC: #1, #2, #3, #7)
  - [x] 5.1 Create `backend/tests/unit/calculators/test_ads_keyword.py`:
    - Test clean_name helper: removes `[` suffix, handles no brackets, handles empty
    - Test AK2 with MND data (AK1=80): verify status counts, unique products=4, percentage=5.0%
    - Test AK2 with KYPSO data (AK1=54): verify unique products=2, percentage=3.7%
    - Test AK3 ad type breakdown formatting
    - Test AK4 flags: all 7 flags logic with edge cases
    - Test threshold calculations AM6, AM7, AM9, AM10
    - Test TOP ads query (primary and fallback)
    - Test AL3 recommendation flag (substring counting)
    - Test BOTTOM ads query (primary and fallback, format differences)
    - Test AL6-AL9 flags
    - Test combine_output order
    - Test edge cases: empty data, all ended ads, no shop-level ads

- [x] Task 6: Write backend integration tests (AC: #4, #5)
  - [x] 6.1 Create `backend/tests/integration/api/test_calculators.py`:
    - Test POST endpoint returns calculator result when all data present
    - Test 400/422 error when cpc_ad_report missing
    - Test 400/422 error when keyword_report missing
    - Test 400/422 error when total_products not set
    - Test upsert: running calculator twice updates existing result

- [x] Task 7: Add frontend hooks and types for calculator results (AC: #4)
  - [x] 7.1 Create/update `frontend/src/hooks/useCalculator.ts`:
    - `useCalculatorResults(brandId)`: GET calculator results for a brand
    - `useRunCalculator(brandId, calculatorType)`: POST mutation to trigger calculator
    - Type definitions: `CalculatorResult`, `AdsKeywordDetails`

## Dev Notes

### This Is Primarily a Backend Story

The core work is implementing the calculator pure function and its API. The frontend will get a minimal hook addition, but the full calculator results **display** is Story 3.8. This story provides the calculation engine + API + basic hook.

### Authoritative Calculator Specification

**CRITICAL**: The calculator logic MUST exactly match `logic/calculator-1-kata-kunci-iklan-shopee.md`. This is the single source of truth. The spec includes sample results for MND (AK1=80) and KYPSO (AK1=54) that serve as acceptance test fixtures.

### CSV Column Offset — Critical Implementation Detail

Shopee CSV exports do NOT have the blank column F that exists in the Google Sheet. This means:
- Sheet column G (Tampilan Iklan) = CSV column F
- Sheet column H (Mode Bidding) = CSV column G
- Sheet column I (Penempatan Iklan) = CSV column H

The calculator must work with **CSV column names** as they come from the parser, NOT Sheet column letters. The parser already reads the CSV correctly — use the column names from `REQUIRED_COLUMNS` and the actual CSV headers.

**CSV columns available from parser** (cpc_ad_report):
- `Nama Iklan`, `Jenis Iklan`, `Kode Produk`, `Penempatan Iklan`, `Biaya`
- Plus additional columns: `Status`, `Mode Bidding`, `Tampilan Iklan`, etc.

**CSV columns available from parser** (keyword_report):
- `Kata Pencarian/Penempatan`, `Jenis Iklan`, `Kode Produk`, `Penempatan Iklan`, `Biaya`
- Plus: `Omzet Penjualan`, `Efektifitas Iklan`, `Mode Bidding`, etc.

### Parsed Data Structure in brand_uploads

The upload parser stores data as JSONB in `brand_uploads.parsed_data`:
```json
{
  "columns": ["Nama Iklan", "Status", "Jenis Iklan", ...],
  "data": [
    {"Nama Iklan": "...", "Status": "Berjalan", "Jenis Iklan": "Iklan Produk", ...},
    ...
  ],
  "row_count": 49
}
```

The calculator must reconstruct a Polars DataFrame from this JSONB or work with the list of dicts directly. Recommended: use `pl.DataFrame(parsed_data["data"])` to reconstruct.

### Calculator Architecture — Pure Function Pattern

Per architecture doc, calculators MUST be pure functions with no I/O:
```python
# calculators/ads_keyword.py — PURE, no database access
def calculate_ads_keyword(
    cpc_data: list[dict],      # parsed rows from cpc_ad_report
    keyword_data: list[dict],  # parsed rows from keyword_report
    total_products: int,       # AK1 from manual input
) -> AdsKeywordResult:
    ...
```

The service layer (`modules/evaluations/calculator_service.py`) handles all I/O:
- Load parsed data from `brand_uploads`
- Load manual inputs from `evaluation_inputs`
- Call pure calculator
- Store results in `calculator_results`

### Number Formatting

Indonesian number formatting for the output text:
- GMV/Cost: `"IDR 26,433,781"` — use comma as thousands separator (NOT dot) based on sample output
- ROAS: decimal format `5.68` (no thousands separator needed)
- Percentages: `"5.0%"` or `"3.7%"` — one decimal place

**Note**: The sample output in the spec uses comma separators for IDR values (e.g., `IDR 26,433,781`), NOT Indonesian dot separators. Follow the spec's sample output formatting exactly.

### AK1 (total_products) Source

The `total_products` value (AK1) comes from the manual data form (Story 3.3):
- Stored at: `evaluation_inputs.manual_data` → `products.productCount`
- The service layer must read this value before calling the calculator
- If null/missing, return `CALC_MISSING_DATA` error

### Project Structure Notes

**New files to create:**

```
backend/app/db/migrations/versions/008_create_calculator_results_table.py
backend/app/db/queries/calculator_results.py
backend/app/calculators/ads_keyword.py
backend/app/modules/evaluations/calculator_service.py
backend/tests/unit/calculators/__init__.py
backend/tests/unit/calculators/test_ads_keyword.py
backend/tests/integration/api/test_calculators.py
frontend/src/hooks/useCalculator.ts
```

**Existing files to modify:**

```
backend/app/modules/evaluations/router.py  ← ADD calculator endpoint
backend/app/modules/evaluations/schemas.py ← ADD CalculatorResultResponse
```

### Architecture Compliance

**Backend Pattern (MUST follow):**
- Calculator in `calculators/ads_keyword.py` — PURE function, no I/O, no database access
- Service orchestration in `modules/evaluations/calculator_service.py` — handles all I/O
- Router endpoint in `modules/evaluations/router.py` — REST convention
- Database queries in `db/queries/calculator_results.py` — parameterized SQL with $1, $2
- Exception chaining: always `raise ... from e`
- Structured error codes: `CALC_MISSING_DATA`, `CALC_EXECUTION_FAILED`

**Database Pattern (MUST follow):**
- asyncpg + parameterized SQL (no ORM)
- Migration in Alembic raw SQL mode
- UNIQUE constraint for upsert on (brand_id, calculator_type)
- Indexes on brand_id and calculator_type

**Testing Pattern (MUST follow):**
- Unit tests: `backend/tests/unit/calculators/test_ads_keyword.py`
- Integration tests: `backend/tests/integration/api/test_calculators.py`
- Use spec sample data (MND AK1=80, KYPSO AK1=54) as test fixtures
- Run: `cd backend && uv run python -m pytest -v`

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| polars | existing | DataFrame operations for calculator logic | Installed |
| asyncpg | existing | Database queries (calculator_results) | Installed |
| fastapi | existing | API endpoint | Installed |
| pydantic | existing | Request/response schemas | Installed |
| pytest | existing | Unit + integration tests | Installed |

**No new dependencies needed.** All required libraries are already installed.

### Testing Requirements

**Backend Unit Tests (pytest):**

```
backend/tests/unit/calculators/test_ads_keyword.py:
  - test_clean_name_removes_bracket_suffix
  - test_clean_name_no_brackets
  - test_clean_name_empty_string
  - test_ak2_mnd_sample (AK1=80, expected: 4 aktif, 1 dijeda, 44 berakhir, 4 products, 5.0%)
  - test_ak2_kypso_sample (AK1=54, expected: 3 aktif, 0 dijeda, 7 berakhir, 2 products, 3.7%)
  - test_ak3_type_breakdown_formatting
  - test_ak3_non_ended_only_filter
  - test_ak4_flag1_low_participation
  - test_ak4_flag1_good_participation
  - test_ak4_flag2_low_active_ratio
  - test_ak4_flag2_suppressed_when_flag1_low
  - test_ak4_flags3_to_7_all_ads_check
  - test_thresholds_calculation
  - test_thresholds_am7_capped_at_10
  - test_thresholds_am10_capped_at_3
  - test_top_ads_primary_query
  - test_top_ads_fallback_when_no_primary_results
  - test_al3_auto_bidding_flag
  - test_al3_gmv_max_flag
  - test_al3_manual_bidding_positive
  - test_bottom_ads_primary_query
  - test_bottom_ads_fallback_format_difference
  - test_al6_to_al9_flags
  - test_combine_output_correct_order
  - test_empty_data_handling
```

**Backend Integration Tests (pytest):**

```
backend/tests/integration/api/test_calculators.py:
  - test_run_ads_keyword_calculator_success
  - test_run_ads_keyword_missing_cpc_report
  - test_run_ads_keyword_missing_keyword_report
  - test_run_ads_keyword_missing_total_products
  - test_run_ads_keyword_upsert_on_recalculation
```

### Previous Story Intelligence

**From Story 3.3 (Manual Data Input Form):**
- `evaluation_inputs.manual_data` stores all manual data as nested JSONB
- `products.productCount` is where AK1 (total_products) lives
- Auto-save on blur means the value may be available before the user explicitly triggers calculation
- React Hook Form manages form state; auto-save via `useSaveEvaluationInputs` mutation

**From Story 3.2 (Data File Upload):**
- `brand_uploads.parsed_data` stores parsed CSV data as `{"columns": [...], "data": [...], "row_count": N}`
- Parser already handles Shopee CSV metadata (7 skip rows), column validation
- Upload service maps `cpc_ad_report` → calculator_target "ads_keyword"
- Upload service maps `keyword_report` → calculator_target "ads_keyword"
- File type is stored in `brand_uploads.file_type` column

**From Code Reviews:**
- Exception chaining: always `raise ... from e`
- Response schemas must match ACs field-by-field
- ILIKE queries need ESCAPE clause (not applicable here but good practice)
- File List must include ALL changed files

### Git Intelligence

Recent commits show Story 3.3 complete and merged to develop:
```
15a7e63 Merge feature/3-3-manual-data-input-form into develop
4c7f4a6 Update CLAUDE.md — remove redundant sections
fc27b66 Fix 10 code review issues for Story 3.3 (3H/4M/3L)
0811d02 Mark Story 3.3 complete — all tasks done, status → review
a70be42 Add comprehensive tests for manual data forms (149 tests pass)
```

**Patterns to follow:**
- Feature branch naming: `feature/3-4-ads-keyword-calculator`
- Atomic commits per task
- Tests committed alongside implementation

### References

- [Source: logic/calculator-1-kata-kunci-iklan-shopee.md — Complete calculator specification with sample data]
- [Source: _bmad-output/planning-artifacts/epics.md — Story 3.4 ACs, FR12]
- [Source: _bmad-output/planning-artifacts/architecture.md — Calculator pure function pattern, module boundaries]
- [Source: _bmad-output/planning-artifacts/prd.md — FR12: Ads Keyword Calculator requirements]
- [Source: _bmad-output/implementation-artifacts/3-3-manual-data-input-form.md — ManualData JSONB structure, products.productCount]
- [Source: backend/app/modules/upload/parser.py — REQUIRED_COLUMNS, CSV parsing, SHOPEE_CSV_SKIP_ROWS]
- [Source: backend/app/db/queries/uploads.py — get_upload_by_type query pattern]
- [Source: _bmad-output/lessons-learned.md — Code review patterns, testing patterns]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

- Verified MND CPC data: 49 rows (4 Berjalan, 1 Dijeda, 44 Berakhir) — matches spec
- Verified MND keyword thresholds: AM6=3,786,348, AM7=5, AM9=451,559, AM10=3 — matches spec
- Verified TOP 5 ads and BOTTOM fallback (1 ad) match spec sample output exactly
- Used actual MND CSV files to validate calculator logic against real data

### Completion Notes List

- ✅ Task 1: Migration 008 + query module with get_results_by_brand, get_result_by_type, upsert_result
- ✅ Task 2: Sheet 1 calculator — AK2 (status overview), AK3 (type breakdown), AK4 (7 flags)
- ✅ Task 3: Sheet 2 calculator — thresholds, TOP/BOTTOM with fallback, AL3/AL6-AL9 flags, combine_output
- ✅ Task 4: Service layer (calculator_service.py) + POST endpoint + CalculatorResultResponse schema
- ✅ Task 5: 57 unit tests covering all calculator logic, edge cases, and both MND/KYPSO fixtures
- ✅ Task 6: 6 integration tests — success, missing data (3 variants), upsert, auth
- ✅ Task 7: useRunCalculator hook + CalculatorResult/AdsKeywordDetails types + apiClient paths

### Senior Developer Review (AI)

**Reviewer:** Mr. Door | **Date:** 2026-02-11 | **Model:** Claude Opus 4.6

**Result:** APPROVED after fixes

**Issues Found:** 3 High, 3 Medium, 3 Low — all 9 fixed in commit `3312646`

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| H1 | HIGH | No error wrapping around calculator execution | Added try/except with CALC_EXECUTION_FAILED |
| H2 | HIGH | No validation of parsed_data structure | Added `_extract_parsed_data()` validator |
| H3 | HIGH | AC #7 threshold validation missing from tests | Added spec-value threshold test |
| M4 | MEDIUM | AL8 substring check may not trigger (spec ambiguity) | Added comment + test documenting behavior |
| M5 | MEDIUM | No dedicated CalculatorException class | Added to exceptions.py |
| M6 | MEDIUM | Frontend error discarded in useCalculator | Propagate actual API error |
| L7 | LOW | MND fixtures approximate | Addressed by H3 focused test |
| L8 | LOW | Redundant runtime type guard | Removed dead code |
| L9 | LOW | No AL8 trigger test | Added conditional trigger test |

**Post-fix test count:** 194 passing (was 192)

### Change Log

- 2026-02-11: Code review fixes — 9 issues (3H/3M/3L) all resolved, 194 tests passing
- 2026-02-11: Story 3.4 implementation complete — all 7 tasks done, 63 new tests (57 unit + 6 integration), all 192 backend tests passing

### File List

- backend/app/core/exceptions.py (modified — added CalculatorException)
- backend/app/db/migrations/versions/008_create_calculator_results_table.py (new)
- backend/app/db/queries/calculator_results.py (new)
- backend/app/calculators/ads_keyword.py (new)
- backend/app/modules/evaluations/calculator_service.py (new)
- backend/app/modules/evaluations/router.py (modified)
- backend/app/modules/evaluations/schemas.py (modified)
- backend/tests/unit/calculators/__init__.py (new)
- backend/tests/unit/calculators/test_ads_keyword.py (new)
- backend/tests/integration/api/test_calculators.py (new)
- frontend/src/hooks/useCalculator.ts (new)
- frontend/src/services/apiClient.ts (modified)
