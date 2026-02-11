# Story 3.10: Save Evaluation

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **BD team member**,
I want **to save a completed evaluation permanently**,
so that **it becomes part of the evaluation history for this brand and can be reviewed later by the team**.

## Acceptance Criteria

1. **Save evaluation creates permanent record**
   **Given** I have a final score generated for a brand (scoring result available)
   **When** I click "Save Evaluation"
   **Then** create a new record in the `evaluations` table with:
   - `brand_id` — the evaluated brand
   - `user_id` — the authenticated evaluator
   - `template` — "fashion" or "non_fashion"
   - `final_score` — numeric total score (DECIMAL, can be negative)
   - `verdict` — F75 value (e.g., "✔️", "❌", "❌ Non Mall", "❌ No Brand", "❌ Opex", "⭕️", or "")
   - `score_breakdown` — JSONB snapshot of all per-category scores (CategoryScore array)
   - `calculator_results` — JSONB snapshot of all calculator outputs (text output for Calc 1, tables + avg stock for Calc 2, 5 values + flag for Calc 3)
   - `manual_inputs` — JSONB snapshot of all manual input values by category
   - `rule_version` — INTEGER DEFAULT 1 (for future rule configuration tracking)
   - `email_output` — TEXT generated email body
   - `created_at` — TIMESTAMPTZ auto-set to NOW()
   **And** show success toast "Evaluation saved"
   **And** the "Save Evaluation" button becomes disabled with "Saved ✓" state

2. **Multiple saves create separate records (history preserved)**
   **Given** I already saved an evaluation for this brand today
   **When** I save again (after recalculating or changing data)
   **Then** create a NEW evaluation record (INSERT, not upsert)
   **And** previous evaluations are preserved (history)
   **And** each record has its own `created_at` timestamp

3. **Save requires scoring result**
   **Given** I am on the evaluation page
   **When** no scoring result has been generated yet
   **Then** the "Save Evaluation" button is disabled
   **And** I see helper text: "Generate a score first to save"

4. **Save failure is handled gracefully**
   **Given** I click "Save Evaluation"
   **When** the database save fails (network error, server error)
   **Then** show error toast "Failed to save evaluation. Please try again."
   **And** data is NOT lost (still displayed on screen)
   **And** the "Save Evaluation" button remains enabled for retry

5. **Backend save endpoint**
   **Given** I call `POST /api/v1/evaluations/brands/{brand_id}/save`
   **When** authenticated and scoring data is provided in the request body
   **Then** validate that the brand exists
   **And** insert a new record into the `evaluations` table
   **And** return the saved evaluation with its `id` and `created_at`

6. **Save endpoint validates required data**
   **Given** I call `POST /api/v1/evaluations/brands/{brand_id}/save`
   **When** required fields are missing (no `final_score`, no `template`, no `verdict`)
   **Then** return 422 Unprocessable Entity with validation errors

7. **Database migration for evaluations table**
   **Given** the evaluations table does not yet exist
   **When** running migrations
   **Then** create the `evaluations` table with the schema from AC #1
   **And** add indexes on `brand_id` and `created_at` (DESC) for efficient history queries

## Tasks / Subtasks

- [x] Task 1: Create database migration for `evaluations` table (AC: #7)
  - [x] 1.1 Create migration file `backend/app/db/migrations/versions/009_create_evaluations_table.py` (actual next number is 009)
  - [x] 1.2 Define table schema matching AC #1 with all columns and proper types
  - [x] 1.3 Add indexes: `idx_evaluations_brand_id`, `idx_evaluations_created_at` (DESC)
  - [x] 1.4 Run migration locally to verify

- [x] Task 2: Create backend DB queries for evaluations persistence (AC: #1, #5)
  - [x] 2.1 Add `insert_evaluation()` query in `backend/app/db/queries/evaluations.py` — INSERT (not upsert), returns id + created_at
  - [x] 2.2 Use parameterized SQL with `$1, $2, ...` placeholders
  - [x] 2.3 JSONB columns serialized via `json.dumps()` on write

- [x] Task 3: Create backend save service function and endpoint (AC: #1, #2, #5, #6)
  - [x] 3.1 Add `SaveEvaluationRequest` and `SaveEvaluationResponse` schemas in `evaluations/schemas.py`
  - [x] 3.2 Add `save_evaluation()` service function in `evaluations/service.py` — validates brand, inserts record
  - [x] 3.3 Add `POST /api/v1/evaluations/brands/{brand_id}/save` endpoint in `evaluations/router.py`
  - [x] 3.4 Endpoint requires auth via `Depends(get_current_user)`

- [x] Task 4: Write backend tests (AC: #1, #2, #4, #5, #6)
  - [x] 4.1 Unit test: `insert_evaluation()` query creates new record each time (not upsert)
  - [x] 4.2 Integration test: POST /save with full data returns 200 with id + created_at
  - [x] 4.3 Integration test: POST /save with missing required fields returns 422
  - [x] 4.4 Integration test: POST /save with invalid brand_id returns 404
  - [x] 4.5 Integration test: POST /save without auth returns 401
  - [x] 4.6 Integration test: Two saves for same brand create two separate records

- [x] Task 5: Create frontend `useSaveEvaluation` hook (AC: #1, #3, #4)
  - [x] 5.1 Create `frontend/src/hooks/useSaveEvaluation.ts` with TanStack `useMutation`
  - [x] 5.2 POST to `/api/v1/evaluations/brands/{brand_id}/save` via `apiClient.ts`
  - [x] 5.3 Add path type for save endpoint in `apiClient.ts`
  - [x] 5.4 Return: `{ saveEvaluation, isSaving, isSaved, error, reset }`

- [x] Task 6: Wire "Save Evaluation" button in EvaluationSections (AC: #1, #3, #4)
  - [x] 6.1 Enable the existing disabled "Save Evaluation" button in `EvaluationSections.tsx`
  - [x] 6.2 Button enabled only when `scoringResult` is available and not already saved
  - [x] 6.3 On click: assemble request from scoring result + manual data + calculator results + user context
  - [x] 6.4 Show loading state during save, success toast on completion, error toast on failure
  - [x] 6.5 After successful save: button shows "Saved ✓" (disabled), can re-enable after data changes
  - [x] 6.6 Wire `useSaveEvaluation` hook in `EvaluationPage.tsx` and pass callbacks down

- [x] Task 7: Write frontend tests (AC: #1, #3, #4)
  - [x] 7.1 Test: Save button disabled when no scoring result
  - [x] 7.2 Test: Save button enabled when scoring result available
  - [x] 7.3 Test: Save button shows loading state during save
  - [x] 7.4 Test: Save button shows "Saved ✓" after successful save
  - [x] 7.5 Test: Error state shows retry capability

## Dev Notes

### Story Context — Save Evaluation as Permanent Snapshot

This is the final story in Epic 3 (Brand Evaluation Workflow). It takes all the work-in-progress data from the evaluation flow and creates a permanent, immutable record. This is **critical for business value** — without this, evaluations are transient and can't be reviewed later.

**Key architectural decision:** The save creates a **point-in-time snapshot**. All data is copied into the `evaluations` table as JSONB — not referenced by foreign keys. This means:
- If manual inputs change later, the saved evaluation preserves what was there at save time
- If calculator results are re-run, the saved evaluation preserves the original results
- If scoring rules change (Epic 5), the `rule_version` tracks which rules were used

This is an INSERT-only pattern (no upserts). Each save creates a new record. Multiple evaluations for the same brand are expected and encouraged (evaluation history).

### Database Schema — `evaluations` Table

```sql
CREATE TABLE evaluations (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER NOT NULL REFERENCES brand_vp_data(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    template VARCHAR(20) NOT NULL,          -- 'fashion' or 'non_fashion'
    final_score DECIMAL(5,2) NOT NULL,      -- can be negative (e.g., -15.00)
    verdict VARCHAR(20) NOT NULL,           -- F75 value: "✔️", "❌", "❌ Non Mall", etc.
    score_breakdown JSONB NOT NULL,         -- CategoryScore[] snapshot
    calculator_results JSONB NOT NULL,      -- {ads_keyword: {...}, discount: {...}, top_sku: {...}}
    manual_inputs JSONB NOT NULL,           -- ManualData snapshot by category
    rule_version INTEGER NOT NULL DEFAULT 1,
    email_output TEXT,                      -- generated email body (nullable if not generated)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_evaluations_brand_id ON evaluations(brand_id);
CREATE INDEX idx_evaluations_created_at ON evaluations(created_at DESC);
```

**Key differences from `evaluation_inputs` table:**
- No UNIQUE constraint — multiple records per brand allowed (history)
- No `updated_at` — records are immutable once created
- Stores complete snapshots, not references
- `final_score` is DECIMAL(5,2) to support negative scores like -15.50

### Save Request/Response Schemas

**Request body (`SaveEvaluationRequest`):**
```python
class SaveEvaluationRequest(BaseModel):
    template: CategoryType                      # "fashion" | "non_fashion"
    final_score: float                          # total score from scoring
    verdict: VerdictType                        # F75 value
    score_breakdown: list[dict[str, Any]]       # CategoryScore[] as dicts
    calculator_results: dict[str, Any]          # {type: {details, output_text}}
    manual_inputs: dict[str, Any]               # ManualData by category
    rule_version: int = 1
    email_output: str | None = None             # email body text
```

**Response body (`SaveEvaluationResponse`):**
```python
class SaveEvaluationResponse(BaseModel):
    id: int                                     # new record ID
    brand_id: int
    final_score: float
    verdict: str
    template: str
    created_at: datetime
```

### How Data Flows Into the Save Request

```
Frontend assembles save request from:
├── scoringResult (from useScoring hook)
│   ├── total_score → final_score
│   ├── category_scores → score_breakdown (serialized to dicts)
│   ├── verdict → verdict
│   ├── template → template
│   └── email_body → email_output
├── calculatorResults (from useCalculatorResults hook)
│   └── results[] → calculator_results (keyed by calculator_type)
├── manualData (from useAutoSaveForm)
│   └── full ManualData object → manual_inputs
└── rule_version: 1 (hardcoded for now, Epic 5 will make dynamic)
```

### Existing "Save Evaluation" Button Location

The button already exists in `EvaluationSections.tsx` at the bottom of all sections. It is currently **disabled** as a placeholder for this story. The implementation needs to:
1. Wire the button to the new `useSaveEvaluation` hook
2. Enable it when `scoringResult` is available
3. Assemble the request payload from the three data sources above

### Existing Code to Integrate With

**Backend (existing — extend, don't replace):**
- `modules/evaluations/router.py` — Add `POST /save` endpoint alongside existing endpoints
- `modules/evaluations/schemas.py` — Add `SaveEvaluationRequest`, `SaveEvaluationResponse` (existing types `CategoryType`, `VerdictType` reused)
- `modules/evaluations/service.py` — Add `save_evaluation()` function (follows existing pattern: validate brand → DB operation → return response)
- `db/queries/evaluations.py` — Add `insert_evaluation()` function (INSERT not upsert)
- `db/queries/brands.py` — Existing `get_brand_by_id()` reused for validation

**Frontend (existing — extend, don't replace):**
- `pages/EvaluationPage.tsx` — Wire `useSaveEvaluation` hook, pass callbacks to children
- `components/evaluation/EvaluationSections.tsx` — Enable existing "Save Evaluation" button, wire to save handler
- `hooks/useScoring.ts` — `scoringResult` provides final_score, verdict, email_body, score_breakdown, template
- `hooks/useCalculator.ts` — `useCalculatorResults(brandId)` provides calculator outputs
- `hooks/useAutoSaveForm.ts` — `manualData` provides current manual inputs
- `services/apiClient.ts` — Add path type for new save endpoint

### Architecture Compliance

**Backend Pattern (MUST follow):**
- New endpoint in `modules/evaluations/router.py` — REST convention: `POST /api/v1/evaluations/brands/{brand_id}/save`
- Service layer validates brand, performs DB insert — no business logic in router
- DB query uses parameterized SQL (`$1, $2, ...`) — never f-strings or string concatenation
- JSONB columns serialized with `json.dumps()` on write — automatic dict on read
- Transaction pattern: `async with db.connection() as conn:` (single INSERT, transaction optional but fine for consistency)
- Auth required via `Depends(get_current_user)` — returns `user_id` for the record
- Exception chaining: always `raise AppException(...) from e` — never lose tracebacks
- Error codes: `BRAND_NOT_FOUND` (404) for invalid brand_id
- Response schema MUST match AC #5 field-by-field: `id`, `brand_id`, `final_score`, `verdict`, `template`, `created_at`

**Frontend Pattern (MUST follow):**
- Hook uses `apiClient.ts` (openapi-fetch) — never raw `fetch()`
- TanStack Query `useMutation` for the save operation
- Error states have visible UI (error toast, retry) — no swallowed errors
- Use existing shadcn/ui `Button` component with loading state
- Use existing `toast` from shadcn/ui for success/error notifications
- camelCase for variables, PascalCase for components
- No new dependencies — all required libraries already installed

**Data Integrity Rules:**
- Save is INSERT-only — NEVER use ON CONFLICT / upsert for the `evaluations` table
- All JSONB fields are snapshots — do not reference other tables by ID within the JSON
- `created_at` is server-generated (DEFAULT NOW()) — do not accept from client
- `user_id` comes from auth middleware (`get_current_user`) — do not accept from client

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| FastAPI | existing | Router, Depends, Pydantic validation | Installed |
| asyncpg | existing | Parameterized SQL INSERT | Installed |
| pydantic | existing | SaveEvaluationRequest/Response schemas | Installed |
| @tanstack/react-query | existing | useMutation for save | Installed |
| openapi-fetch | existing | Typed API client | Installed |
| shadcn/ui (Button, Toast) | existing | Save button + notifications | Installed |
| lucide-react | existing | Icons (Save, Check, AlertCircle) | Installed |

**No new dependencies needed.** All required libraries are already installed.

### Project Structure Notes

**New files to create:**
```
backend/app/db/migrations/versions/010_create_evaluations_table.py  ← DB migration
backend/tests/integration/api/test_save_evaluation.py               ← Integration tests
frontend/src/hooks/useSaveEvaluation.ts                              ← Save mutation hook
```

**Existing files to modify:**
```
backend/app/db/queries/evaluations.py          ← Add insert_evaluation() query
backend/app/modules/evaluations/schemas.py     ← Add SaveEvaluationRequest, SaveEvaluationResponse
backend/app/modules/evaluations/service.py     ← Add save_evaluation() service function
backend/app/modules/evaluations/router.py      ← Add POST /save endpoint
frontend/src/services/apiClient.ts             ← Add save endpoint path type
frontend/src/pages/EvaluationPage.tsx           ← Wire useSaveEvaluation hook
frontend/src/components/evaluation/EvaluationSections.tsx ← Enable save button, wire handler
```

**Alignment with unified project structure:**
- Backend follows `modules/{feature}/{router,schemas,service}.py` pattern — confirmed
- DB queries in `db/queries/evaluations.py` — extends existing file
- Migration in `db/migrations/versions/` — follows Alembic naming convention
- Frontend hook in `hooks/` directory — follows established pattern
- No new component directories needed — button already exists in EvaluationSections

### Testing Requirements

**Backend Integration Tests (pytest) — `tests/integration/api/test_save_evaluation.py`:**

| Test | AC | Description |
|------|-----|-------------|
| `test_save_evaluation_success` | #1, #5 | POST /save with full valid data returns 200 with `id`, `brand_id`, `final_score`, `verdict`, `template`, `created_at` |
| `test_save_evaluation_missing_fields` | #6 | POST /save without `final_score` or `template` returns 422 |
| `test_save_evaluation_invalid_brand` | #5 | POST /save with non-existent brand_id returns 404 with `BRAND_NOT_FOUND` |
| `test_save_evaluation_auth_required` | #5 | POST /save without auth header returns 401 |
| `test_save_creates_new_record_each_time` | #2 | Two saves for same brand create 2 separate records with different `id` and `created_at` |
| `test_save_evaluation_negative_score` | #1 | POST /save with `final_score: -15.5` succeeds (DECIMAL supports negatives) |
| `test_save_preserves_jsonb_data` | #1 | Saved record has correct `score_breakdown`, `calculator_results`, `manual_inputs` JSONB content |

**Frontend Component Tests (vitest):**

| Test | AC | File | Description |
|------|-----|------|-------------|
| `save button disabled without scoring result` | #3 | EvaluationSections.test.tsx | Button disabled when `scoringResult` is null |
| `save button enabled with scoring result` | #3 | EvaluationSections.test.tsx | Button enabled when `scoringResult` is provided |
| `save button shows loading during save` | #1 | EvaluationSections.test.tsx | Button shows spinner when `isSaving` is true |
| `save button shows saved state` | #1 | EvaluationSections.test.tsx | Button shows "Saved ✓" after `isSaved` is true |
| `error toast on save failure` | #4 | EvaluationSections.test.tsx | Error message displayed when save fails |

**Run commands:**
- Backend: `cd backend && uv run python -m pytest tests/integration/api/test_save_evaluation.py -v`
- Frontend: `cd frontend && npx vitest run --reporter=verbose`
- Full suite: Backend 466+ tests, Frontend 209+ tests (baseline from Story 3.9)

### Previous Story Intelligence

**From Story 3.9 (Final Scoring with Template Selection) — Immediate predecessor:**

- `ScoringResult` dataclass in `calculators/scoring.py` contains ALL data needed for the save:
  - `total_score: float`, `category_scores: list[CategoryScore]`, `verdict: str`, `template: str`
  - `email_body: str`, `email_subject: str`, `whatsapp_link: str`
  - `conclusion: str`, `marketing_estimation: str`, etc.
- Values stored as percentage numbers (0.5 = 0.5%, not fractions) — carry this convention through to saved JSONB
- Frontend `useScoring(brandId)` hook returns `{ scoringResult, isStale, isGenerating, generateScore }`
- `ScoringResponse` schema already maps all ScoringResult fields — reuse these types
- Existing `VerdictType = Literal["✔️", "❌", "❌ Non Mall", "❌ No Brand", "❌ Opex", "⭕️", ""]` — reuse in SaveEvaluationRequest
- Existing `CategoryType = Literal["fashion", "non_fashion"]` — reuse in SaveEvaluationRequest
- ScorePanel shows live scores in sidebar; ScoringSection is the main scoring UI — both are read-only consumers of scoring data
- Code review fix: ScorePanel maps Indonesian category names to English labels via `CATEGORY_MAP` — this mapping is display-only, JSONB stores original names

**From Story 3.8 (Calculator Results Display):**

- `useCalculatorResults(brandId)` hook returns cached calculator results with queryKey `['calculatorResults', brandId]`
- Calculator result structure: `{ calculator_type, output_text, details, calculated_at }`
- Three calculator types: `ads_keyword`, `discount`, `top_sku`
- The save request needs to snapshot these results keyed by `calculator_type`

**From Story 3.3 (Manual Data Input Form):**

- `ManualData` type defined in `formConfig.ts` with all category interfaces
- `useAutoSaveForm` manages `manualData` with auto-save on blur
- `useEvaluationState(brandId)` returns `{ category_type, manual_data, updated_at }`
- The save request needs to snapshot the current `manualData` object

**From Code Reviews (all Epic 3 stories):**

- Response schemas MUST match ACs field-by-field — the `SaveEvaluationResponse` must return exactly: `id`, `brand_id`, `final_score`, `verdict`, `template`, `created_at`
- Frontend hooks MUST use `apiClient.ts` — never raw `fetch()`
- Error states MUST have visible UI (toast, retry button)
- File List MUST include ALL changed files (check `git diff` before marking done)
- React keys: use stable identifiers, not array indices
- 2 pre-existing Firebase config failures in App.test.tsx and EvaluationForms.test.tsx — these are NOT related to this story, ignore them

### Git Intelligence

**Recent commits (Story 3.9 merged to develop):**
```
1374823 Mark stories 3.1 and 3.9 as done after code review
5e67e90 Merge feature/3-9-final-scoring-with-template-selection into develop
cf1f9dd Fix code review findings: ScorePanel mapping, N/A marking, verdict validation, expanded tests
209060e Add scoring display components and useScoring hook (Tasks 6-7)
0510251 Mark Story 3.9 complete — all tasks done, status → review
```

**Patterns to follow:**
- Feature branch naming: `feature/3-10-save-evaluation`
- Atomic commits per task (1 commit per task, sometimes combining tightly-coupled tasks)
- Tests committed alongside implementation
- Branch created from `develop` (current branch)

**Files created/modified in Story 3.9 that this story depends on:**
- `backend/app/calculators/scoring.py` — ScoringResult dataclass (read-only dependency)
- `backend/app/modules/evaluations/router.py` — POST /score endpoint (extend with /save)
- `backend/app/modules/evaluations/schemas.py` — ScoringResponse, CategoryType, VerdictType (reuse)
- `backend/app/modules/evaluations/service.py` — generate_score() pattern (follow for save_evaluation)
- `frontend/src/hooks/useScoring.ts` — scoringResult data source (read-only dependency)
- `frontend/src/components/evaluation/EvaluationSections.tsx` — "Save Evaluation" button placeholder (modify)
- `frontend/src/pages/EvaluationPage.tsx` — hook wiring pattern (extend)

### How This Feeds Into Epic 4 (Evaluation History & Search)

Story 3.10 creates the `evaluations` table that Epic 4 queries extensively:

| Epic 4 Story | Depends On | Fields Used |
|-------------|-----------|-------------|
| 4-1 (History List) | `evaluations` table | brand_id, final_score, template, user_id, created_at — paginated list |
| 4-2 (Search by Brand) | `evaluations` JOIN `brand_vp_data` | brand_name ILIKE search |
| 4-3 (Filter by Date) | `evaluations.created_at` | WHERE created_at BETWEEN date_from AND date_to |
| 4-4 (Filter by Category) | `evaluations.template` | WHERE template = 'fashion' or 'non_fashion' |
| 4-5 (Detail View) | All columns | Full evaluation record with score_breakdown, calculator_results, manual_inputs |
| 4-6 (Real-time Notifications) | SSE broadcast | On INSERT → broadcast `new_evaluation` event |

**Design for Epic 4 compatibility:**
- `idx_evaluations_brand_id` index supports JOIN with brand_vp_data for search
- `idx_evaluations_created_at DESC` index supports date range filtering and default sort order
- No `template` index needed yet (low cardinality, sequential scan OK for 5 users)
- SSE broadcast of `new_evaluation` event is **out of scope** for Story 3.10 — Epic 4 Story 4.6 will add it

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.10 — Story ACs, evaluations table spec, FR27]
- [Source: _bmad-output/planning-artifacts/architecture.md — Module structure, DB conventions, API patterns, naming rules]
- [Source: _bmad-output/planning-artifacts/architecture.md#Data-Architecture — asyncpg + parameterized SQL, Alembic migrations]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Journey-1 — Completion flow: "Submit Evaluation" → confirmation → history]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Feedback-Patterns — Toast notifications, success/error patterns]
- [Source: _bmad-output/planning-artifacts/prd.md — FR27: Save evaluations permanently, NFR14: No data loss on save]
- [Source: _bmad-output/implementation-artifacts/3-9-final-scoring-with-template-selection.md — ScoringResult structure, hooks, test baseline]
- [Source: backend/app/modules/evaluations/router.py — Existing endpoints to extend with POST /save]
- [Source: backend/app/modules/evaluations/schemas.py — CategoryType, VerdictType, ScoringResponse to reuse]
- [Source: backend/app/modules/evaluations/service.py — generate_score() pattern to follow]
- [Source: backend/app/db/queries/evaluations.py — Existing query patterns (upsert, parameterized SQL)]
- [Source: backend/app/db/queries/calculator_results.py — get_results_by_brand() for loading calculator outputs]
- [Source: backend/app/calculators/scoring.py — ScoringResult dataclass with all score fields]
- [Source: frontend/src/hooks/useScoring.ts — scoringResult data, ScoringResult type]
- [Source: frontend/src/hooks/useCalculator.ts — useCalculatorResults for loading calculator data]
- [Source: frontend/src/hooks/useEvaluation.ts — useEvaluationState, useSaveEvaluationInputs patterns]
- [Source: frontend/src/hooks/useAutoSaveForm.ts — manualData state management]
- [Source: frontend/src/components/evaluation/EvaluationSections.tsx — "Save Evaluation" button placeholder]
- [Source: frontend/src/pages/EvaluationPage.tsx — Hook wiring, prop passing patterns]
- [Source: frontend/src/services/apiClient.ts — Path type definitions for openapi-fetch]
- [Source: frontend/src/components/evaluation/forms/formConfig.ts — ManualData type, formatIDR]
- [Source: _bmad-output/lessons-learned.md — Code review patterns, schema matching, error handling]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

No blocking issues encountered during implementation.

### Completion Notes List

- Task 1: Created migration 009_create_evaluations_table.py with full schema (DECIMAL(5,2) for negative scores, JSONB columns, indexes on brand_id and created_at DESC)
- Task 2: Added insert_evaluation() query using parameterized SQL ($1..$10), json.dumps() for JSONB serialization, INSERT-only (no upsert)
- Task 3: Added SaveEvaluationRequest/Response schemas (reusing CategoryType, VerdictType), save_evaluation() service with brand validation, POST /save endpoint with auth
- Task 4: 7 backend integration tests covering: success, missing fields (422), invalid brand (404), auth required (401), multiple saves create separate records, negative scores, JSONB data preservation
- Task 5: Created useSaveEvaluation hook with TanStack useMutation, isSaved state tracking, reset capability
- Task 6: Wired save button with 3 states (default/loading/saved), helper text when no scoring result, error display, toast notifications via sonner, data assembly from scoringResult + calculatorResults + manualData
- Task 7: 7 frontend component tests for save button states; updated EvaluationPage.test.tsx mocks for new hooks

### Senior Developer Review (AI)

**Reviewer:** Mr. Door (Claude Opus 4.6)
**Date:** 2026-02-11
**Outcome:** Approved (after fixes)

**Issues Found:** 1 High, 2 Medium, 4 Low — 5 fixed, 2 deferred (L2 test naming, L3 verdict type)

| # | Severity | Finding | Fix Applied |
|---|----------|---------|-------------|
| H1 | HIGH | `onResetSave` wired but never invoked — save button stuck on "Saved ✓" after first save, breaking multi-save workflow (AC #2) | Added `useEffect` in EvaluationPage.tsx that calls `resetSave()` when `manualData` or `scoringResult` changes after a save |
| M1 | MEDIUM | `save_evaluation` service lacks explicit transaction (inconsistent with `save_evaluation_inputs` in same file) | Wrapped queries in `async with conn.transaction():` |
| M2 | MEDIUM | No test for save request payload assembly logic in `handleSaveEvaluation` | Added `assembles correct save payload` test in EvaluationPage.test.tsx |
| L1 | LOW | Inline error "Failed to save." differs from toast "Failed to save evaluation." | Fixed inline text to match AC: "Failed to save evaluation. Please try again." |
| L2 | LOW | `SaveButton.test.tsx` naming doesn't follow co-located convention | Deferred — cosmetic, no functional impact |
| L3 | LOW | Frontend `verdict` type is `string` instead of VerdictType union | Deferred — would cascade into ScoringResult type; backend Pydantic validates |
| L4 | LOW | `useSaveEvaluation.reset` callback unstable due to `[mutation]` dependency | Extracted `mutation.reset` to stable ref `resetMutation` |

**Backend tests:** 7/7 passed (updated mocks for new transaction pattern)
**Frontend tests:** 15/15 passed (7 SaveButton + 8 EvaluationPage including new payload test)

### Change Log

- 2026-02-11: Implemented Story 3.10 — Save Evaluation feature (all 7 tasks)
- 2026-02-11: Code review — fixed 5 issues (1H, 2M, 2L), deferred 2 LOW, all tests passing

### File List

**New files:**
- backend/app/db/migrations/versions/009_create_evaluations_table.py
- backend/tests/integration/api/test_save_evaluation.py
- frontend/src/hooks/useSaveEvaluation.ts
- frontend/src/components/evaluation/SaveButton.test.tsx

**Modified files:**
- backend/app/db/queries/evaluations.py
- backend/app/modules/evaluations/schemas.py
- backend/app/modules/evaluations/service.py
- backend/app/modules/evaluations/router.py
- frontend/src/services/apiClient.ts
- frontend/src/pages/EvaluationPage.tsx
- frontend/src/pages/EvaluationPage.test.tsx
- frontend/src/components/evaluation/EvaluationSections.tsx
- _bmad-output/implementation-artifacts/sprint-status.yaml
