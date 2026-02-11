# Story 3.5: Discount Check Calculator

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system**,
I want **to execute the Discount Check Calculator on uploaded Order Export data**,
so that **the BD team gets the discount analysis as part of the brand evaluation**.

## Acceptance Criteria

1. **Urutan calculation and price cleaning**
   **Given** a brand has uploaded Order Export Excel (`order_export` in `brand_uploads`)
   **When** the calculator is executed
   **Then** process the parsed order data as follows:

   **Urutan (item position within order):**
   - Compare each row's `No. Pesanan` with the previous row
   - Same order number as previous row → increment position counter
   - Different order number → reset to 1
   - Empty order number → skip row

   **Price cleaning:**
   - Remove `.` thousands separator from `Harga Awal` and `Harga Setelah Diskon`
   - Convert cleaned strings to numbers

   **Voucher/Paket allocation (Urutan=1 only):**
   - `Voucher Ditanggung Penjual`: apply full value only when Urutan = 1 (first line item per order), else 0
   - `Paket Diskon`: apply full value only when Urutan = 1, else 0
   - Remove `.` separator before converting these values to numbers

2. **Discount calculations per line item**
   **Given** cleaned prices and allocated voucher/paket values
   **When** computing per-line discount metrics
   **Then** calculate:

   **Total Discount (N):**
   `N = (Harga Awal - Harga Setelah Diskon) + Voucher(if Urutan=1) + Paket(if Urutan=1)`

   **Discount Percentage (O):**
   `O = N / Harga Awal`

   **Total Paid (P):**
   `P = Harga Setelah Diskon - Voucher(if Urutan=1) - Paket(if Urutan=1)`

3. **Product summary and TOP SKU filter**
   **Given** per-line discount calculations are complete
   **When** aggregating by product
   **Then** produce:

   **Product Summary:**
   - Group by `Nama Produk` (exact match, NOT including variant)
   - Per product: total quantity sold (SUM of `Jumlah`), average discount % (AVERAGE of column O values)

   **TOP SKU Filter:**
   - Filter products where: `Qty > AVERAGE(all product Qty)` AND `AvgDisc < 1.0` (100%)
   - Order by Qty descending
   - Limit = `ROUND(unique_products * 20%)` — NO minimum floor (differs from Calculator 2's `MAX(ROUND(20%), 20)`)

4. **5 output values**
   **Given** TOP SKU filter and per-line calculations are complete
   **When** generating output
   **Then** produce exactly 5 values:

   **Output 1 — % Diskon TOP SKU:**
   `SUMIF(P > 0, N) / SUM(P)` across ALL order lines (not just TOP SKU)
   Formatted as: `"% Diskon TOP SKU: X.X%"` (one decimal place, e.g., "2.7%")

   **Output 2 — Range:**
   `ROUNDUP(MIN(top_sku_avg_disc), 3) ~ ROUNDUP(MAX(top_sku_avg_disc), 3)`
   Formatted as: `"Range: X.X% ~ Y.Y%"` (one decimal place after ROUNDUP to 3 decimals, e.g., "0.0% ~ 6.7%")

   **Output 3 — Voucher Percentage:**
   `SUM(voucher_values) / SUM(harga_setelah_diskon)` across ALL lines
   Formatted as: `"Voucher X.X%"` (one decimal place, e.g., "Voucher 0.3%")

   **Output 4 — Paket Diskon Percentage:**
   `SUM(paket_values) / SUM(harga_setelah_diskon)` across ALL lines
   Formatted as: `"Paket Diskon X.X%"` (one decimal place, e.g., "Paket Diskon 0.0%")

   **Output 5 — Fake Discount Flag:**
   If `SUM(N) / SUM(P) > 20%` → `"📌 Berpotensi menggunakan 'fake discount'"`
   Otherwise → empty string (no flag)

5. **Combined output text**
   **Given** all 5 output values are computed
   **When** assembling the output
   **Then** combine as newline-separated text:
   ```
   % Diskon TOP SKU: 2.7%
   Range: 0.0% ~ 6.7%
   Voucher 0.3%
   Paket Diskon 0.0%
   ```
   **And** if fake discount flag is triggered, append:
   ```
   📌 Berpotensi menggunakan 'fake discount'
   ```

6. **Calculator API endpoint**
   **Given** I am authenticated
   **When** I call `POST /api/v1/evaluations/brands/{brand_id}/calculators/discount`
   **Then** the system loads `order_export` parsed data from `brand_uploads`
   **And** executes the Discount Check Calculator
   **And** stores results in `calculator_results` table (upsert on brand_id + calculator_type)
   **And** returns the calculator output:
   ```json
   {
     "calculator_type": "discount",
     "output_text": "% Diskon TOP SKU: 2.7%\nRange: 0.0% ~ 6.7%\nVoucher 0.3%\nPaket Diskon 0.0%",
     "details": {
       "discount_pct": "2.7%",
       "range_min": "0.0%",
       "range_max": "6.7%",
       "voucher_pct": "0.3%",
       "paket_pct": "0.0%",
       "fake_discount_flag": false,
       "product_summary": [
         {"product_name": "...", "qty": 10, "avg_discount_pct": 0.027}
       ],
       "top_sku": [
         {"product_name": "...", "qty": 10, "avg_discount_pct": 0.027}
       ],
       "totals": {
         "sum_n": 1234567,
         "sum_p": 45678901,
         "sum_voucher": 12345,
         "sum_paket": 0,
         "sum_harga_setelah_diskon": 45691246
       }
     },
     "calculated_at": "2026-02-11T10:30:00Z"
   }
   ```

7. **Error handling for missing data**
   **Given** the calculator is triggered for a brand
   **When** `order_export` has not been uploaded
   **Then** return error with code `CALC_MISSING_DATA` and detail: "Order Export (order_export) has not been uploaded for this brand"

   **Given** the uploaded data has missing required columns
   **When** column validation fails
   **Then** return error with code `CALC_MISSING_DATA` and detail specifying which columns are missing

8. **Test fixtures match spec**
   **Given** SUKA Nov 2025 sample data
   **When** the calculator runs
   **Then** output matches: `"% Diskon TOP SKU: 2.7%\nRange: 0.0% ~ 6.7%\nVoucher 0.3%\nPaket Diskon 0.0%"`
   **And** no fake discount flag (2.7% < 20%)

   **Given** KYPSO Oct 2025 sample data
   **When** the calculator runs
   **Then** output matches: `"% Diskon TOP SKU: 217.3%\nRange: 56.1% ~ 73.1%\nVoucher 0.1%\nPaket Diskon 0.0%\n📌 Berpotensi menggunakan 'fake discount'"`
   **And** fake discount flag triggered (217.3% > 20%)

   **Given** MND Nov 2025 sample data
   **When** the calculator runs
   **Then** output matches: `"% Diskon TOP SKU: 102.9%\nRange: 42.2% ~ 50.4%\nVoucher 3.9%\nPaket Diskon 0.2%\n📌 Berpotensi menggunakan 'fake discount'"`

## Tasks / Subtasks

- [x] Task 1: Implement discount calculator pure function (AC: #1, #2, #3, #4, #5)
  - [x] 1.1 Create `backend/app/calculators/discount.py` with result dataclass `DiscountResult`
  - [x] 1.2 Implement `_safe_num()` helper (reuse pattern from ads_keyword.py or import from shared utils)
  - [x] 1.3 Implement `_clean_price(value)`: remove `.` thousands separator, convert to float
  - [x] 1.4 Implement `_calculate_urutan(rows)`: compute item position within each order
  - [x] 1.5 Implement `_calculate_line_items(rows)`: compute N (total discount), O (discount %), P (total paid) per line
  - [x] 1.6 Implement `_build_product_summary(line_items)`: group by Nama Produk, aggregate qty and avg discount %
  - [x] 1.7 Implement `_filter_top_sku(product_summary)`: apply qty > avg AND avg_disc < 1.0, limit ROUND(unique * 20%)
  - [x] 1.8 Implement `_format_output(totals, top_sku_stats)`: generate 5 output values as formatted text
  - [x] 1.9 Implement main entry `calculate_discount(order_data)` → `DiscountResult`

- [x] Task 2: Create API endpoint and service layer (AC: #6, #7)
  - [x] 2.1 Add `run_discount_calculator(brand_id, user_id)` to `calculator_service.py`:
    - Load `order_export` parsed_data from `brand_uploads`
    - Validate data present (raise CALC_MISSING_DATA if not)
    - Call pure calculator function
    - Upsert result to `calculator_results` table
    - Return result
  - [x] 2.2 Add endpoint to `router.py`:
    - `POST /api/v1/evaluations/brands/{brand_id}/calculators/discount`
    - Response schema: existing `CalculatorResultResponse`
  - [x] 2.3 Import and wire up in `router.py`

- [x] Task 3: Write backend unit tests for calculator (AC: #1, #2, #3, #4, #5, #8)
  - [x] 3.1 Create `backend/tests/unit/calculators/test_discount.py`:
    - Test `_clean_price` helper: handles dots, empty strings, non-numeric
    - Test `_calculate_urutan`: same order increments, different order resets, empty skips
    - Test per-line discount calculation: N, O, P formulas
    - Test voucher/paket allocation: only applied at Urutan=1
    - Test product summary: groups by Nama Produk (exact match, not variant)
    - Test TOP SKU filter: qty > avg AND disc < 1.0, correct limit formula
    - Test output 1: `% Diskon TOP SKU` formula across ALL lines
    - Test output 2: Range with ROUNDUP to 3 decimal places
    - Test output 3: Voucher % (denominator is Harga Setelah Diskon)
    - Test output 4: Paket Diskon %
    - Test output 5: Fake discount flag threshold at 20%
    - Test SUKA sample: 2.7%, Range 0.0%~6.7%, no flag
    - Test KYPSO sample: 217.3%, flag triggered
    - Test MND sample: 102.9%, flag triggered
    - Test edge cases: single order, all same product, zero prices, empty data

- [x] Task 4: Write backend integration tests (AC: #6, #7)
  - [x] 4.1 Add discount tests to `backend/tests/integration/api/test_calculators.py`:
    - Test POST endpoint returns calculator result when order_export present
    - Test 400 error when order_export missing
    - Test 400 error when required columns missing (AC #7)
    - Test upsert: running calculator twice updates existing result
    - Test authentication required

- [x] Task 5: Add frontend hook for discount calculator (AC: #6)
  - [x] 5.1 Update `frontend/src/hooks/useCalculator.ts`:
    - Add `DiscountDetails` type matching the details structure
    - Ensure `useRunCalculator` hook works for `calculatorType: "discount"` (should work generically already)
    - Add `DiscountDetails` to the union type if calculator-specific typing exists

## Dev Notes

### This Is Primarily a Backend Story

Like Story 3.4, the core work is implementing the calculator pure function and its API. The frontend gets a minimal type addition. The full calculator results **display** is Story 3.8.

### Authoritative Calculator Specification

**CRITICAL**: The calculator logic MUST exactly match `logic/calculator-3-discount-checkup.md`. This is the single source of truth. Key sample outputs:
- SUKA: "% Diskon TOP SKU: 2.7%, Range: 0.0% ~ 6.7%, Voucher 0.3%, Paket Diskon 0.0%" (no flag)
- KYPSO: "% Diskon TOP SKU: 217.3%, Range: 56.1% ~ 73.1%, Voucher 0.1%, Paket Diskon 0.0%" (flag)
- MND: "% Diskon TOP SKU: 102.9%, Range: 42.2% ~ 50.4%, Voucher 3.9%, Paket Diskon 0.2%" (flag)

### Shared Order Export Data

This calculator uses the **same** `order_export` file as Calculator 2 (Top SKU). The order export is already uploaded and parsed by Story 3.2. The key difference:

| Aspect | Calculator 2 (Top SKU) | Calculator 3 (Discount) |
|--------|----------------------|------------------------|
| Ranking | By revenue (omzet) | By quantity (Qty) |
| Grouping | Nama Produk + Variasi | Nama Produk only |
| Voucher handling | Divided by Jumlah Produk di Pesan | Applied only to Urutan=1 |
| TOP SKU limit | MAX(ROUND(20%), 20) | ROUND(20%) — no minimum |
| Purpose | Identify top revenue products | Analyze discount health |

### No Manual Input Dependency

Unlike Calculator 1 (Ads Keyword) which requires `total_products` (AK1) from manual input, the Discount Calculator operates **only on the uploaded Order Export data**. No manual data dependency.

### Parsed Data Structure in brand_uploads

The upload parser stores data as JSONB in `brand_uploads.parsed_data`:
```json
{
  "columns": ["No. Pesanan", "Nama Produk", "Harga Awal", "Harga Setelah Diskon", ...],
  "data": [
    {"No. Pesanan": "240101ABC", "Nama Produk": "...", "Harga Awal": "125.000", ...},
    ...
  ],
  "row_count": 500
}
```

### Columns Used from Order Export

From the parser's `REQUIRED_COLUMNS["order_export"]`:
- `No. Pesanan` — order number (for Urutan grouping)
- `Nama Produk` — product name (for product summary grouping)
- `Harga Awal` — original price (Indonesian format: `.` = thousands)
- `Harga Setelah Diskon` — discounted price (Indonesian format)
- `Jumlah` — quantity per line item
- `Voucher Ditanggung Penjual` — seller voucher (order-level)
- `Paket Diskon` — bundle discount from seller

**Note**: `Nomor Referensi SKU`, `Nama Variasi`, `Jumlah Produk di Pesan`, `Cashback Koin`, `Diskon Dari Shopee` — these are needed by Calculator 2 (Top SKU) but NOT used by Calculator 3 (Discount).

### Price Format Handling — Critical

Indonesian price format uses `.` as thousands separator:
- `"125.000"` → 125000
- `"1.250.000"` → 1250000
- `"0"` → 0
- `""` or missing → 0

The `_clean_price()` helper must strip dots then convert to number. This is straightforward string replacement.

### Urutan Logic — Critical

The Urutan (item position) determines whether voucher/paket discounts are applied:
- Orders can have multiple line items (different products in the same order)
- Voucher and Paket Diskon are **order-level** discounts, not per-item
- To prevent double-counting, only apply these to the FIRST line item (Urutan=1)
- **Rows must be processed in the order they appear** in the data (rows for the same order are consecutive)

### Output Formulas — MUST Match Spec Exactly

| Output | Formula | Denominator Notes |
|--------|---------|-------------------|
| % Diskon TOP SKU | `SUMIF(P>0, N) / SUM(P)` | Uses ALL lines, only P>0 for N numerator |
| Voucher % | `SUM(voucher) / SUM(harga_setelah_diskon)` | Denominator is K (after discount), NOT J (original) |
| Paket Diskon % | `SUM(paket) / SUM(harga_setelah_diskon)` | Same denominator as Voucher |
| Fake Discount | `SUM(N) / SUM(P) > 20%` | ALL N values, ALL P values |

### ROUNDUP for Range Values

The Range output uses `ROUNDUP(value, 3)` — rounds UP to 3 decimal places, then formats as percentage with 1 decimal place. Example: if raw avg_disc = 0.06698, ROUNDUP(0.06698, 3) = 0.067, formatted as "6.7%".

Python's `math.ceil` works on integers — for decimal places, use: `math.ceil(value * 1000) / 1000`

### How Output Feeds into Scoring System

The full text output goes into **cell D73** of the scoring system template. The scoring system then:
- **H73**: If D73 contains "Berpotensi menggunakan 'fake discount'" → score 0, else score 5
- **G68**: Parses D73 using REGEXEXTRACT to calculate marketing cost estimation
- **G72/G73**: Uses parsed D73 values for recommended marketing budget

This means the output text format is **critical** — the scoring system relies on exact text patterns.

### Project Structure Notes

**New files to create:**

```
backend/app/calculators/discount.py
backend/tests/unit/calculators/test_discount.py
backend/tests/integration/api/test_discount_calculator.py
```

**Existing files to modify:**

```
backend/app/modules/evaluations/calculator_service.py  ← ADD run_discount_calculator
backend/app/modules/evaluations/router.py              ← ADD discount calculator endpoint
frontend/src/hooks/useCalculator.ts                    ← ADD DiscountDetails type
```

### Architecture Compliance

**Backend Pattern (MUST follow):**
- Calculator in `calculators/discount.py` — PURE function, no I/O, no database access
- Service orchestration in `modules/evaluations/calculator_service.py` — handles all I/O
- Router endpoint in `modules/evaluations/router.py` — REST convention
- Database queries reuse existing `db/queries/calculator_results.py` (`upsert_result`, `get_result_by_type`)
- Exception chaining: always `raise ... from e`
- Structured error codes: `CALC_MISSING_DATA`, `CALC_EXECUTION_FAILED`

**Calculator Architecture (MUST follow):**
```python
# calculators/discount.py — PURE, no database access
def calculate_discount(
    order_data: list[dict],  # parsed rows from order_export
) -> DiscountResult:
    ...
```

The service layer (`calculator_service.py`) handles all I/O:
- Load parsed data from `brand_uploads`
- Call pure calculator
- Store results in `calculator_results`

**Database Pattern (MUST follow):**
- Reuse existing `calculator_results` table (created in Story 3.4, migration 008)
- calculator_type = `"discount"`
- UNIQUE(brand_id, calculator_type) enables upsert

**Testing Pattern (MUST follow):**
- Unit tests: `backend/tests/unit/calculators/test_discount.py`
- Integration tests: `backend/tests/integration/api/test_discount_calculator.py`
- Run: `cd backend && uv run python -m pytest -v`

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| polars | existing | Not strictly needed — can work with list[dict] directly | Installed |
| asyncpg | existing | Database queries (calculator_results) | Installed |
| fastapi | existing | API endpoint | Installed |
| pydantic | existing | Response schemas (reuse CalculatorResultResponse) | Installed |
| pytest | existing | Unit + integration tests | Installed |

**No new dependencies needed.** All required libraries are already installed.

### Testing Requirements

**Backend Unit Tests (pytest):**

```
backend/tests/unit/calculators/test_discount.py:
  - test_clean_price_removes_dots
  - test_clean_price_empty_string
  - test_clean_price_zero
  - test_clean_price_no_dots
  - test_urutan_same_order_increments
  - test_urutan_different_order_resets
  - test_urutan_empty_order_skips
  - test_line_item_total_discount_formula
  - test_line_item_discount_percentage
  - test_line_item_total_paid
  - test_voucher_applied_only_urutan_1
  - test_paket_applied_only_urutan_1
  - test_product_summary_groups_by_name_only
  - test_product_summary_qty_and_avg_discount
  - test_top_sku_filter_qty_above_average
  - test_top_sku_filter_excludes_100pct_discount
  - test_top_sku_limit_formula
  - test_output_discount_pct_uses_all_lines
  - test_output_range_roundup_3_decimals
  - test_output_voucher_pct_denominator_is_after_discount
  - test_output_paket_pct
  - test_output_fake_discount_above_20pct
  - test_output_fake_discount_below_20pct
  - test_suka_sample_output
  - test_kypso_sample_output
  - test_mnd_sample_output
  - test_empty_data_handling
  - test_single_order_single_item
  - test_all_zero_prices
```

**Backend Integration Tests (pytest):**

```
backend/tests/integration/api/test_discount_calculator.py:
  - test_run_discount_calculator_success
  - test_run_discount_missing_order_export
  - test_run_discount_upsert_on_recalculation
  - test_run_discount_auth_required
```

### Previous Story Intelligence

**From Story 3.4 (Ads Keyword Calculator):**
- Pure function pattern works well: `calculate_ads_keyword(data, data, int) → Result`
- Service layer pattern: load from brand_uploads, validate, call calculator, upsert result
- `_extract_parsed_data()` helper validates parsed_data structure — reuse this
- `CalculatorResultResponse` schema already exists — reuse it directly
- `calculator_results` table already exists with UNIQUE(brand_id, calculator_type) — no migration needed
- Integration test pattern: create brand, create upload, run calculator, verify result
- Code review found: missing error wrapping (H1), missing parsed_data validation (H2) — discount calculator must include both from the start

**From Code Reviews:**
- Exception chaining: always `raise ... from e`
- Response schemas must match ACs field-by-field
- File List must include ALL changed files
- Wrap calculator execution in try/except for CALC_EXECUTION_FAILED

### Git Intelligence

Recent commits show Story 3.4 merged to develop:
```
0791fcc Merge feature/3-4-ads-keyword-calculator into develop
e759fb4 Mark Story 3.4 done after code review — all issues resolved
3312646 Fix 9 code review issues for Story 3.4 (3H/3M/3L)
```

**Patterns to follow:**
- Feature branch naming: `feature/3-5-discount-check-calculator`
- Atomic commits per task
- Tests committed alongside implementation

### References

- [Source: logic/calculator-3-discount-checkup.md — Complete calculator specification with 4 sample outputs]
- [Source: _bmad-output/planning-artifacts/epics.md — Story 3.5 ACs, FR13]
- [Source: _bmad-output/planning-artifacts/architecture.md — Calculator pure function pattern, module boundaries]
- [Source: _bmad-output/planning-artifacts/prd.md — FR13: Discount Check Calculator requirements]
- [Source: _bmad-output/implementation-artifacts/3-4-ads-keyword-calculator.md — Calculator implementation patterns, service layer, test patterns]
- [Source: backend/app/calculators/ads_keyword.py — Pure function pattern, helper utilities, result dataclass]
- [Source: backend/app/modules/evaluations/calculator_service.py — Service layer pattern, _extract_parsed_data helper]
- [Source: backend/app/modules/upload/parser.py — REQUIRED_COLUMNS["order_export"], parsed_data structure]
- [Source: backend/app/db/queries/calculator_results.py — upsert_result, get_result_by_type queries]
- [Source: _bmad-output/lessons-learned.md — Code review patterns, testing patterns]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

No blocking issues encountered during implementation.

### Completion Notes List

- **Task 1**: Implemented `backend/app/calculators/discount.py` with `DiscountResult` dataclass and all helper functions: `_clean_price`, `_calculate_urutan`, `_calculate_line_items`, `_build_product_summary`, `_filter_top_sku`, `_roundup`, `_format_output`, and main entry `calculate_discount()`. All formulas match the spec exactly (N/O/P calculations, ROUNDUP for range, SUMIF(P>0,N)/SUM(P) for discount %, fake discount threshold >20%).
- **Task 2**: Added `run_discount_calculator()` to `calculator_service.py` following the same I/O orchestration pattern as ads_keyword: validate brand, load order_export, extract parsed_data, call pure function, upsert result. Exception chaining with `raise ... from e`.
- **Task 2**: Added `POST /api/v1/evaluations/brands/{brand_id}/calculators/discount` endpoint to `router.py`.
- **Task 3**: Created 56 unit tests covering all helpers, formulas, sample data (SUKA/KYPSO/MND patterns), and edge cases. All pass.
- **Task 4**: Added 4 integration tests: auth required, success, missing data, upsert. All pass.
- **Task 5**: Added `DiscountDetails` interface to `useCalculator.ts`, updated `useRunCalculator` to accept `'discount'` calculator type, added discount endpoint to API client types.

### Change Log

- 2026-02-11: Story 3.5 implementation complete — discount calculator pure function, API endpoint, service layer, 60 tests (56 unit + 4 integration), frontend type additions.
- 2026-02-11: Code review fixes — added column validation (H1), exact MND value assertions (M1), _safe_num tests (M2), unused param docs (L1), task description fix (L3). Tests: 69 unit + 11 integration = 80 total.

### File List

**New files:**
- `backend/app/calculators/discount.py` — Discount Check Calculator pure function
- `backend/tests/unit/calculators/test_discount.py` — 56 unit tests for calculator

**Modified files:**
- `backend/app/modules/evaluations/calculator_service.py` — Added `run_discount_calculator()` service function
- `backend/app/modules/evaluations/router.py` — Added POST discount calculator endpoint
- `backend/tests/integration/api/test_calculators.py` — Added 4 discount calculator integration tests
- `frontend/src/hooks/useCalculator.ts` — Added `DiscountDetails` type, updated hook for discount support
- `frontend/src/services/apiClient.ts` — Added discount calculator endpoint path type
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Updated story status
