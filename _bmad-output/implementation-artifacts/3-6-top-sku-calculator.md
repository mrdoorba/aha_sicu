# Story 3.6: Top SKU Calculator

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system**,
I want **to execute the Top SKU Calculator on uploaded Order Export and Mass Update data**,
so that **the BD team gets the SKU analysis (top-selling products with revenue and stock) as part of the brand evaluation**.

## Acceptance Criteria

1. **Per-line data extraction from Order Export**
   **Given** a brand has uploaded Order Export Excel (`order_export` in `brand_uploads`) AND Mass Update Excel (`mass_update` in `brand_uploads`)
   **When** the calculator is executed

   **Then** extract per-line data from order_export rows:

   **SKU (BO):**
   `Nomor Referensi SKU`

   **Product+Variant label (BP):**
   `Nama Produk & " - " & Nama Variasi`

   **Quantity (BQ):**
   `Jumlah`

   **Revenue per line (BR):**
   ```
   Revenue = (Harga Setelah Diskon × Jumlah)
             - (Voucher Ditanggung Penjual / Jumlah Produk di Pesan)
             - (Cashback Koin / Jumlah Produk di Pesan)
             + (Diskon dari Shopee / Jumlah Produk di Pesan)
   ```

   **Price cleaning:**
   - Remove `.` thousands separator from all price fields (`Harga Setelah Diskon`, `Voucher Ditanggung Penjual`, `Cashback Koin`, `Diskon Dari Shopee`) before converting to numbers
   - `Jumlah` and `Jumlah Produk di Pesan` are already numeric — use `_safe_num()`

   **Important**: ALL orders are used regardless of status (Selesai, Batal, etc.). There is NO status filter. Order-level discounts (voucher, cashback, Shopee discount) are split evenly across all items in the order using `Jumlah Produk di Pesan`.

2. **Aggregate by Product+Variant**
   **Given** per-line data is extracted
   **When** aggregating
   **Then** group by exact match on **Product+Variant label** (`Nama Produk & " - " & Nama Variasi`):
   - **Total Quantity**: `SUM(Jumlah)` per product+variant
   - **Total Revenue (Omzet)**: `SUM(Revenue)` per product+variant

3. **Rank top products**
   **Given** aggregated product data
   **When** ranking
   **Then** sort by Total Omzet descending
   **And** limit = `MAX(ROUND(unique_products × 20%), 20)` — minimum 20 items (differs from Discount Calculator which has NO minimum)
   **And** if fewer than 20 unique products exist, return all products

4. **Enrich with Kode Variasi from Mass Update**
   **Given** top products are ranked
   **When** enriching with mass_update data
   **Then** for each top product:
   - Prepare mass_update name column: `Nama Produk & " - " & Nama Variasi`
   - XLOOKUP the top product's label against mass_update name column
   - If match found → return `Kode Variasi` from mass_update
   - If no match → `"Kode Variasi tidak ditemukan"`

5. **Calculate Rata-rata Harga Jual (Average Selling Price)**
   **Given** top products are identified
   **When** calculating selling price
   **Then** for each top product:
   `Rata2 Harga Jual = MAXIFS(Revenue_per_line, Product+Variant_label, this_product)`
   This is the **maximum single-line revenue** for that product across all orders.

6. **Stock lookup**
   **Given** Kode Variasi is resolved for each top product
   **When** looking up stock
   **Then** use Kode Variasi to lookup `Stok` from mass_update (match by Kode Variasi)
   **And** if Kode Variasi was "tidak ditemukan" → stock = 0

7. **Average stock metric**
   **Given** stock values are resolved for all top products
   **When** computing average
   **Then** `Average Stock = ROUND(AVERAGE(stock of all Top 20% products))` — integer

8. **Two output tables**
   **Given** all calculations are complete
   **When** generating output

   **Then produce Output 1 — Top Selling SKU with Revenue table:**

   | Column | Description |
   |--------|-------------|
   | Kode Variasi | From mass_update lookup (or "Kode Variasi tidak ditemukan") |
   | Product Name | Product + Variant label (BP) |
   | Total Omzet | Sum of revenue per product (IDR integer) |
   | Rata2 Harga Jual | Max single-line revenue per product (IDR integer) |

   **And produce Output 2 — Top Selling SKU with Stock table:**

   | Column | Description |
   |--------|-------------|
   | Kode Variasi | Same as Output 1 |
   | Nama Produk | Product name only (without variant) |
   | Varian | Variant name only |
   | Stok | Stock from mass_update (0 if tidak ditemukan) |

   **And** return average stock as a single integer metric

9. **Calculator API endpoint**
   **Given** I am authenticated
   **When** I call `POST /api/v1/evaluations/brands/{brand_id}/calculators/top_sku`
   **Then** the system loads `order_export` AND `mass_update` parsed data from `brand_uploads`
   **And** validates both uploads exist and have required columns
   **And** executes the Top SKU Calculator
   **And** stores results in `calculator_results` table (upsert on brand_id + calculator_type)
   **And** returns the calculator output:
   ```json
   {
     "calculator_type": "top_sku",
     "output_text": "",
     "details": {
       "output_1": [
         {
           "kode_variasi": "301913525888",
           "product_name": "KYPSO Sovereign ... - Cokelat Muda",
           "total_omzet": 4355000,
           "rata2_harga_jual": 387000
         }
       ],
       "output_2": [
         {
           "kode_variasi": "301913525888",
           "nama_produk": "KYPSO Sovereign ...",
           "varian": "Cokelat Muda",
           "stok": 782
         }
       ],
       "average_stock": 123,
       "product_count": 20,
       "total_unique_products": 95
     },
     "calculated_at": "2026-02-11T10:30:00Z"
   }
   ```

10. **Error handling for missing data**
    **Given** the calculator is triggered for a brand
    **When** `order_export` has not been uploaded
    **Then** return error with code `CALC_MISSING_DATA` and detail: "Order Export (order_export) has not been uploaded for this brand"

    **Given** `mass_update` has not been uploaded
    **When** attempting calculation
    **Then** return error with code `CALC_MISSING_DATA` and detail: "Mass Update (mass_update) has not been uploaded for this brand"

    **Given** uploaded data has missing required columns
    **When** column validation fails
    **Then** return error with code `CALC_MISSING_DATA` specifying which columns are missing

11. **Test fixtures match spec**
    **Given** KYPSO Oct 2025 sample data
    **When** the calculator runs
    **Then** output produces 20 products
    **And** top product = "KYPSO Sovereign ... - Cokelat Muda" at 4,355,000 omzet
    **And** average stock = 123

    **Given** MND Nov 2025 sample data
    **When** the calculator runs
    **Then** output produces 20 products
    **And** top product = "Seoul Shoulder Bag ... - Black" at 19,593,731 omzet
    **And** average stock = 125

## Tasks / Subtasks

- [x] Task 1: Implement top SKU calculator pure function (AC: #1, #2, #3, #4, #5, #6, #7, #8)
  - [x] 1.1 Create `backend/app/calculators/top_sku.py` with result dataclass `TopSkuResult`
  - [x] 1.2 Implement `_clean_price(value)`: reuse pattern from discount.py — remove `.` thousands separator, convert to float
  - [x] 1.3 Implement `_safe_num(value)`: reuse pattern from discount.py — coerce to float
  - [x] 1.4 Implement `_extract_per_line(rows)`: extract SKU, product+variant label, quantity, revenue per line with the revenue formula
  - [x] 1.5 Implement `_aggregate_by_product(line_items)`: group by product+variant label, sum qty and revenue
  - [x] 1.6 Implement `_rank_top_products(aggregated)`: sort by omzet desc, limit = MAX(ROUND(20%), 20)
  - [x] 1.7 Implement `_build_mass_update_lookup(mass_update_data)`: create name→kode_variasi and kode_variasi→stok lookup dicts
  - [x] 1.8 Implement `_enrich_with_mass_update(top_products, mu_lookup)`: add kode_variasi, rata2_harga_jual, stok per product
  - [x] 1.9 Implement `_build_output_tables(enriched_products)`: generate output_1 and output_2 table structures
  - [x] 1.10 Implement `_calculate_average_stock(enriched_products)`: ROUND(AVERAGE(all stocks))
  - [x] 1.11 Implement main entry `calculate_top_sku(order_data, mass_update_data)` → `TopSkuResult`

- [x] Task 2: Create API endpoint and service layer (AC: #9, #10)
  - [x] 2.1 Add required columns validation for `order_export` top_sku usage and `mass_update` to `_REQUIRED_COLUMNS` in calculator_service.py
  - [x] 2.2 Add `run_top_sku_calculator(brand_id, user_id)` to `calculator_service.py`:
    - Load `order_export` AND `mass_update` parsed_data from `brand_uploads`
    - Validate both present (raise CALC_MISSING_DATA if not)
    - Validate required columns for both file types
    - Call pure calculator function
    - Upsert result to `calculator_results` table
    - Return result
  - [x] 2.3 Add endpoint to `router.py`:
    - `POST /api/v1/evaluations/brands/{brand_id}/calculators/top_sku`
    - Response schema: existing `CalculatorResultResponse`
  - [x] 2.4 Import and wire up in `router.py`

- [x] Task 3: Write backend unit tests for calculator (AC: #1, #2, #3, #4, #5, #6, #7, #8, #11)
  - [x] 3.1 Create `backend/tests/unit/calculators/test_top_sku.py`:
    - Test `_clean_price`: handles dots, empty, non-numeric (same pattern as discount)
    - Test `_safe_num`: handles None, strings, dashes
    - Test `_extract_per_line`: revenue formula correctness
    - Test revenue: voucher/cashback/shopee_discount divided by jumlah_produk_di_pesan
    - Test revenue: price cleaning before multiplication
    - Test `_aggregate_by_product`: groups by exact product+variant label
    - Test `_aggregate_by_product`: sums qty and revenue correctly
    - Test `_rank_top_products`: sorts by omzet descending
    - Test `_rank_top_products`: limit = MAX(ROUND(20%), 20)
    - Test `_rank_top_products`: returns all if fewer than 20 unique products
    - Test `_build_mass_update_lookup`: builds name→kode and kode→stok mappings
    - Test `_enrich_with_mass_update`: matches by product+variant label
    - Test `_enrich_with_mass_update`: "Kode Variasi tidak ditemukan" when no match
    - Test `_enrich_with_mass_update`: stok = 0 when kode_variasi not found
    - Test rata2_harga_jual: max single-line revenue per product
    - Test `_calculate_average_stock`: ROUND(AVERAGE(all stocks))
    - Test output_1 table structure: kode_variasi, product_name, total_omzet, rata2_harga_jual
    - Test output_2 table structure: kode_variasi, nama_produk (without variant), varian, stok
    - Test empty data handling
    - Test single product single order
    - Test KYPSO-like sample: verify top product and average stock pattern
    - Test MND-like sample: verify top product and average stock pattern

- [x] Task 4: Write backend integration tests (AC: #9, #10)
  - [x] 4.1 Add top_sku tests to `backend/tests/integration/api/test_calculators.py`:
    - Test POST endpoint returns calculator result when both files present
    - Test 400 error when order_export missing
    - Test 400 error when mass_update missing
    - Test 400 error when required columns missing
    - Test upsert: running calculator twice updates existing result
    - Test authentication required

- [x] Task 5: Add frontend hook for top SKU calculator (AC: #9)
  - [x] 5.1 Update `frontend/src/hooks/useCalculator.ts`:
    - Add `TopSkuDetails` type matching the details structure
    - Add `'top_sku'` to `CalculatorType` union
    - Add top_sku path to `CALCULATOR_PATHS`
    - Update `CalculatorDetails` union type
  - [x] 5.2 Update `frontend/src/services/apiClient.ts`:
    - Add top_sku calculator endpoint path type

## Dev Notes

### This Is Primarily a Backend Story

Like Stories 3.4 and 3.5, the core work is implementing the calculator pure function and its API. The frontend gets minimal type additions. The full calculator results **display** is Story 3.8.

### Authoritative Calculator Specification

**CRITICAL**: The calculator logic MUST exactly match `logic/calculator-2-penjualan.md`. This is the single source of truth. Key sample outputs:
- KYPSO Oct 2025: 20 products, top = "KYPSO Sovereign ... - Cokelat Muda" at 4,355,000 omzet, avg stock 123
- MND Nov 2025: 20 products, top = "Seoul Shoulder Bag ... - Black" at 19,593,731 omzet, avg stock 125

### Two Input Files Required

Unlike Calculator 3 (Discount) which only needs `order_export`, the Top SKU Calculator requires BOTH:
1. **order_export** — Order Export Excel (same file used by Calculator 3)
2. **mass_update** — Mass Update / Sales Info Excel (unique to Calculator 2)

Both must be uploaded and parsed before this calculator can run. The service layer must validate both exist.

| Aspect | Calculator 2 (Top SKU) | Calculator 3 (Discount) |
|--------|----------------------|------------------------|
| Input files | order_export + mass_update | order_export only |
| Ranking | By revenue (omzet) | By quantity (Qty) |
| Grouping | Nama Produk + " - " + Variasi | Nama Produk only |
| Voucher handling | Divided by Jumlah Produk di Pesan | Applied only to Urutan=1 |
| TOP SKU limit | MAX(ROUND(20%), 20) — minimum 20 | ROUND(20%) — no minimum |
| Output format | Two tables + average stock integer | 5 text values + flag |
| Purpose | Identify top revenue products + stock | Analyze discount health |

### Revenue Formula — Critical Differences from Discount Calculator

The revenue formula for Top SKU is DIFFERENT from the discount formula. Key differences:
- **Multiplied by quantity**: `Harga Setelah Diskon × Jumlah` (discount just uses raw price)
- **Order-level adjustments divided by items in order**: voucher/cashback/Shopee discount are each divided by `Jumlah Produk di Pesan` (discount divides differently — applies only at Urutan=1)
- **Shopee discount ADDED back**: `+ (Diskon dari Shopee / Jumlah Produk di Pesan)` — this is added, not subtracted
- **Uses different columns**: `Nomor Referensi SKU`, `Nama Variasi`, `Jumlah Produk di Pesan`, `Cashback Koin`, `Diskon Dari Shopee` — none of these are used by Calculator 3

### Mass Update File Structure — Critical

Mass Update Excel has **2 system metadata rows** before the header:
- Row 1-2: System metadata
- Row 3: Headers
- Row 4+: Data

The parser already handles this: `parse_excel(file_bytes, header_row=2)` for mass_update. The parsed_data stored in `brand_uploads.parsed_data` will already have correct column headers.

Mass Update `Nama Produk` and `Nama Variasi` columns are used to build the lookup label: `Nama Produk & " - " & Nama Variasi`. This must match EXACTLY against the same label built from order_export.

**Warning**: Products with names that differ between order export and mass update (e.g., old/short names vs new/long names) will NOT match. This is expected behavior — display "Kode Variasi tidak ditemukan".

### Parsed Data Structure in brand_uploads

Both files store data as JSONB in `brand_uploads.parsed_data`:
```json
{
  "columns": ["No. Pesanan", "Nama Produk", ...],
  "data": [
    {"No. Pesanan": "240101ABC", "Nama Produk": "...", ...},
    ...
  ],
  "row_count": 500
}
```

### Columns Used from Order Export

From the parser's `REQUIRED_COLUMNS["order_export"]`:
- `Nama Produk` — product name (for grouping label)
- `Nomor Referensi SKU` — SKU reference
- `Nama Variasi` — variant name (for grouping label)
- `Harga Setelah Diskon` — discounted price (Indonesian format: `.` = thousands)
- `Jumlah` — quantity per line item
- `Jumlah Produk di Pesan` — total items in the order (for splitting order-level discounts)
- `Voucher Ditanggung Penjual` — seller voucher (order-level)
- `Cashback Koin` — coin cashback (order-level)
- `Diskon Dari Shopee` — Shopee discount (order-level, ADDED back to revenue)

### Columns Used from Mass Update

From the parser's `REQUIRED_COLUMNS["mass_update"]`:
- `Nama Produk` — product name (for building lookup label)
- `Nama Variasi` — variant name (for building lookup label)
- `Kode Variasi` — variant code (returned as identifier)
- `Stok` — current stock count

**Note**: `Kode Produk`, `SKU`, `Harga` columns exist in mass_update but are NOT needed by this calculator. Only `Nama Produk`, `Nama Variasi`, `Kode Variasi`, and `Stok` are used.

### Price Format Handling — Critical

Indonesian price format uses `.` as thousands separator:
- `"529.000"` → 529000
- `"1.250.000"` → 1250000
- `"0"` → 0
- `""` or missing → 0

Reuse the `_clean_price()` pattern from `calculators/discount.py`: strip dots then convert to number.

### How Output Feeds into Scoring System

- **D70**: Average Stock number (integer). Scoring system uses:
  - D70 >= 24 → score 10
  - D70 >= 12 → score 5
  - D70 < 12 → score -5
- Both output tables are used for reference in the scoring system
- The `output_text` field can be empty string (tables don't have a text representation — they're stored in `details` JSONB)

### Project Structure Notes

**New files to create:**

```
backend/app/calculators/top_sku.py
backend/tests/unit/calculators/test_top_sku.py
```

**Existing files to modify:**

```
backend/app/modules/evaluations/calculator_service.py  ← ADD run_top_sku_calculator, _REQUIRED_COLUMNS for mass_update
backend/app/modules/evaluations/router.py              ← ADD top_sku calculator endpoint
backend/tests/integration/api/test_calculators.py      ← ADD top_sku integration tests
frontend/src/hooks/useCalculator.ts                    ← ADD TopSkuDetails type
frontend/src/services/apiClient.ts                     ← ADD top_sku endpoint path type
```

### Architecture Compliance

**Backend Pattern (MUST follow):**
- Calculator in `calculators/top_sku.py` — PURE function, no I/O, no database access
- Service orchestration in `modules/evaluations/calculator_service.py` — handles all I/O
- Router endpoint in `modules/evaluations/router.py` — REST convention
- Database queries reuse existing `db/queries/calculator_results.py` (`upsert_result`, `get_result_by_type`)
- Exception chaining: always `raise ... from e`
- Structured error codes: `CALC_MISSING_DATA`, `CALC_EXECUTION_FAILED`

**Calculator Architecture (MUST follow):**
```python
# calculators/top_sku.py — PURE, no database access
def calculate_top_sku(
    order_data: list[dict],       # parsed rows from order_export
    mass_update_data: list[dict],  # parsed rows from mass_update
) -> TopSkuResult:
    ...
```

The service layer (`calculator_service.py`) handles all I/O:
- Load parsed data from `brand_uploads` for BOTH file types
- Validate both exist, validate columns
- Call pure calculator
- Store results in `calculator_results`

**Database Pattern (MUST follow):**
- Reuse existing `calculator_results` table (created in Story 3.4, migration 008)
- calculator_type = `"top_sku"`
- UNIQUE(brand_id, calculator_type) enables upsert

**Testing Pattern (MUST follow):**
- Unit tests: `backend/tests/unit/calculators/test_top_sku.py`
- Integration tests: `backend/tests/integration/api/test_calculators.py` (add to existing file)
- Run: `cd backend && uv run python -m pytest -v`

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| asyncpg | existing | Database queries (calculator_results, brand_uploads) | Installed |
| fastapi | existing | API endpoint | Installed |
| pydantic | existing | Response schemas (reuse CalculatorResultResponse) | Installed |
| pytest | existing | Unit + integration tests | Installed |

**No new dependencies needed.** All required libraries are already installed.

### Testing Requirements

**Backend Unit Tests (pytest):**

```
backend/tests/unit/calculators/test_top_sku.py:
  - test_clean_price_removes_dots
  - test_clean_price_empty_string
  - test_clean_price_zero
  - test_safe_num_none
  - test_safe_num_string_dash
  - test_extract_per_line_revenue_formula
  - test_extract_per_line_price_cleaning
  - test_extract_per_line_order_level_discount_splitting
  - test_extract_per_line_shopee_discount_added_back
  - test_aggregate_groups_by_product_variant_label
  - test_aggregate_sums_qty_and_revenue
  - test_aggregate_deduplicates_same_product
  - test_rank_sorts_by_omzet_descending
  - test_rank_limit_max_round_20pct_20
  - test_rank_returns_all_if_fewer_than_20
  - test_rank_minimum_20_enforced
  - test_mass_update_lookup_builds_name_to_kode_mapping
  - test_mass_update_lookup_builds_kode_to_stok_mapping
  - test_enrich_matches_by_label
  - test_enrich_tidak_ditemukan_when_no_match
  - test_enrich_stok_zero_when_kode_not_found
  - test_rata2_harga_jual_is_max_single_line_revenue
  - test_average_stock_rounded_integer
  - test_output_1_table_structure
  - test_output_2_splits_nama_and_varian
  - test_empty_order_data
  - test_empty_mass_update_data
  - test_single_product_single_order
  - test_kypso_sample_pattern
  - test_mnd_sample_pattern
```

**Backend Integration Tests (pytest):**

```
backend/tests/integration/api/test_calculators.py (add to existing):
  - test_run_top_sku_calculator_success
  - test_run_top_sku_missing_order_export
  - test_run_top_sku_missing_mass_update
  - test_run_top_sku_missing_columns
  - test_run_top_sku_upsert_on_recalculation
  - test_run_top_sku_auth_required
```

### Previous Story Intelligence

**From Story 3.5 (Discount Check Calculator):**
- Pure function pattern works well: `calculate_discount(data) → DiscountResult`
- Service layer pattern: load from brand_uploads, validate, call calculator, upsert result
- `_extract_parsed_data()` helper validates parsed_data structure — reuse this
- `_validate_columns()` validates column presence — extend with mass_update columns
- `CalculatorResultResponse` schema already exists — reuse it directly
- `calculator_results` table already exists with UNIQUE(brand_id, calculator_type) — no migration needed
- Integration test pattern: create brand, create upload, run calculator, verify result
- Code review found: missing error wrapping (H1), missing parsed_data validation (H2) — top_sku calculator must include both from the start
- Code review found: column validation via `_validate_columns()` is important — include for both order_export and mass_update

**From Story 3.4 (Ads Keyword Calculator):**
- Multiple input files pattern: ads_keyword needs cpc_ad_report + keyword_report + manual input
- Service layer loads each file separately and validates each
- Same pattern needed for top_sku: load order_export + mass_update separately

**From Code Reviews:**
- Exception chaining: always `raise ... from e`
- Response schemas must match ACs field-by-field
- File List must include ALL changed files
- Wrap calculator execution in try/except for CALC_EXECUTION_FAILED

### Git Intelligence

Recent commits show Story 3.5 merged to develop:
```
571f3d3 Merge feature/3-5-discount-check-calculator into develop
61c5ab6 Mark Story 3.5 done after code review — all issues resolved
4892ce0 Fix 6 code review issues for Story 3.5 (1H/2M/3L)
```

**Patterns to follow:**
- Feature branch naming: `feature/3-6-top-sku-calculator`
- Atomic commits per task
- Tests committed alongside implementation

### References

- [Source: logic/calculator-2-penjualan.md — Complete calculator specification with sample outputs for KYPSO and MND]
- [Source: _bmad-output/planning-artifacts/epics.md — Story 3.6 ACs, FR14]
- [Source: _bmad-output/planning-artifacts/architecture.md — Calculator pure function pattern, module boundaries]
- [Source: _bmad-output/planning-artifacts/prd.md — FR14: Top SKU Calculator requirements]
- [Source: _bmad-output/implementation-artifacts/3-5-discount-check-calculator.md — Calculator implementation patterns, service layer, test patterns]
- [Source: backend/app/calculators/discount.py — Pure function pattern, _clean_price helper, _safe_num helper, result dataclass]
- [Source: backend/app/modules/evaluations/calculator_service.py — Service layer pattern, _extract_parsed_data helper, _validate_columns helper]
- [Source: backend/app/modules/evaluations/router.py — API endpoint pattern for calculators]
- [Source: backend/app/modules/evaluations/schemas.py — CalculatorResultResponse schema (reuse)]
- [Source: backend/app/modules/upload/parser.py — REQUIRED_COLUMNS["order_export"] and REQUIRED_COLUMNS["mass_update"]]
- [Source: backend/app/db/queries/calculator_results.py — upsert_result, get_result_by_type queries]
- [Source: frontend/src/hooks/useCalculator.ts — Frontend hook pattern, CalculatorType union, CALCULATOR_PATHS]
- [Source: frontend/src/services/apiClient.ts — API path type definitions]
- [Source: _bmad-output/lessons-learned.md — Code review patterns, testing patterns]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

No debug issues encountered. All tests passed on first run.

### Completion Notes List

- **Task 1+3**: Implemented `calculate_top_sku()` pure function with full processing pipeline (11 subfunctions) and 47 unit tests covering all ACs. Revenue formula correctly handles price cleaning, order-level discount splitting by `Jumlah Produk di Pesan`, and Shopee discount added back. Ranking uses `MAX(ROUND(20%), 20)` with minimum 20 floor. Mass update enrichment provides kode_variasi, stok, and rata2_harga_jual (max single-line revenue).
- **Task 2+4**: Added `run_top_sku_calculator()` service function loading both order_export and mass_update, validating columns for each (`order_export_top_sku` and `mass_update` column sets), calling pure calculator, and upserting to `calculator_results`. Router endpoint at `POST /api/v1/evaluations/brands/{brand_id}/calculators/top_sku`. 6 integration tests covering success, missing files, missing columns, upsert, and auth.
- **Task 5**: Added `TopSkuDetails` interface, `'top_sku'` to `CalculatorType` union and `CALCULATOR_PATHS`, and top_sku endpoint path type in `apiClient.ts`. TypeScript compiles cleanly.
- **Regression**: Full test suite passes (321 tests, 0 failures).

### File List

New files:
- `backend/app/calculators/top_sku.py`
- `backend/tests/unit/calculators/test_top_sku.py`

Modified files:
- `backend/app/modules/evaluations/calculator_service.py`
- `backend/app/modules/evaluations/router.py`
- `backend/tests/integration/api/test_calculators.py`
- `frontend/src/hooks/useCalculator.ts`
- `frontend/src/services/apiClient.ts`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/3-6-top-sku-calculator.md`

## Change Log

- 2026-02-11: Implemented Story 3.6 — Top SKU Calculator with full processing pipeline, API endpoint, 47 unit tests, 6 integration tests, and frontend type additions. All 321 tests pass.
