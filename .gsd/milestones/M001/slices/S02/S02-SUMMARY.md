---
id: S02
parent: M001
milestone: M001
provides:
  - marketplace parameter threaded through calculate_score → 5 scoring sub-functions
  - _fmt_currency(value, marketplace) helper for marketplace-aware currency formatting
  - {currency} placeholder in all 8 message templates (4 DEFAULT_RULES + 4 inline defaults)
  - THB conclusion text uses raw numbers instead of /1M juta scaling
  - Migration 027 patching DB templates from hardcoded IDR to {currency}
  - Service layer wiring (generate_score → calculate_score marketplace passthrough)
  - 24 unit tests + 4 wiring tests proving THB output correctness
requires:
  - slice: S01
    provides: MARKETPLACE_CURRENCY dict, marketplace column in scoring_rules, generate_score marketplace reading from eval_inputs
affects:
  - S04
key_files:
  - backend/app/calculators/scoring/helpers.py
  - backend/app/calculators/scoring/_calculator.py
  - backend/app/calculators/scoring/messages.py
  - backend/app/calculators/scoring/categories.py
  - backend/app/calculators/scoring/computations.py
  - backend/app/calculators/scoring/rules.py
  - backend/app/modules/evaluations/service.py
  - backend/app/db/migrations/versions/027_update_message_templates_currency_placeholder.py
  - backend/tests/unit/calculators/test_scoring_marketplace.py
  - backend/tests/unit/test_generate_score_marketplace.py
key_decisions:
  - _fmt_currency delegates to _fmt_idr — formatting is identical for IDR/THB (comma thousands). Currency CODE is injected by template placeholders, not the formatting function (D007)
  - marketplace param uses keyword-only syntax with default "ID" through scoring sub-functions; MARKETPLACE_CURRENCY.get(marketplace, "IDR") for fallback (D008)
  - THB conclusion text uses raw formatted numbers; IDR uses /1_000_000 with "juta" suffix — scale-appropriate display convention (D009)
patterns_established:
  - Thread marketplace as keyword-only param with default "ID" through scoring sub-functions
  - Use MARKETPLACE_CURRENCY.get(marketplace, "IDR") for fallback-safe currency code resolution
  - Use {currency} template placeholder + currency=currency_code kwarg for message formatting
  - For THB marketplace, _compute_g66 uses raw formatted numbers instead of /1M juta scaling
  - Test marketplace at 3 levels: unit (helpers/messages), integration (categories+computations), e2e (calculate_score)
observability_surfaces:
  - calculate_score(marketplace='TH') produces messages with THB currency code — visible in ScoringResult.category_scores[*].rows[*].message
  - _SafeDict renders unresolved {currency} literally if kwarg missing — visible but non-crashing
  - TestMigrationTemplatesDrift replays 012→019→020→021→027 to catch DB↔code template divergence
  - _fmt_currency(value, marketplace) callable standalone to verify number formatting
drill_down_paths:
  - .gsd/milestones/M001/slices/S02/tasks/T01-SUMMARY.md
  - .gsd/milestones/M001/slices/S02/tasks/T02-SUMMARY.md
duration: 40m
verification_result: passed
completed_at: 2026-03-17
---

# S02: Scoring Engine Marketplace Awareness

**Threaded `marketplace` parameter through the entire scoring calculator, replaced all IDR-hardcoded template locations with `{currency}` placeholders, created migration 027 for DB template sync, and proved correctness with 28 new tests covering THB output, backward compatibility, and unknown marketplace fallback.**

## What Happened

The scoring engine had 10 locations hardcoding `IDR` — 4 DEFAULT_RULES templates, 4 inline default templates in message generators, 1 competition benchmark string, and 1 conclusion text scaler. This slice replaced all 10 with marketplace-aware behavior.

**T01 (Thread marketplace through scoring engine + migration 027):** Added `_fmt_currency(value, marketplace)` to helpers.py (delegates to `_fmt_idr` — formatting identical for both currencies). Updated all 8 message templates to use `{currency}` placeholder. Added `marketplace` keyword param to 5 scoring sub-functions: `_generate_business_messages`, `_generate_competition_messages`, `_score_competition`, `_compute_g66`, `_compute_g66_i18n`. Each function resolves the currency code via `MARKETPLACE_CURRENCY.get(marketplace, "IDR")` and passes it to template formatting. The competition benchmark now builds dynamically (`f"{currency_code} {_fmt_currency(...)}"` instead of `f"IDR {_fmt_idr(...)}"` ). Conclusion text (`_compute_g66`) branches on marketplace — THB uses raw comma-formatted numbers, IDR continues using `/1_000_000` with `juta` suffix. `calculate_score()` gained a `marketplace: str = "ID"` parameter and threads it to all 5 sub-functions. Service layer wiring in `generate_score()` passes `marketplace=marketplace` to `calculate_score()`. Migration 027 patches 4 stored message templates from `IDR` to `{currency}` using the `_apply_patches` pattern established by migration 021.

**T02 (Comprehensive THB tests):** Created 24 tests in `test_scoring_marketplace.py` across 7 test classes covering: currency formatting (6), business messages (3), competition messages (3), competition benchmarks (2), conclusion text (4), full end-to-end scoring (4), and backward compatibility (2). Added 1 wiring test in `test_generate_score_marketplace.py` verifying `generate_score` passes `marketplace` to `calculate_score`. Also fixed S01 wiring test assertions that broke because T01 changed arg passing convention from keyword to positional.

## Verification

- `pytest backend/tests/unit/calculators/test_scoring.py -x` → **178 passed** — no regression in existing scoring tests
- `pytest backend/tests/unit/calculators/test_scoring_marketplace.py -x -v` → **24 passed** — all THB-specific tests
- `pytest backend/tests/unit/test_generate_score_marketplace.py -x -v` → **4 passed** — marketplace wiring tests
- `pytest backend/tests/unit/calculators/test_scoring.py::TestMigrationTemplatesDrift -x` → **1 passed** — DB↔code template sync
- `pytest backend/tests/ -q` → **1046 passed, 3 failed** — 3 failures are pre-existing in `test_ads_keyword.py` (unrelated)
- Manual: `_fmt_currency(190_000, 'TH')` → `"190,000"` ✓
- Manual: `MARKETPLACE_CURRENCY.get('XX', 'IDR')` → `"IDR"` ✓ (fallback)

## Requirements Advanced

- SCORE-03 — Marketplace-specific values are now threaded through scoring, but threshold-level differentiation (e.g., different pass/fail cutoffs per marketplace) depends on rules data selected by S01's query layer. The scoring engine itself now fully supports it.

## Requirements Validated

- SCORE-01 — `generate_score()` reads marketplace from eval_inputs and passes it through to `calculate_score()`. Verified by 4 wiring tests including positional arg matching.
- SCORE-02 — All 8 message templates display correct currency (THB/IDR) based on marketplace. Verified by 24 unit tests covering business messages, competition messages, benchmarks, and conclusion text for both TH and ID marketplaces plus unknown marketplace fallback.

## New Requirements Surfaced

- none

## Requirements Invalidated or Re-scoped

- none

## Deviations

- **T01 code was uncommitted in worktree**: T01 executor wrote all production code changes in the `.gsd/worktrees/M001/` worktree but only documentation files were auto-committed. T02 executor had to copy 9 files from the worktree to the main repo to enable test execution. This is a known worktree divergence issue documented in KNOWLEDGE.md.
- **S01 wiring test assertions fixed**: T01 changed `get_rules_by_template_and_marketplace` from keyword to positional arg passing in service.py. Two existing S01 tests used keyword style (`marketplace="TH"`) and needed updating to positional style (`"TH"`).

## Known Limitations

- Currency formatting is identical for IDR and THB (comma thousands separator). If THB ever needs different formatting (e.g., decimal separator), `_fmt_currency` will need marketplace-specific logic instead of delegating to `_fmt_idr`.
- The `{currency}` placeholder approach means if any `_format_message_template` call path forgets to pass `currency=currency_code`, the literal `{currency}` appears in output (non-crashing via `_SafeDict`, but visually wrong). No runtime guard beyond test coverage.
- Pre-existing 3 test failures in `test_ads_keyword.py` remain unrelated to this slice.

## Follow-ups

- none

## Files Created/Modified

- `backend/app/calculators/scoring/helpers.py` — added `_fmt_currency(value, marketplace)` helper
- `backend/app/calculators/scoring/rules.py` — replaced `IDR` with `{currency}` in 4 DEFAULT_RULES templates
- `backend/app/calculators/scoring/messages.py` — added marketplace param to 2 message generators, `{currency}` in 4 inline defaults, `_fmt_currency` usage
- `backend/app/calculators/scoring/categories.py` — added marketplace param to `_score_competition`, dynamic currency in benchmark
- `backend/app/calculators/scoring/computations.py` — added marketplace param to `_compute_g66`/`_compute_g66_i18n`, THB raw number formatting
- `backend/app/calculators/scoring/_calculator.py` — added `marketplace: str = "ID"` param, threaded to 5 sub-functions
- `backend/app/modules/evaluations/service.py` — added `marketplace=marketplace` to `calculate_score()` call
- `backend/app/db/migrations/versions/027_update_message_templates_currency_placeholder.py` — new migration patching 4 templates from IDR to `{currency}`
- `backend/tests/unit/calculators/test_scoring.py` — updated TestMigrationTemplatesDrift to replay migration 027
- `backend/tests/unit/calculators/test_scoring_marketplace.py` — **created** — 24 tests covering THB marketplace scoring
- `backend/tests/unit/test_generate_score_marketplace.py` — added wiring test, fixed S01 assertion styles

## Forward Intelligence

### What the next slice should know
- `calculate_score(marketplace='TH')` is fully functional. The scoring engine correctly produces THB-labeled messages, benchmarks, and conclusion text. S03 (CSV parsing) and S04 (frontend UI) can assume the backend scoring path works for both marketplaces.
- The `marketplace` parameter defaults to `"ID"` everywhere — existing callers need zero changes. New callers just pass `marketplace='TH'`.
- Currency code resolution uses `MARKETPLACE_CURRENCY.get(marketplace, "IDR")` from `app.core.marketplace` — this is the single source of truth for marketplace→currency mapping.

### What's fragile
- **Template placeholder coverage** — if new message templates are added to DEFAULT_RULES or inline defaults, they must include `{currency}` instead of `IDR`, and their formatting calls must pass `currency=currency_code`. No compile-time enforcement; only `TestMigrationTemplatesDrift` and the marketplace tests catch this.
- **Worktree divergence** — code changes made in `.gsd/worktrees/M001/` don't automatically appear in the main repo. Future task executors should verify their code changes are in the right directory.

### Authoritative diagnostics
- `pytest backend/tests/unit/calculators/test_scoring_marketplace.py -v` — each test name encodes the exact dimension being verified. If a specific marketplace behavior breaks, this suite pinpoints which.
- `TestMigrationTemplatesDrift` in `test_scoring.py` — catches any DB template ↔ DEFAULT_RULES divergence. If a future migration or rules change breaks sync, this test fails.
- `_fmt_currency(value, marketplace)` is callable standalone for quick spot-checks.

### What assumptions changed
- **Original assumption**: `_fmt_idr` was the only formatting function needed. **What happened**: `_fmt_currency` was added but delegates to `_fmt_idr` — formatting is identical. The separation exists for semantic clarity and future extensibility.
- **Original assumption**: T01 code would be available in the main repo after T01 completed. **What happened**: worktree divergence meant T02 had to copy files manually. The KNOWLEDGE.md now documents this pattern.
