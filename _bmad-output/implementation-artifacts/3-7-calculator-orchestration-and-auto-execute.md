# Story 3.7: Calculator Orchestration and Auto-Execute

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system**,
I want **to automatically run applicable calculators when their required input files become available after upload**,
so that **the BD team sees calculator results as soon as possible without manually triggering each calculator**.

## Acceptance Criteria

1. **Auto-execute after file upload**
   **Given** a brand file upload completes successfully (via `POST /api/v1/upload/process`)
   **When** the upload is processed and stored in `brand_uploads`
   **Then** check which calculators now have ALL their required files:
   - **Calculator 1 (Ads Keyword)**: needs `cpc_ad_report` + `keyword_report` + manual `total_products` (AK1)
   - **Calculator 2 (Top SKU)**: needs `order_export` + `mass_update`
   - **Calculator 3 (Discount Check)**: needs `order_export`
   **And** run only the calculators whose requirements are fully satisfied
   **And** store results in `calculator_results` table (upsert per brand_id + calculator_type)

2. **Order Export triggers Discount Check immediately**
   **Given** an `order_export` file is uploaded
   **When** checking calculator readiness
   **Then** run Calculator 3 (Discount Check) immediately (only needs order_export)
   **And** if `mass_update` is also already uploaded → also run Calculator 2 (Top SKU)
   **And** if `mass_update` is NOT yet uploaded → Calculator 2 status remains "pending"

3. **Mass Update triggers Top SKU when Order Export exists**
   **Given** a `mass_update` file is uploaded and `order_export` already exists for this brand
   **When** checking calculator readiness
   **Then** run Calculator 2 (Top SKU)

4. **CPC/Keyword uploads trigger Ads Keyword when pair + manual input complete**
   **Given** a `cpc_ad_report` or `keyword_report` file is uploaded
   **When** checking calculator readiness
   **Then** check if the OTHER required file also exists for this brand
   **And** check if `total_products` (AK1) exists in `evaluation_inputs.manual_data`
   **And** if ALL three are present → run Calculator 1 (Ads Keyword)
   **And** if any missing → Calculator 1 status remains "pending"

5. **Calculator failure isolation**
   **Given** any calculator fails during orchestration
   **When** orchestrating multiple calculators
   **Then** continue with other calculators (don't fail all)
   **And** record which calculators succeeded and which failed
   **And** return partial results with error details for failed ones
   **And** the upload itself is NOT rolled back (file stays in brand_uploads)

6. **File re-upload clears and re-runs**
   **Given** a file is re-uploaded (replacing a previous one for the same file_type)
   **When** the upload succeeds
   **Then** clear calculator results that depend on that file type:
   - Re-upload `order_export` → clear `discount` AND `top_sku` results
   - Re-upload `mass_update` → clear `top_sku` result
   - Re-upload `cpc_ad_report` or `keyword_report` → clear `ads_keyword` result
   **And** re-run applicable calculators with the new data

7. **Manual recalculate endpoint**
   **Given** I am authenticated
   **When** I call `POST /api/v1/evaluations/brands/{brand_id}/calculators/run-all`
   **Then** check all calculator dependencies for this brand
   **And** run all calculators whose required files are available
   **And** return results for each calculator (success or error):
   ```json
   {
     "results": [
       {
         "calculator_type": "discount",
         "status": "success",
         "result": { "calculator_type": "discount", "output_text": "...", "details": {...}, "calculated_at": "..." }
       },
       {
         "calculator_type": "top_sku",
         "status": "success",
         "result": { "calculator_type": "top_sku", "output_text": "", "details": {...}, "calculated_at": "..." }
       },
       {
         "calculator_type": "ads_keyword",
         "status": "skipped",
         "reason": "Missing required files: keyword_report"
       }
     ]
   }
   ```

8. **Calculator status endpoint**
   **Given** I am authenticated
   **When** I call `GET /api/v1/evaluations/brands/{brand_id}/calculators/status`
   **Then** return the readiness status of each calculator:
   ```json
   {
     "brand_id": 123,
     "calculators": {
       "ads_keyword": {
         "status": "pending",
         "has_result": false,
         "required_files": ["cpc_ad_report", "keyword_report"],
         "required_manual": ["total_products"],
         "available_files": ["cpc_ad_report"],
         "missing_files": ["keyword_report"],
         "missing_manual": ["total_products"]
       },
       "discount": {
         "status": "ready",
         "has_result": true,
         "required_files": ["order_export"],
         "available_files": ["order_export"],
         "missing_files": [],
         "calculated_at": "2026-02-11T10:30:00Z"
       },
       "top_sku": {
         "status": "ready",
         "has_result": true,
         "required_files": ["order_export", "mass_update"],
         "available_files": ["order_export", "mass_update"],
         "missing_files": [],
         "calculated_at": "2026-02-11T10:31:00Z"
       }
     }
   }
   ```

9. **Upload process response includes calculator results**
   **Given** auto-execute runs after a file upload
   **When** the `POST /api/v1/upload/process` response is returned
   **Then** include auto-executed calculator results in the response:
   ```json
   {
     "upload": {
       "id": 1,
       "brand_id": 123,
       "file_type": "order_export",
       "filename": "Order_all_nov.xlsx",
       "file_size": 524288,
       "row_count": 500,
       "uploaded_at": "2026-02-11T10:30:00Z"
     },
     "auto_calculated": [
       {
         "calculator_type": "discount",
         "status": "success",
         "result": { "calculator_type": "discount", "output_text": "...", "details": {...}, "calculated_at": "..." }
       },
       {
         "calculator_type": "top_sku",
         "status": "skipped",
         "reason": "Missing required files: mass_update"
       }
     ]
   }
   ```

10. **Frontend reflects auto-calculation state**
    **Given** an upload completes and auto-calculation runs
    **When** the frontend receives the upload response with `auto_calculated` results
    **Then** invalidate the relevant TanStack Query caches (calculator results, calculator status)
    **And** the calculator results display updates automatically without manual refresh

## Tasks / Subtasks

- [x] Task 1: Implement calculator orchestration engine (AC: #1, #2, #3, #4, #5, #6)
  - [x] 1.1 Create calculator dependency mapping in `calculators/engine.py`:
    - File-type → calculator mapping (which calculators each file feeds)
    - Calculator → required files mapping (what each calculator needs)
    - Calculator → required manual inputs mapping (for ads_keyword)
  - [x] 1.2 Implement `check_calculator_readiness(brand_id, conn)` → dict of calculator statuses:
    - Load all `brand_uploads` for the brand (file_type presence check)
    - Load `evaluation_inputs` for manual data check (total_products for ads_keyword)
    - Compare against dependency map
    - Return per-calculator status: ready/pending/has_result with missing items
  - [x] 1.3 Implement `run_ready_calculators(brand_id, user_id, conn)` → list of results:
    - Call `check_calculator_readiness()`
    - For each ready calculator, call existing `run_*_calculator()` from calculator_service.py
    - Wrap each in try/except for failure isolation (AC #5)
    - Return list of `{calculator_type, status, result/reason}`
  - [x] 1.4 Implement `run_calculators_for_upload(brand_id, file_type, user_id, conn)` → list:
    - Determine which calculators the uploaded file_type feeds (from dependency map)
    - Only check/run those specific calculators (not all)
    - Used by upload process for targeted auto-execute
  - [x] 1.5 Implement `clear_dependent_results(brand_id, file_type, conn)`:
    - Map file_type to affected calculator_types
    - Delete from `calculator_results` where brand_id + calculator_type matches
    - Used before re-running after file re-upload (AC #6)

- [x] Task 2: Integrate auto-execute into upload pipeline (AC: #1, #6, #9)
  - [x] 2.1 Modify `upload/service.py` `process_upload()`:
    - After successful upsert_upload, call `clear_dependent_results()` for the file_type
    - Then call `run_calculators_for_upload()` with the brand_id and file_type
    - Capture results (success/skip/error per calculator)
    - Return enhanced response including `auto_calculated` list
  - [x] 2.2 Update `upload/schemas.py`:
    - Add `AutoCalculatedResult` schema: calculator_type, status, result (optional), reason (optional)
    - Update `ProcessResponse` (or create new) to include `upload` + `auto_calculated` list
  - [x] 2.3 Update `upload/router.py` process endpoint:
    - Pass user_id to process_upload for calculator execution context
    - Return enhanced response with auto_calculated results

- [x] Task 3: Add run-all and status endpoints (AC: #7, #8)
  - [x] 3.1 Add `POST /api/v1/evaluations/brands/{brand_id}/calculators/run-all` endpoint:
    - Call `run_ready_calculators()` from engine
    - Return list of per-calculator results
  - [x] 3.2 Add `GET /api/v1/evaluations/brands/{brand_id}/calculators/status` endpoint:
    - Call `check_calculator_readiness()` from engine
    - Return structured status per calculator
  - [x] 3.3 Add response schemas:
    - `CalculatorStatusResponse` — per-calculator readiness status
    - `RunAllResponse` — list of per-calculator execution results
  - [x] 3.4 Wire up endpoints in evaluations/router.py

- [x] Task 4: Add DB query for clearing calculator results (AC: #6)
  - [x] 4.1 Add `delete_results_by_types(conn, brand_id, calculator_types: list[str])` to `db/queries/calculator_results.py`:
    - DELETE FROM calculator_results WHERE brand_id = $1 AND calculator_type = ANY($2)
    - Return count of deleted rows
  - [x] 4.2 Add `get_uploads_for_brand(conn, brand_id)` to `db/queries/uploads.py` if not exists:
    - SELECT file_type FROM brand_uploads WHERE brand_id = $1
    - Return list of available file_types

- [x] Task 5: Write backend unit tests for orchestration engine (AC: #1-#6)
  - [x] 5.1 Create `backend/tests/unit/calculators/test_engine.py`:
    - Test dependency mapping correctness (file→calculator, calculator→files)
    - Test `check_calculator_readiness`: all files present → ready
    - Test `check_calculator_readiness`: missing file → pending with missing list
    - Test `check_calculator_readiness`: ads_keyword missing manual input → pending
    - Test `check_calculator_readiness`: has_result reflects existing calculator_results
    - Test `run_ready_calculators`: runs only ready calculators
    - Test `run_ready_calculators`: failure isolation (one fails, others continue)
    - Test `run_calculators_for_upload`: order_export triggers discount + checks top_sku
    - Test `run_calculators_for_upload`: mass_update triggers only top_sku check
    - Test `run_calculators_for_upload`: cpc_ad_report triggers only ads_keyword check
    - Test `clear_dependent_results`: order_export clears discount + top_sku
    - Test `clear_dependent_results`: mass_update clears only top_sku
    - Test `clear_dependent_results`: cpc_ad_report clears only ads_keyword

- [x] Task 6: Write backend integration tests (AC: #7, #8, #9)
  - [x] 6.1 Add orchestration integration tests to `backend/tests/integration/api/`:
    - Test POST run-all returns results for ready calculators
    - Test POST run-all skips calculators with missing files
    - Test POST run-all isolates failures
    - Test GET status returns correct readiness per calculator
    - Test GET status reflects existing results (has_result + calculated_at)
    - Test upload process response includes auto_calculated results
    - Test file re-upload clears old results and re-runs
    - Test authentication required on all new endpoints

- [x] Task 7: Update frontend hooks for orchestration (AC: #10)
  - [x] 7.1 Update `frontend/src/hooks/useCalculator.ts`:
    - Add `useCalculatorStatus(brandId)` hook — GET status endpoint
    - Add `useRunAllCalculators(brandId)` hook — POST run-all mutation
    - Add `CalculatorStatus` type and `RunAllResponse` type
  - [x] 7.2 Update `frontend/src/hooks/useUpload.ts`:
    - Update `useProcessUpload` to handle enhanced response with `auto_calculated`
    - On upload success with auto_calculated results, invalidate calculator query caches
  - [x] 7.3 Update `frontend/src/services/apiClient.ts`:
    - Add path types for run-all and status endpoints

## Dev Notes

### This Story Connects Existing Pieces

Unlike Stories 3.4-3.6 which implemented individual calculators, this story is about **orchestration** — connecting the upload pipeline to the calculator execution pipeline. The three calculator pure functions already exist and work. The service layer functions (`run_ads_keyword_calculator`, `run_discount_calculator`, `run_top_sku_calculator`) already handle data loading, validation, execution, and storage. This story adds the "glue" layer that decides WHEN to call them.

### Engine Architecture

The orchestration logic goes in `calculators/engine.py` (file exists but is empty — just a docstring). This is the right place per architecture.md: "Calculator orchestration in `calculators/engine.py`".

**Key Design Decision:** The engine should NOT duplicate the data-loading and validation logic already in `calculator_service.py`. Instead, it should:
1. Check readiness (what files/inputs exist)
2. Decide which calculators to run
3. Call the existing `run_*_calculator()` functions from `calculator_service.py`
4. Handle failure isolation and result aggregation

```
engine.py (orchestration decisions)
    ↓ calls
calculator_service.py (existing per-calculator functions with I/O)
    ↓ calls
calculators/*.py (existing pure functions)
```

### Calculator Dependency Map — Critical Reference

| Calculator | Required Files | Required Manual Input | Triggered By Upload Of |
|-----------|---------------|----------------------|----------------------|
| ads_keyword | `cpc_ad_report` + `keyword_report` | `total_products` (AK1) from manual_data | `cpc_ad_report` OR `keyword_report` |
| discount | `order_export` | None | `order_export` |
| top_sku | `order_export` + `mass_update` | None | `order_export` OR `mass_update` |

**File Type → Affected Calculators (for auto-execute):**

| File Type | Calculators to Check |
|-----------|---------------------|
| `cpc_ad_report` | `ads_keyword` |
| `keyword_report` | `ads_keyword` |
| `order_export` | `discount`, `top_sku` |
| `mass_update` | `top_sku` |

**File Type → Calculators to Clear on Re-upload:**

| File Type | Clear Results For |
|-----------|------------------|
| `cpc_ad_report` | `ads_keyword` |
| `keyword_report` | `ads_keyword` |
| `order_export` | `discount`, `top_sku` |
| `mass_update` | `top_sku` |

### Upload Service Integration Point

The current `process_upload()` in `upload/service.py` follows this flow:
```
Download from GCS → Parse → Validate columns → Upsert to brand_uploads → Delete from GCS
```

After this story, it becomes:
```
Download from GCS → Parse → Validate columns → Upsert to brand_uploads → Delete from GCS
    → Clear dependent calculator results
    → Run applicable calculators (auto-execute)
    → Return upload + auto_calculated results
```

The `process_upload()` function already receives `brand_id` and `file_type`. It needs to additionally receive `user_id` (for calculator execution context — needed by `run_*_calculator()` functions).

### Existing Calculator Service Functions

Each already handles its complete flow:

```python
# calculator_service.py — already implemented
async def run_ads_keyword_calculator(brand_id: int, user_id: int, conn) -> dict
async def run_discount_calculator(brand_id: int, user_id: int, conn) -> dict
async def run_top_sku_calculator(brand_id: int, user_id: int, conn) -> dict
```

Each:
- Validates brand exists
- Loads parsed_data from brand_uploads
- Validates required columns
- Calls the pure calculator function
- Upserts result to calculator_results
- Returns CalculatorResultResponse-compatible dict

The engine.py should call these directly. No need to re-implement data loading.

### Ads Keyword Special Case — Manual Input Dependency

Calculator 1 (Ads Keyword) requires `total_products` from `evaluation_inputs.manual_data`. This is the ONLY calculator with a manual data dependency. The engine must check:

```python
# Check if total_products exists in evaluation_inputs
inputs = await get_evaluation_inputs(conn, brand_id)
if inputs and inputs.get("manual_data", {}).get("total_products"):
    # ads_keyword is ready (if files also present)
```

The existing `run_ads_keyword_calculator()` in calculator_service.py already loads this from evaluation_inputs. The engine just needs to CHECK readiness, not load the actual data.

### Database Queries Needed

**Existing queries (reuse):**
- `db/queries/uploads.py`: `get_uploads_by_brand()` — returns all uploads for a brand
- `db/queries/calculator_results.py`: `upsert_result()`, `get_result_by_type()`
- `db/queries/evaluations.py`: `get_evaluation_inputs()` — for manual data check

**New query needed:**
- `db/queries/calculator_results.py`: `delete_results_by_types(brand_id, types[])` — for clearing dependent results on re-upload

### Response Schema Design

**Enhanced upload process response:**
The current `UploadResponse` returns upload info. The enhanced response wraps it:

```python
class AutoCalculatedItem(BaseModel):
    calculator_type: str
    status: str  # "success", "skipped", "error"
    result: CalculatorResultResponse | None = None  # present when status="success"
    reason: str | None = None  # present when status="skipped" or "error"

class ProcessUploadResponse(BaseModel):
    upload: UploadResponse
    auto_calculated: list[AutoCalculatedItem]
```

**Calculator status response:**
```python
class SingleCalculatorStatus(BaseModel):
    status: str  # "ready", "pending"
    has_result: bool
    required_files: list[str]
    required_manual: list[str] = []
    available_files: list[str]
    missing_files: list[str]
    missing_manual: list[str] = []
    calculated_at: datetime | None = None

class CalculatorStatusResponse(BaseModel):
    brand_id: int
    calculators: dict[str, SingleCalculatorStatus]
```

### Project Structure Notes

**New files to create:**
```
backend/app/calculators/engine.py              ← Orchestration logic (expand existing empty file)
backend/tests/unit/calculators/test_engine.py  ← Unit tests for orchestration
```

**Existing files to modify:**
```
backend/app/modules/upload/service.py          ← Integrate auto-execute after upload
backend/app/modules/upload/schemas.py          ← Enhanced process response
backend/app/modules/upload/router.py           ← Pass user_id, return enhanced response
backend/app/modules/evaluations/router.py      ← Add run-all and status endpoints
backend/app/modules/evaluations/schemas.py     ← Add status and run-all response schemas
backend/app/db/queries/calculator_results.py   ← Add delete_results_by_types query
backend/tests/integration/api/test_calculators.py ← Add orchestration integration tests
frontend/src/hooks/useCalculator.ts            ← Add status and run-all hooks
frontend/src/hooks/useUpload.ts                ← Handle auto_calculated in upload response
frontend/src/services/apiClient.ts             ← Add new endpoint path types
```

### Architecture Compliance

**Backend Pattern (MUST follow):**
- Engine in `calculators/engine.py` — orchestration ONLY, calls existing service functions
- Engine should NOT access database directly — use service functions and DB query helpers
- New endpoints in `modules/evaluations/router.py` — follows REST convention
- Response schemas in `modules/evaluations/schemas.py` — Pydantic models
- Exception chaining: always `raise ... from e`
- Structured error codes: `CALC_MISSING_DATA`, `CALC_EXECUTION_FAILED`
- Calculator isolation: one calculator failure MUST NOT prevent others from running

**Calculator Architecture (MUST follow):**
```
calculators/engine.py (orchestration — decides what to run)
    ↓ calls existing functions
modules/evaluations/calculator_service.py (per-calculator I/O + execution)
    ↓ calls
calculators/*.py (pure functions — unchanged)
```

The engine.py is NOT a pure function — it does I/O through the service layer. This is correct because orchestration inherently requires checking database state.

**Database Pattern (MUST follow):**
- Reuse existing `calculator_results` table — no new migrations
- Reuse existing `brand_uploads` table — no new migrations
- New delete query uses parameterized SQL: `$1, $2` placeholders
- Use `ANY($2::text[])` for array parameter in delete query

**Testing Pattern (MUST follow):**
- Unit tests: `backend/tests/unit/calculators/test_engine.py`
- Integration tests: `backend/tests/integration/api/` (add to existing or new file)
- Run: `cd backend && uv run python -m pytest -v`

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| asyncpg | existing | Database queries | Installed |
| fastapi | existing | API endpoints | Installed |
| pydantic | existing | Response schemas | Installed |
| pytest | existing | Tests | Installed |

**No new dependencies needed.** All required libraries are already installed.

### Testing Requirements

**Backend Unit Tests (pytest):**

```
backend/tests/unit/calculators/test_engine.py:
  - test_file_to_calculator_mapping_completeness
  - test_calculator_to_files_mapping_completeness
  - test_check_readiness_all_files_present_is_ready
  - test_check_readiness_missing_file_is_pending
  - test_check_readiness_ads_keyword_missing_manual_input
  - test_check_readiness_ads_keyword_all_present
  - test_check_readiness_has_result_reflects_existing_results
  - test_run_ready_calculators_runs_only_ready
  - test_run_ready_calculators_skips_pending
  - test_run_ready_calculators_failure_isolation
  - test_run_calculators_for_upload_order_export_triggers_discount
  - test_run_calculators_for_upload_order_export_triggers_top_sku_if_mass_update_exists
  - test_run_calculators_for_upload_mass_update_triggers_top_sku_if_order_export_exists
  - test_run_calculators_for_upload_cpc_triggers_ads_keyword_check
  - test_clear_dependent_results_order_export_clears_discount_and_top_sku
  - test_clear_dependent_results_mass_update_clears_top_sku_only
  - test_clear_dependent_results_cpc_clears_ads_keyword_only
  - test_clear_dependent_results_keyword_clears_ads_keyword_only
```

**Backend Integration Tests (pytest):**

```
backend/tests/integration/api/:
  - test_run_all_returns_ready_calculator_results
  - test_run_all_skips_calculators_missing_files
  - test_run_all_isolates_failures
  - test_calculator_status_correct_readiness
  - test_calculator_status_reflects_existing_results
  - test_upload_process_includes_auto_calculated
  - test_upload_reupload_clears_and_reruns
  - test_run_all_auth_required
  - test_calculator_status_auth_required
```

### Previous Story Intelligence

**From Story 3.6 (Top SKU Calculator):**
- Service layer pattern: `run_top_sku_calculator()` loads from brand_uploads, validates, calls calculator, upserts
- Both `order_export` and `mass_update` must exist — same dual-file pattern needed for readiness check
- Integration test pattern: create brand, create upload, run calculator, verify result
- 324 tests currently pass — maintain full regression

**From Story 3.5 (Discount Check Calculator):**
- Service layer pattern: `run_discount_calculator()` loads order_export, validates, calls calculator, upserts
- `_extract_parsed_data()` and `_validate_columns()` helpers are well-established
- CalculatorResultResponse schema is reusable for individual results

**From Story 3.4 (Ads Keyword Calculator):**
- Service layer pattern: `run_ads_keyword_calculator()` loads TWO files + manual input
- Manual input dependency: loads `total_products` from evaluation_inputs
- This is the most complex dependency — engine must check file + manual data

**From Code Reviews (all stories):**
- Exception chaining: always `raise ... from e`
- Response schemas must match ACs field-by-field
- File List must include ALL changed files
- Wrap calculator execution in try/except for CALC_EXECUTION_FAILED

### Git Intelligence

Recent commits show Story 3.6 merged to develop:
```
ced6039 Merge feature/3-6-top-sku-calculator into develop
84e3321 Mark Story 3.6 done after code review — all issues resolved
1c77dc3 Fix 7 code review issues for Story 3.6 (1H/3M/3L)
```

**Patterns to follow:**
- Feature branch naming: `feature/3-7-calculator-orchestration-and-auto-execute`
- Atomic commits per task
- Tests committed alongside implementation

### How This Feeds into Story 3.8 (Calculator Results Display)

Story 3.8 is the frontend display of calculator results. This orchestration story provides:
- **Calculator status endpoint** — frontend needs to show which calculators are pending/ready/complete
- **Auto-calculated results in upload response** — frontend can update UI immediately after upload
- **Run-all endpoint** — frontend can offer a "Recalculate All" button
- Story 3.8 will consume the data structures defined here

### How This Feeds into Story 3.9 (Final Scoring)

Story 3.9 (Final Scoring) needs all three calculators to have run. The calculator status endpoint from this story will be used to check if scoring prerequisites are met:
- Discount Check result → feeds into scoring D73 (fake discount flag)
- Top SKU average_stock → feeds into scoring D70 (stock score)
- All calculator results must exist before final scoring can run

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.7 — Story 3.7 ACs, FR15, FR18]
- [Source: _bmad-output/planning-artifacts/architecture.md — Calculator orchestration in engine.py, module boundaries]
- [Source: _bmad-output/planning-artifacts/prd.md — FR15: Auto-execute calculators, FR18: Recalculate on data change]
- [Source: _bmad-output/implementation-artifacts/3-6-top-sku-calculator.md — Previous story patterns, service layer, testing]
- [Source: backend/app/calculators/engine.py — Empty file, placeholder for orchestration]
- [Source: backend/app/modules/evaluations/calculator_service.py — Existing run_*_calculator() functions]
- [Source: backend/app/modules/evaluations/router.py — Existing calculator endpoints]
- [Source: backend/app/modules/evaluations/schemas.py — CalculatorResultResponse schema]
- [Source: backend/app/modules/upload/service.py — process_upload() function, integration point]
- [Source: backend/app/modules/upload/router.py — Upload process endpoint]
- [Source: backend/app/modules/upload/schemas.py — UploadResponse, ProcessRequest schemas]
- [Source: backend/app/db/queries/calculator_results.py — upsert_result, get_result_by_type queries]
- [Source: backend/app/db/queries/uploads.py — get_uploads_by_brand query]
- [Source: backend/app/db/queries/evaluations.py — get_evaluation_inputs query]
- [Source: frontend/src/hooks/useCalculator.ts — Calculator hooks and types]
- [Source: frontend/src/hooks/useUpload.ts — Upload hooks, process flow]
- [Source: frontend/src/services/apiClient.ts — API path type definitions]
- [Source: _bmad-output/lessons-learned.md — Code review patterns, testing patterns]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

None — all issues resolved inline.

### Completion Notes List

- All 7 tasks implemented across 16 files (1 new, 15 modified)
- 47 new tests added (38 unit + 9 integration), baseline 324 → 371 total, all pass
- Engine architecture: `calculators/engine.py` orchestrates via existing `run_*_calculator()` service functions — no duplication of data-loading logic
- `get_any_evaluation_inputs()` query added to check manual_data without user_id context (needed for readiness checks)
- Upload process response changed from flat `UploadResponse` to nested `ProcessUploadResponse { upload, auto_calculated }` — existing test `test_process_valid_csv` updated
- Frontend TS compiles clean; 1 pre-existing Firebase auth test failure (environment issue, unrelated)

### File List

**New files:**
- `backend/app/calculators/engine.py` — Calculator orchestration engine (dependency maps, readiness checks with user-specific manual data, auto-execute, clear-dependent)
- `backend/tests/unit/calculators/test_engine.py` — 36 unit tests for engine

**Modified non-code files:**
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Updated story status

**Modified backend files:**
- `backend/app/db/queries/calculator_results.py` — Added `delete_results_by_types()` query
- `backend/app/db/queries/evaluations.py` — Added `get_any_evaluation_inputs()` query with `ORDER BY updated_at DESC`
- `backend/app/modules/upload/schemas.py` — Added `AutoCalculatedItem`, `ProcessUploadResponse` schemas
- `backend/app/modules/upload/service.py` — Integrated auto-execute into `process_upload()` flow
- `backend/app/modules/upload/router.py` — Updated response_model to `ProcessUploadResponse`
- `backend/app/modules/evaluations/schemas.py` — Added `SingleCalculatorStatus`, `CalculatorStatusResponse`, `RunCalculatorItem`, `RunAllResponse` schemas
- `backend/app/modules/evaluations/router.py` — Added `POST run-all` and `GET status` endpoints
- `backend/tests/integration/api/test_calculators.py` — Added 8 orchestration integration tests
- `backend/tests/integration/api/test_upload.py` — Fixed regression from ProcessUploadResponse change

**Modified frontend files:**
- `frontend/src/hooks/useCalculator.ts` — Added `useCalculatorStatus`, `useRunAllCalculators` hooks + types
- `frontend/src/hooks/useUpload.ts` — Added `AutoCalculatedItem`, `ProcessUploadResponse` types; cache invalidation
- `frontend/src/services/apiClient.ts` — Added `run-all` and `status` endpoint path types; updated `process` response

### Change Log

| Date | Change | Commit |
|------|--------|--------|
| 2026-02-11 | Task 1+4: Engine + DB queries | `7d7a2b0` |
| 2026-02-11 | Task 2: Upload pipeline integration | `1ba7c19` |
| 2026-02-11 | Task 3: Run-all + status endpoints | `f8d3d14` |
| 2026-02-11 | Task 5: 36 unit tests | `57efcb8` |
| 2026-02-11 | Task 6: 8 integration tests + fix regression | `902f666` |
| 2026-02-11 | Task 7: Frontend hooks + API types | `0aadc0c` |
| 2026-02-11 | Fix 9 code review issues (2H/4M/3L) | — |
