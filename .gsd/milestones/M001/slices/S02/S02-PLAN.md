# S02: Scoring Engine Marketplace Awareness

**Goal:** The pure scoring calculator (`calculate_score`) accepts a `marketplace` parameter and produces output with the correct currency code (THB or IDR), formatted values, and marketplace-appropriate scaling for all revenue-related messages, benchmarks, and conclusion text.

**Demo:** Call `calculate_score(..., marketplace='TH')` with THB-scale data → all message templates show `THB` (not `IDR`), competition benchmarks show `THB`, and conclusion text uses appropriate unit scaling instead of `juta`.

## Must-Haves

- `calculate_score()` accepts `marketplace: str = "ID"` parameter — existing callers unaffected
- `_fmt_currency(value, marketplace)` helper returns formatted number (comma-separated, no prefix)
- All 4 business message templates use `{currency}` placeholder instead of hardcoded `IDR`
- All 2 competition message templates use `{currency}` placeholder instead of hardcoded `IDR`
- Competition benchmark string in `_score_competition` uses currency code from marketplace
- `_compute_g66` and `_compute_g66_i18n` use marketplace-appropriate unit scaling (not `juta` for THB)
- `generate_score()` passes `marketplace` to `calculate_score()` (one-line wiring in service.py)
- Migration 027 patches DB-stored message templates to use `{currency}` placeholder (keeps drift test passing)
- All 178+ existing scoring tests pass (no regression)
- New tests verify THB output for business messages, competition messages, benchmarks, and conclusion text

## Proof Level

- This slice proves: contract
- Real runtime required: no
- Human/UAT required: no

## Verification

- `backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py -x` — all existing tests pass (no regression)
- `backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring_marketplace.py -x` — new THB-specific tests pass
- `backend/.venv/bin/python -m pytest backend/tests/unit/test_generate_score_marketplace.py -x` — marketplace wiring tests pass
- `backend/.venv/bin/python -m pytest backend/tests/ -x --timeout=60` — full test suite passes
- New tests assert: THB business messages contain `"THB"` not `"IDR"`, THB competition messages contain `"THB"` not `"IDR"`, THB competition benchmark contains `"THB"`, THB conclusion text does NOT contain `juta`, ID marketplace output unchanged from current behavior
- Failure-path diagnostic: calling `calculate_score(marketplace='XX')` (unknown marketplace) uses IDR fallback via `MARKETPLACE_CURRENCY.get(marketplace, "IDR")` — verified by test that unknown marketplace defaults to IDR output

## Observability / Diagnostics

- Runtime signals: `calculate_score` with `marketplace='TH'` produces messages with `THB` currency code — verifiable by inspecting `ScoringResult.category_scores[*].rows[*].message`
- Inspection surfaces: `_fmt_currency(value, marketplace)` can be called standalone to verify formatting; DB templates inspectable via `SELECT rules->'business'->'monthly_sales_trend'->'message_pass' FROM scoring_rules`
- Failure visibility: `TestMigrationTemplatesDrift` catches any DEFAULT_RULES ↔ DB template divergence; `_SafeDict` renders unresolved `{currency}` placeholder literally if kwarg is missing (visible in output but non-crashing)

## Integration Closure

- Upstream surfaces consumed: `app.core.marketplace.MARKETPLACE_CURRENCY` (S01), `generate_score()` marketplace reading from eval_inputs (S01)
- New wiring introduced in this slice: `marketplace` param threaded from `generate_score()` → `calculate_score()` → message generators / category scorers / computation functions
- What remains before the milestone is truly usable end-to-end: S03 (CSV THB parsing), S04 (frontend marketplace UI)

## Tasks

- [x] **T01: Thread marketplace through scoring engine and create migration 027** `est:45m`
  - Why: All 10 IDR-hardcoded locations must be updated atomically — the formatting helper, message templates, benchmark string, conclusion scaling, and function signatures must change together to avoid broken intermediate states. Migration 027 keeps DB templates in sync.
  - Files: `backend/app/calculators/scoring/helpers.py`, `backend/app/calculators/scoring/_calculator.py`, `backend/app/calculators/scoring/messages.py`, `backend/app/calculators/scoring/categories.py`, `backend/app/calculators/scoring/computations.py`, `backend/app/calculators/scoring/rules.py`, `backend/app/modules/evaluations/service.py`, `backend/app/db/migrations/versions/027_update_message_templates_currency_placeholder.py`
  - Do: (1) Add `_fmt_currency(value, marketplace)` to helpers.py — returns comma-formatted number (same as `_fmt_idr`), keeping `_fmt_idr` as backward compat. (2) Update 4 DEFAULT_RULES templates in rules.py: replace `IDR {idr_val}` → `{currency} {idr_val}`, `IDR {idr_avg}` → `{currency} {idr_avg}`, `IDR {selling_price}` → `{currency} {selling_price}`, `IDR {market_price}` → `{currency} {market_price}`. (3) Update 4 inline default templates in messages.py to match. (4) Add `marketplace` param to `_generate_business_messages`, `_generate_competition_messages`; pass `currency=currency_code` to all `_format_message_template` calls that format currency values; replace `_fmt_idr` with `_fmt_currency` in those functions. (5) Add `marketplace` param to `_score_competition` in categories.py; replace `f"IDR {_fmt_idr(market_price)}"` with `f"{currency_code} {_fmt_currency(market_price, marketplace)}"`. (6) Add `marketplace` param to `_compute_g66` and `_compute_g66_i18n` in computations.py; for THB, use raw number formatting instead of `/ 1_000_000` with `juta`. (7) Add `marketplace: str = "ID"` to `calculate_score()` signature; pass it to `_score_competition`, `_generate_business_messages`, `_generate_competition_messages`, `_compute_g66`, `_compute_g66_i18n`. (8) Pass `marketplace=marketplace` in `generate_score()` call to `calculate_score()` in service.py. (9) Create migration 027 that patches all scoring_rules rows' message templates to replace `IDR` with `{currency}` in the 4 affected template strings.
  - Verify: `backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py -x` — all existing tests still pass
  - Done when: All 10 IDR-hardcoded locations replaced, `calculate_score` accepts `marketplace` param, migration 027 exists, existing test suite passes without modification

- [ ] **T02: Add comprehensive THB marketplace scoring tests** `est:30m`
  - Why: Unit tests must prove that the marketplace threading produces correct THB output — business messages show `THB`, competition messages show `THB`, benchmarks show `THB`, and conclusion text uses appropriate scaling. This is the slice's verification gate.
  - Files: `backend/tests/unit/calculators/test_scoring_marketplace.py`, `backend/tests/unit/test_generate_score_marketplace.py`
  - Do: (1) Create `test_scoring_marketplace.py` with tests for: `_fmt_currency` returns formatted number for both ID and TH; `calculate_score(marketplace='TH')` with THB-scale data produces messages containing `THB`; `calculate_score(marketplace='ID')` produces messages containing `IDR` (backward compat); competition benchmark string contains `THB` for TH marketplace; `_compute_g66` with TH marketplace does NOT contain `juta`; `_compute_g66` with ID marketplace still contains `juta`; `test_default_rules_produce_identical_messages` still works with marketplace='ID'; `TestMigrationTemplatesDrift` still passes (DB templates use `{currency}`, DEFAULT_RULES uses `{currency}`). (2) Add a test to `test_generate_score_marketplace.py` verifying `calculate_score` is called with `marketplace` kwarg from `generate_score`.
  - Verify: `backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring_marketplace.py backend/tests/unit/test_generate_score_marketplace.py -x -v` — all new tests pass; then `backend/.venv/bin/python -m pytest backend/tests/ -x --timeout=60` — full suite passes
  - Done when: ≥8 new tests pass covering THB currency formatting, business messages, competition messages, competition benchmark, conclusion scaling, and backward compatibility; full test suite green

## Files Likely Touched

- `backend/app/calculators/scoring/helpers.py`
- `backend/app/calculators/scoring/_calculator.py`
- `backend/app/calculators/scoring/messages.py`
- `backend/app/calculators/scoring/categories.py`
- `backend/app/calculators/scoring/computations.py`
- `backend/app/calculators/scoring/rules.py`
- `backend/app/modules/evaluations/service.py`
- `backend/app/db/migrations/versions/027_update_message_templates_currency_placeholder.py`
- `backend/tests/unit/calculators/test_scoring_marketplace.py`
- `backend/tests/unit/test_generate_score_marketplace.py`
