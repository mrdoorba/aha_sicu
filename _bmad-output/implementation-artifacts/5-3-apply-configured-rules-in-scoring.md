# Story 5.3: Apply Configured Rules in Scoring

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system**,
I want **to apply the configured rules from the database during score calculation**,
so that **scoring reflects the latest business thresholds without code deployment**.

## Acceptance Criteria

1. **Scoring calculator uses DB rules instead of hardcoded values**
   **Given** a final score calculation is triggered via `POST /api/v1/evaluations/brands/{brand_id}/score`
   **When** the scoring calculator runs
   **Then** fetch current rules from `scoring_rules` table for the selected template (fashion or non_fashion)
   **And** pass the rules JSONB to the `calculate_score()` pure function as a new `rules` parameter
   **And** apply thresholds, points, and comparison operators from the rules instead of hardcoded values
   **And** the scoring calculator remains a pure function (rules passed in, no DB access inside)

2. **All scoring categories use configurable thresholds**
   **Given** the rules JSONB contains category-specific thresholds
   **When** scoring each category
   **Then** the following categories read their thresholds from the rules dict:
   - **Operational:** unfulfilled_order_rate (threshold, points), late_shipment_rate (threshold, points), preparation_time (threshold, points), chat_response_rate (threshold), overall_rating (threshold)
   - **Business:** monthly_sales_trend (threshold_pct, points), six_month_avg_threshold (threshold, points), conversion_rate (threshold)
   - **Visitors:** returning_visitors_pct (threshold, points), followers (threshold, points)
   - **Promo Tools:** usage_pct_threshold (threshold, opportunity_points), effectiveness_pct_threshold (threshold, opportunity_points)
   - **Products/Status:** product_count (threshold, points), store_status_points (mall, star_plus, star, regular)
   - **Ads:** roi_threshold (threshold, opportunity_points), gmv_ratio_threshold (threshold, points)
   - **Campaign:** participation_pct_threshold (threshold, opportunity_points)
   - **Stock:** high_threshold (threshold, points), mid_threshold (threshold, points), low_penalty (threshold, points)
   - **Discount:** fake_discount_flag (points_no_flag, points_flag)
   - **Interpretation:** ranges (min, max, label, verdict)
   **And** if a rule key is missing, fall back to the current hardcoded default value (defensive)

3. **Rule version is returned in scoring response**
   **Given** a score is generated using rules from the DB
   **When** the scoring response is returned
   **Then** the `ScoringResponse` includes a new `rule_version: int` field
   **And** the value matches `scoring_rules.version` for the template used

4. **Frontend uses rule_version from scoring response**
   **Given** the frontend generates a score and receives the response
   **When** the user clicks "Save Evaluation"
   **Then** the `rule_version` from the scoring response is used in the save request
   **And** the frontend no longer hardcodes `rule_version: 1`

5. **Historical evaluations show rule version context**
   **Given** rules were updated after an evaluation was saved
   **When** viewing a historical evaluation in the detail view
   **Then** the detail page continues to show "Rule v{evaluation.rule_version}" (already implemented)
   **And** no changes needed to the existing detail view display

6. **Default rules produce identical scores to current hardcoded behavior**
   **Given** the scoring_rules table contains the default seed values (from migration 010)
   **When** a score is calculated using rules from the DB
   **Then** the result is identical to the current hardcoded calculation
   **And** all existing scoring tests continue to pass with default rules

7. **Modified rules produce different scores**
   **Given** a system owner has updated rules (e.g., changed operational unfulfilled_order_rate threshold from 1.0 to 2.0)
   **When** a score is calculated using the updated rules
   **Then** the scoring reflects the new thresholds
   **And** the rule_version in the response matches the updated version number

## Tasks / Subtasks

- [x] Task 1: Add `rules` parameter to `calculate_score()` and all per-category scoring functions (AC: #1, #2, #6)
  - [x] 1.1 Add `rules: dict | None = None` parameter to `calculate_score()` signature
  - [x] 1.2 Define `DEFAULT_FASHION_RULES` and `DEFAULT_NON_FASHION_RULES` constants in `scoring.py` (copy from migration 010 seed data) for fallback when `rules` is None
  - [x] 1.3 Add helper `_get_rule(rules, category, key, field, default)` to safely extract rule values with fallback
  - [x] 1.4 Refactor `_score_operational(manual_data, rules)` — replace hardcoded thresholds (1.0, 4pts, 3pts, 95.0, 4.7) with rule lookups
  - [x] 1.5 Refactor `_score_business(manual_data, rules)` — replace hardcoded thresholds (90%, 100M, conversion rate) with rule lookups
  - [x] 1.6 Refactor `_score_content(manual_data, rules)` — replace hardcoded 0.95 threshold with rule lookup
  - [x] 1.7 Refactor `_score_visitors(manual_data, rules)` — replace hardcoded thresholds (23%, 50000, 3pts, 2pts) with rule lookups
  - [x] 1.8 Refactor `_score_promo_tools(manual_data, rules)` — replace hardcoded 0.80 and 0.90 thresholds with rule lookups
  - [x] 1.9 Refactor `_score_products(manual_data, rules)` — replace hardcoded thresholds (35, mall=10, star_plus=5) with rule lookups
  - [x] 1.10 Refactor `_score_ads(manual_data, template, rules)` — replace hardcoded ROI threshold (8/9) and GMV threshold (0.84) with rule lookups
  - [x] 1.11 Refactor `_score_campaign(manual_data, rules)` — replace hardcoded 0.90 threshold with rule lookup
  - [x] 1.12 Refactor `_score_stock(calculator_results, rules)` — replace hardcoded thresholds (24, 12, -5/5/10pts) with rule lookups
  - [x] 1.13 Refactor `_score_discount_row(calculator_results, rules)` — replace hardcoded 5/0 points with rule lookups
  - [x] 1.14 Update conversion rate template logic (line 1366) to use `rules["business"]["conversion_rate"]["threshold"]` instead of hardcoded 2.0/3.0
  - [x] 1.15 Update marketing percentage floor in `_compute_g72()` to derive from rules if possible (0.15 fashion / 0.12 non-fashion)

- [x] Task 2: Add `rule_version` to `ScoringResponse` schema (AC: #3)
  - [x] 2.1 Add `rule_version: int` field to `ScoringResponse` in `backend/app/modules/evaluations/schemas.py`
  - [x] 2.2 Update `ScoringResult` dataclass in `scoring.py` to include `rule_version: int` field

- [x] Task 3: Update `generate_score()` service to load rules from DB (AC: #1, #3)
  - [x] 3.1 Import `rules_queries` from `app.db.queries`
  - [x] 3.2 In `generate_score()`, within the existing `db.connection()` block, call `rules_queries.get_rules_by_template(conn, template)`
  - [x] 3.3 Extract `rules_jsonb = rule_row["rules"]` and `rule_version = rule_row["version"]`
  - [x] 3.4 Pass `rules=rules_jsonb` to `calculate_score()`
  - [x] 3.5 Include `rule_version` in the `ScoringResponse` return

- [x] Task 4: Update existing scoring unit tests to pass rules parameter (AC: #6)
  - [x] 4.1 Create `DEFAULT_RULES` test fixture matching the migration 010 seed data
  - [x] 4.2 Update all existing `calculate_score()` calls in `test_scoring.py` to pass `rules=DEFAULT_RULES`
  - [x] 4.3 Verify all existing tests pass with the default rules (identical behavior)
  - [x] 4.4 Also test that `rules=None` falls back to defaults (backward compatibility)

- [x] Task 5: Add new scoring tests with modified rules (AC: #7)
  - [x] 5.1 Test `_score_operational` with custom thresholds (e.g., unfulfilled threshold=2.0, points=6) produces different score
  - [x] 5.2 Test `_score_ads` with custom ROI threshold (e.g., 5.0 instead of 8.0) changes verdict
  - [x] 5.3 Test `_score_stock` with custom thresholds (e.g., high=30, mid=15) changes scoring tiers
  - [x] 5.4 Test `_score_discount_row` with custom points (e.g., points_no_flag=10, points_flag=-5)
  - [x] 5.5 Test `calculate_score()` end-to-end with modified rules produces different total_score
  - [x] 5.6 Test rule_version is included in ScoringResult

- [x] Task 6: Add integration test for scoring endpoint with DB rules (AC: #1, #3)
  - [x] 6.1 Test `POST /api/v1/evaluations/brands/{id}/score` returns `rule_version` field
  - [x] 6.2 Test returned `rule_version` matches `scoring_rules.version` for the template
  - [x] 6.3 Test scoring with default rules produces expected results

- [x] Task 7: Update frontend `ScoringResult` type and `useScoring` hook (AC: #3, #4)
  - [x] 7.1 Add `rule_version: number` to `ScoringResult` interface in `useScoring.ts`
  - [x] 7.2 The hook already passes through the full response — no logic changes needed

- [x] Task 8: Update `EvaluationPage.tsx` to use rule_version from scoring response (AC: #4)
  - [x] 8.1 In `handleSaveEvaluation`, replace hardcoded `rule_version: 1` with `scoringResult.rule_version`
  - [x] 8.2 Verify the value flows correctly to the save API request

- [x] Task 9: Write frontend tests (AC: #4)
  - [x] 9.1 Test `EvaluationPage` passes `rule_version` from scoring result to save request (not hardcoded 1)
  - [x] 9.2 Test `useScoring` hook returns `rule_version` from API response

## Dev Notes

### Story Context — Third and Final Story of Epic 5 (Rule Configuration)

This is the final story in Epic 5, closing the loop on rule configuration:
- **Story 5.1 (done):** View current scoring rules — read-only display + DB migration + seed data
- **Story 5.2 (done):** Edit scoring rules with password confirmation — write operations
- **Story 5.3 (this):** Apply configured rules in scoring — integrate DB rules into the scoring calculator

**Critical design decision:** The scoring calculator (`calculators/scoring.py`) MUST remain a pure function. Rules are loaded by the service layer (`modules/evaluations/service.py`) and passed into `calculate_score()`. This preserves testability and the architecture boundary: calculators have no I/O.

### Core Refactoring Strategy

**Approach: Add `rules` parameter to the pure function, extract thresholds with fallback**

The refactoring follows a consistent pattern for every scoring function:

```python
# BEFORE (hardcoded):
def _score_operational(manual_data: dict) -> CategoryScore:
    if d7 <= 1.0:
        f7, h7 = "✔️", 4.0

# AFTER (rules-driven with fallback):
def _score_operational(manual_data: dict, rules: dict | None = None) -> CategoryScore:
    ops_rules = _get_rule_category(rules, "operational")
    threshold = _get_rule_value(ops_rules, "unfulfilled_order_rate", "threshold", 1.0)
    points = _get_rule_value(ops_rules, "unfulfilled_order_rate", "points", 4.0)
    if d7 <= threshold:
        f7, h7 = "✔️", points
```

**Helper functions to add:**

```python
def _get_rule_category(rules: dict | None, category: str) -> dict:
    """Get a category dict from rules, or empty dict if missing."""
    if rules is None:
        return {}
    return rules.get(category, {})

def _get_rule_value(category_rules: dict, key: str, field: str, default: Any) -> Any:
    """Get a specific value from category rules, with default fallback."""
    return category_rules.get(key, {}).get(field, default)
```

**Why this approach:**
- Every threshold gets a sensible default = current hardcoded value
- If rules dict is None (backward compat), all defaults apply — identical behavior
- If rules dict is incomplete (e.g., missing a category), only that category falls back
- No risk of breaking existing behavior when rules have default seed values
- Minimal diff: each function gains 2-5 lines for rule extraction, thresholds swap to variables

### Rules JSONB Structure (from migration 010 seed data)

The rules are stored per-template in `scoring_rules.rules` as JSONB. Structure:

```python
{
    "operational": {
        "unfulfilled_order_rate": {"threshold": 1.0, "points": 4, "comparison": "lte"},
        "late_shipment_rate": {"threshold": 1.0, "points": 3, "comparison": "lte"},
        "preparation_time": {"threshold": 1.0, "points": 3, "comparison": "lte"},
        "chat_response_rate": {"threshold": 95.0, "comparison": "gte", "info_only": True},
        "overall_rating": {"threshold": 4.7, "comparison": "gte", "info_only": True},
    },
    "business": {
        "monthly_sales_trend": {"threshold_pct": 90.0, "points": 10, "comparison": "gte"},
        "six_month_avg_threshold": {"threshold": 100000000, "points": 10, "comparison": "gte"},
        "conversion_rate": {"threshold": 2.0, "comparison": "gte", "info_only": True},  # 3.0 for non_fashion
    },
    "content": {
        "quality_ratio": {"threshold": 95.0, "comparison": "gte", "info_only": True},
    },
    "visitors": {
        "returning_visitors_pct": {"threshold": 23.0, "points": 3, "comparison": "gte"},
        "followers": {"threshold": 50000, "points": 2, "comparison": "gte"},
    },
    "promo_tools": {
        "usage_pct_threshold": {"threshold": 80.0, "opportunity_points": 5},
        "effectiveness_pct_threshold": {"threshold": 90.0, "opportunity_points": 10},
    },
    "products_status": {
        "product_count": {"threshold": 35, "points": 5, "comparison": "gte"},
        "store_status_points": {"mall": 10, "star_plus": 5, "star": 0, "regular": 0},
    },
    "ads": {
        "roi_threshold": {"threshold": 8.0, "opportunity_points": 5, "comparison": "gt"},  # 9.0 for non_fashion
        "gmv_ratio_threshold": {"threshold": 84.0, "points": 5, "comparison": "lt"},
        "cost_ratio_range": {"min": 5.0, "max": 10.0, "info_only": True},
    },
    "campaign": {
        "participation_pct_threshold": {"threshold": 90.0, "opportunity_points": 10, "comparison": "gte"},
    },
    "stock": {
        "high_threshold": {"threshold": 24, "points": 10, "comparison": "gte"},
        "mid_threshold": {"threshold": 12, "points": 5, "comparison": "gte"},
        "low_penalty": {"threshold": 12, "points": -5, "comparison": "lt"},
    },
    "discount": {
        "fake_discount_flag": {"points_no_flag": 5, "points_flag": 0},
    },
    "interpretation": {
        "ranges": [
            {"min": 71, "max": None, "label": "Good Candidate", "verdict": "✔️"},
            {"min": 41, "max": 70, "label": "Needs Review", "verdict": "⭕️"},
            {"min": None, "max": 40, "label": "Not Recommended", "verdict": "❌"},
        ],
    },
}
```

**Important:** Percentage values follow the project convention: `1.0` = 1% (not 0.01). The scoring functions already work in this convention — thresholds in rules match exactly.

### Service Layer Integration

**Current flow (service.py `generate_score()` lines 144-248):**

```python
async with db.connection() as conn:
    brand = await brand_queries.get_brand_by_id(conn, brand_id)
    eval_inputs = await eval_queries.get_evaluation_inputs(conn, brand_id, user_id)
    calc_rows = await calc_queries.get_results_by_brand(conn, brand_id)

result = calculate_score(manual_data=..., calculator_results=..., template=..., ...)
return ScoringResponse(...)
```

**New flow (add 2 lines inside existing `db.connection()` block):**

```python
async with db.connection() as conn:
    brand = await brand_queries.get_brand_by_id(conn, brand_id)
    eval_inputs = await eval_queries.get_evaluation_inputs(conn, brand_id, user_id)
    calc_rows = await calc_queries.get_results_by_brand(conn, brand_id)
    # NEW: Load rules for template
    rule_row = await rules_queries.get_rules_by_template(conn, template)

rules_jsonb = rule_row["rules"] if rule_row else None
rule_version = rule_row["version"] if rule_row else 1

result = calculate_score(manual_data=..., calculator_results=..., template=..., rules=rules_jsonb, ...)
return ScoringResponse(..., rule_version=rule_version)
```

**Note:** `get_rules_by_template()` already exists in `db/queries/rules.py` — no new query needed. Single additional DB call, same connection.

### G-Column Message Benchmark Strings

The G-column message functions (e.g., `_generate_operational_messages`) currently use hardcoded benchmark strings in messages like `"nilai disarankan: <1%"`. For this story, **DO NOT make message templates dynamic** — the benchmark strings in messages are presentation text, not scoring logic. Only the scoring thresholds and points need to be dynamic.

If future stories want dynamic message text, that's a separate concern. This story focuses on scoring calculation accuracy.

### Frontend Changes — Minimal

The frontend changes are very small:

1. **`useScoring.ts`:** Add `rule_version: number` to `ScoringResult` interface (1 line)
2. **`EvaluationPage.tsx`:** Replace `rule_version: 1` with `scoringResult.rule_version` (1 line)

No new components, no new hooks, no layout changes.

### Project Structure Notes

- All modifications extend existing files — no new files except test files
- `calculators/scoring.py` is the largest change (refactoring all scoring functions)
- `modules/evaluations/service.py` gains 2 lines for rule loading
- `modules/evaluations/schemas.py` gains 1 field
- No database migration needed — both `scoring_rules` and `evaluations.rule_version` already exist
- No new dependencies needed

### Architecture Compliance

**Backend Pattern (MUST follow):**
- Calculator remains pure function — no DB access inside `calculators/scoring.py`
- Rules loaded by service layer (`modules/evaluations/service.py`), passed to calculator
- Existing `get_rules_by_template()` query reused — no new queries needed
- Error handling: if rules not found in DB, fall back to None (defaults apply)
- Schemas: add `rule_version: int` to `ScoringResponse` Pydantic model

**Frontend Pattern (MUST follow):**
- `ScoringResult` type updated in `useScoring.ts`
- `EvaluationPage.tsx` reads `rule_version` from scoring response
- No raw `fetch()` — all through `apiClient.ts` (already the case)

**Naming Conventions:**
- Backend: snake_case — `rule_version`, `_get_rule_value()`, `rules_jsonb`
- Frontend: camelCase in code, but `rule_version` in API data (snake_case JSON)
- New helper functions: `_get_rule_category()`, `_get_rule_value()` (private, snake_case)

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| FastAPI | existing | No endpoint changes (just response schema) | Installed |
| asyncpg | existing | Reuse existing `get_rules_by_template()` query | Installed |
| Pydantic | existing | Add `rule_version: int` to ScoringResponse | Installed |
| @tanstack/react-query | v5 (existing) | No changes to hook patterns | Installed |
| openapi-fetch | existing | No changes | Installed |

**No new dependencies required — all libraries already installed.**

### File Structure Requirements

**Modified files (backend):**
```
backend/app/calculators/scoring.py              — Add rules parameter to all scoring functions, helper extractors
backend/app/modules/evaluations/service.py      — Load rules from DB before calling calculate_score()
backend/app/modules/evaluations/schemas.py      — Add rule_version to ScoringResponse
backend/tests/unit/calculators/test_scoring.py  — Update existing tests with rules fixture, add custom rules tests
```

**New files (backend):**
```
backend/tests/integration/api/test_scoring_rules_integration.py  — Integration test for scoring + rules
```

**Modified files (frontend):**
```
frontend/src/hooks/useScoring.ts        — Add rule_version to ScoringResult interface
frontend/src/pages/EvaluationPage.tsx   — Use scoringResult.rule_version instead of hardcoded 1
```

**New files (frontend):**
```
(none — existing test files may be updated)
```

### Testing Requirements

**Backend Unit Tests (pytest) — update `test_scoring.py` + new tests:**

| Test | AC | Description |
|------|-----|-------------|
| `test_calculate_score_with_default_rules` | #6 | Default rules produce identical results to current hardcoded tests |
| `test_calculate_score_rules_none_fallback` | #6 | `rules=None` falls back to defaults — backward compatible |
| `test_operational_custom_thresholds` | #2, #7 | Custom operational thresholds change scores |
| `test_business_custom_thresholds` | #2, #7 | Custom business thresholds change scores |
| `test_ads_custom_roi_threshold` | #2, #7 | Custom ROI threshold changes verdict |
| `test_stock_custom_thresholds` | #2, #7 | Custom stock thresholds change scoring tiers |
| `test_discount_custom_points` | #2, #7 | Custom discount points change category score |
| `test_visitors_custom_thresholds` | #2, #7 | Custom visitor thresholds change scores |
| `test_promo_custom_thresholds` | #2, #7 | Custom promo thresholds change opportunity points |
| `test_campaign_custom_threshold` | #2, #7 | Custom campaign threshold changes score |
| `test_products_custom_thresholds` | #2, #7 | Custom product count and status points |
| `test_scoring_result_includes_rule_version` | #3 | ScoringResult dataclass has rule_version field |
| `test_end_to_end_modified_rules_total_score` | #7 | Modified rules produce different total_score |

**Backend Integration Tests (pytest) — `test_scoring_rules_integration.py`:**

| Test | AC | Description |
|------|-----|-------------|
| `test_score_endpoint_returns_rule_version` | #3 | POST scoring endpoint includes rule_version in response |
| `test_score_uses_db_rules` | #1 | Scoring uses rules from DB (mock rules query) |
| `test_rule_version_matches_db` | #3 | rule_version in response matches scoring_rules.version |

**Frontend Tests (vitest):**

| Test | AC | Description |
|------|-----|-------------|
| `test_save_uses_rule_version_from_scoring` | #4 | EvaluationPage passes scoring rule_version to save (not 1) |
| `test_scoring_result_type_includes_rule_version` | #3 | ScoringResult interface includes rule_version |

**Run commands:**
- Backend unit: `cd backend && uv run python -m pytest tests/unit/calculators/test_scoring.py -v`
- Backend integration: `cd backend && uv run python -m pytest tests/integration/api/test_scoring_rules_integration.py -v`
- Frontend: `cd frontend && npx vitest run src/pages/EvaluationPage --reporter=verbose`

### Previous Story Intelligence (from Story 5.2)

**Key patterns established in 5.2 that apply here:**
- `scoring_rules` table created with `id`, `template`, `rules` (JSONB), `version` (int), `updated_by`, `updated_at`
- Seed data inserted by migration 010 — FASHION_RULES and NON_FASHION_RULES dicts exactly match the hardcoded thresholds in `scoring.py`
- `get_rules_by_template(conn, template)` query already exists and returns the row as a dict
- Rules service in `app/modules/rules/service.py` wraps the query
- ScoringRuleResponse schema: `id: int, template: str, rules: dict, version: int, updated_by: int | None, updated_at: datetime | None`
- Test count after 5.2: 544 backend + 285 frontend (all passing)
- `require_role` decorator pattern used for admin endpoints (not needed here — scoring endpoint already exists)
- Password confirmation pattern uses Firebase reauthentication (not relevant to this story)

**Files created/modified in 5.2 (do NOT recreate or duplicate):**
- `backend/app/db/migrations/versions/010_create_scoring_rules_table.py` — migration + seed data (ALREADY EXISTS)
- `backend/app/db/queries/rules.py` — DB queries (ALREADY EXISTS, reuse `get_rules_by_template`)
- `backend/app/modules/rules/` — service, schemas, router (ALREADY EXISTS, not modified in 5.3)
- `frontend/src/pages/RulesPage.tsx` — rules management UI (not relevant to 5.3)

### Git Intelligence Summary

Recent commit history shows:
- Story 5.2 completed: scoring rules CRUD operations with password confirmation
- Story 5.1 completed: read-only rules display with DB migration
- Epic 4 fully complete: evaluation history, search, filters, detail view, SSE notifications
- Epic 3 fully complete: brand evaluation workflow including scoring calculator
- Codebase is stable with 544 backend + 285 frontend tests passing

Branch strategy: work on `feature/5-3-apply-configured-rules-in-scoring`, merge to `develop` when done.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 5, Story 5.3 ACs]
- [Source: `_bmad-output/planning-artifacts/architecture.md` — Calculators as pure functions, module structure]
- [Source: `_bmad-output/implementation-artifacts/5-2-edit-scoring-rules-with-password-confirmation.md` — Previous story patterns]
- [Source: `backend/app/calculators/scoring.py` — Current hardcoded scoring calculator (1429 lines)]
- [Source: `backend/app/modules/evaluations/service.py` — `generate_score()` function, lines 144-248]
- [Source: `backend/app/modules/evaluations/schemas.py` — `ScoringResponse`, `SaveEvaluationRequest`]
- [Source: `backend/app/db/queries/rules.py` — `get_rules_by_template()` query]
- [Source: `backend/app/db/migrations/versions/010_create_scoring_rules_table.py` — Rules JSONB structure and seed data]
- [Source: `frontend/src/hooks/useScoring.ts` — `ScoringResult` interface]
- [Source: `frontend/src/pages/EvaluationPage.tsx:96` — Hardcoded `rule_version: 1`]
- [Source: `_bmad-output/lessons-learned.md` — Percentage convention, pytest command, cache patterns]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

### Completion Notes List

- All 10 per-category scoring functions refactored to accept `rules: dict | None = None` with fallback defaults matching current hardcoded values
- Helper functions `_get_rule_category()` and `_get_rule_value()` provide safe extraction with defaults
- `DEFAULT_FASHION_RULES` and `DEFAULT_NON_FASHION_RULES` constants copied from migration 010 seed data
- Service layer loads rules via existing `get_rules_by_template()` query — single additional DB call in same connection
- Percentage threshold convention: rules store percentages as whole numbers (95.0 = 95%), scoring functions divide by 100 where needed
- Monthly sales trend: `threshold_pct=90` converts to multiplier via `(200 - threshold_pct) / 100 = 1.10`
- Products `store_status_points` uses direct dict access (not `_get_rule_value`) since it's a different structure
- Integration test fix: existing tests needed `SAMPLE_RULES_ROW` added to `fetchrow` side_effect sequences
- All 121 tests pass: 102 backend unit + 11 backend integration + 8 frontend

### Commits

1. `d534b8b` — Task 1: Add rules parameter to scoring calculator and refactor all per-category functions
2. `56c9c0e` — Tasks 2-3: Add rule_version to schema, load rules from DB in service
3. `1986ce8` — Tasks 4-5: Add unit tests for default rules identity and custom rules behavior
4. `c2a80b0` — Task 6: Add integration tests for scoring endpoint with DB rules
5. `bd8f78c` — Tasks 7-8: Update frontend ScoringResult type and EvaluationPage to use dynamic rule_version
6. `e484d0c` — Task 9: Add frontend test for dynamic rule_version in save payload

### File List

**Modified (backend):**
- `backend/app/calculators/scoring.py` — Added rules parameter, helper functions, DEFAULT_*_RULES constants, refactored all scoring functions
- `backend/app/modules/evaluations/schemas.py` — Added `rule_version: int` to ScoringResponse
- `backend/app/modules/evaluations/service.py` — Load rules from DB, pass to calculate_score(), include in response
- `backend/tests/unit/calculators/test_scoring.py` — 18 new tests (4 default rules identity + 14 custom rules behavior)
- `backend/tests/integration/api/test_scoring.py` — Fixed 3 existing tests, added 3 new integration tests

**Modified (frontend):**
- `frontend/src/hooks/useScoring.ts` — Added `rule_version: number` to ScoringResult interface
- `frontend/src/pages/EvaluationPage.tsx` — Changed `rule_version: 1` to `scoringResult.rule_version`
- `frontend/src/pages/EvaluationPage.test.tsx` — Updated save payload test to verify dynamic rule_version
