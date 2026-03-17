---
id: T01
parent: S02
milestone: M001
provides:
  - _fmt_currency(value, marketplace) helper for marketplace-aware currency formatting
  - {currency} placeholder in all 8 message templates (4 DEFAULT_RULES + 4 inline defaults)
  - marketplace parameter threaded through calculate_score → 5 sub-functions
  - Migration 027 patching DB templates from IDR to {currency}
  - Service layer wiring (generate_score → calculate_score marketplace passthrough)
key_files:
  - backend/app/calculators/scoring/helpers.py
  - backend/app/calculators/scoring/rules.py
  - backend/app/calculators/scoring/messages.py
  - backend/app/calculators/scoring/categories.py
  - backend/app/calculators/scoring/computations.py
  - backend/app/calculators/scoring/_calculator.py
  - backend/app/modules/evaluations/service.py
  - backend/app/db/migrations/versions/027_update_message_templates_currency_placeholder.py
key_decisions:
  - _fmt_currency delegates to _fmt_idr — formatting is identical for both IDR/THB (comma thousands). Currency CODE is handled by template placeholders, not by the formatting function.
  - marketplace param uses keyword-only syntax in message generators (_generate_business_messages, _generate_competition_messages) to avoid positional arg confusion
  - Migration 027 queries by (template, marketplace) compound key to match the 026-era schema
patterns_established:
  - Thread marketplace as keyword-only param with default "ID" through scoring sub-functions
  - Use MARKETPLACE_CURRENCY.get(marketplace, "IDR") for fallback-safe currency code resolution
  - For THB marketplace, _compute_g66 uses raw formatted numbers instead of /1M juta scaling
observability_surfaces:
  - calculate_score(marketplace='TH') produces messages with THB currency code — visible in ScoringResult.category_scores[*].rows[*].message
  - _SafeDict renders unresolved {currency} literally if kwarg missing — visible but non-crashing
  - TestMigrationTemplatesDrift catches DB↔code template divergence (now replays 012→019→020→021→027)
duration: 25m
verification_result: passed
completed_at: 2026-03-17
blocker_discovered: false
---

# T01: Thread marketplace through scoring engine and create migration 027

**Threaded `marketplace: str = "ID"` through the entire scoring calculator, replaced all IDR-hardcoded template locations with `{currency}` placeholder, and created migration 027 to patch DB templates.**

## What Happened

1. Added `_fmt_currency(value, marketplace)` to `helpers.py` — delegates to `_fmt_idr` (formatting identical for both currencies). Kept `_fmt_idr` for backward compatibility.

2. Updated 4 DEFAULT_RULES templates in `rules.py`: `IDR {idr_val}` → `{currency} {idr_val}`, `IDR {idr_avg}` → `{currency} {idr_avg}`, `IDR {selling_price}` → `{currency} {selling_price}`, `IDR {market_price}` → `{currency} {market_price}`.

3. Updated 4 inline default templates in `messages.py` to match. Added `marketplace` keyword param to both `_generate_business_messages` and `_generate_competition_messages`. Replaced `_fmt_idr` calls with `_fmt_currency` in currency-formatting contexts. Added `currency=currency_code` to all relevant `_format_message_template` calls and i18n vars dicts.

4. Updated `_score_competition` in `categories.py` — added `marketplace` param, benchmark now uses `MARKETPLACE_CURRENCY.get(marketplace, 'IDR')` instead of hardcoded `"IDR"`.

5. Updated `_compute_g66` and `_compute_g66_i18n` in `computations.py` — added `marketplace` param. For THB, uses raw formatted numbers instead of `/1_000_000` with `juta` scaling.

6. Updated `calculate_score()` in `_calculator.py` — added `marketplace: str = "ID"` parameter, passes it to `_score_competition`, `_generate_business_messages`, `_generate_competition_messages`, `_compute_g66`, `_compute_g66_i18n`.

7. Wired `marketplace=marketplace` to the `calculate_score()` call in `service.py` (`generate_score()` already reads marketplace from eval_inputs).

8. Created migration 027 following the 021 `_apply_patches` pattern — patches 4 message template strings from `IDR` to `{currency}` in scoring_rules JSONB, using `(template, marketplace)` compound key for the post-026 schema.

9. Updated `TestMigrationTemplatesDrift._build_effective_db_templates` in `test_scoring.py` to replay migration 027 after 021.

## Verification

- `pytest backend/tests/unit/calculators/test_scoring.py -x` → **178 passed** (all existing tests, including `TestMigrationTemplatesDrift`)
- `pytest backend/tests/unit/test_generate_score_marketplace.py -x` → **3 passed** (marketplace wiring tests)
- Full suite (excluding pre-existing ads_keyword failure): **957 passed**
- Manual check: `_fmt_currency(190_000, 'TH')` → `"190,000"` ✓
- Manual check: `_fmt_idr(100_000_000)` → `"100,000,000"` ✓ (backward compat)

### Slice-level verification status (T01 — intermediate task):
- ✅ `test_scoring.py -x` — all 178 existing tests pass
- ⬜ `test_scoring_marketplace.py -x` — file not yet created (T02)
- ✅ `test_generate_score_marketplace.py -x` — 3 tests pass
- ⚠️ Full suite: 957 passed, 1 pre-existing failure in `test_ads_keyword.py` (unrelated)

## Diagnostics

- Call `calculate_score(..., marketplace='TH')` and inspect `result.category_scores[*].rows[*].message` for `THB` presence
- If `{currency}` appears literally in output messages, it means the kwarg was not passed to `_format_message_template` — trace the call path
- Migration 027's `_apply_patches` can be called standalone: `m027._apply_patches(rules_dict, forward=True)` to verify template patching
- `TestMigrationTemplatesDrift` catches any future DB↔code template divergence

## Deviations

None. All 9 steps executed as planned.

## Known Issues

- Pre-existing test failure in `backend/tests/unit/calculators/test_ads_keyword.py::TestSheet2BottomThresholdVariants::test_en_bottom_min_cost_50k` — unrelated to scoring changes, no files in that module were modified.

## Files Created/Modified

- `backend/app/calculators/scoring/helpers.py` — added `_fmt_currency(value, marketplace)` function
- `backend/app/calculators/scoring/rules.py` — replaced IDR with {currency} in 4 DEFAULT_RULES templates
- `backend/app/calculators/scoring/messages.py` — added MARKETPLACE_CURRENCY import, _fmt_currency import, marketplace param to 2 generators, {currency} in 4 inline defaults
- `backend/app/calculators/scoring/categories.py` — added MARKETPLACE_CURRENCY import, marketplace param to _score_competition, dynamic currency in benchmark
- `backend/app/calculators/scoring/computations.py` — added marketplace param to _compute_g66 and _compute_g66_i18n, THB raw number formatting
- `backend/app/calculators/scoring/_calculator.py` — added marketplace param to calculate_score, passed to 5 sub-functions
- `backend/app/modules/evaluations/service.py` — added marketplace=marketplace to calculate_score() call
- `backend/app/db/migrations/versions/027_update_message_templates_currency_placeholder.py` — new migration patching 4 templates from IDR to {currency}
- `backend/tests/unit/calculators/test_scoring.py` — updated TestMigrationTemplatesDrift to replay migration 027
