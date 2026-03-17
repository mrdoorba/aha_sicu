# S02: Scoring Engine Marketplace Awareness — Research

**Date:** 2026-03-17
**Depth:** Targeted — known codebase, known patterns, moderate complexity from multi-location sync

## Summary

S02 threads `marketplace` through the pure scoring calculator so that message templates, currency formatting, and benchmark labels all reflect the correct marketplace. S01 already wired `generate_score()` to fetch the correct rules row by marketplace — the scoring engine receives the right *thresholds* but still formats all output as IDR regardless of marketplace.

The work is mechanical but spread across 5 files in `calculators/scoring/`, with a three-location message template sync requirement that must be handled atomically. The core change is: `calculate_score()` accepts a new `marketplace` parameter (defaulting to `'ID'`), passes it to message generators and category scoring functions, and those functions use `_fmt_currency(value, marketplace)` instead of `_fmt_idr(value)` plus inject a `{currency}` code into template strings where `IDR` is hardcoded.

There are exactly **10 IDR-specific locations** in the scoring module:
- `rules.py` DEFAULT_RULES: 4 message templates with hardcoded `IDR` (business pass/fail, competition pass/fail)
- `messages.py` inline defaults: 4 matching templates (same strings as above)
- `categories.py` line 531: benchmark string `f"IDR {_fmt_idr(market_price)}"`
- `computations.py` line 161: conclusion text with `juta` (millions — IDR-specific unit)

All other message templates are currency-agnostic (percentages, counts, ratios).

## Recommendation

**Add `marketplace: str = "ID"` parameter to `calculate_score()`**, threading it through to:
1. `_fmt_currency(value, marketplace)` — new helper replacing `_fmt_idr()`, using `MARKETPLACE_CURRENCY` from `app.core.marketplace`
2. Message generator functions — `_generate_business_messages`, `_generate_competition_messages` receive `marketplace` and inject the correct currency code
3. `_score_competition` — benchmark string uses currency code instead of hardcoded `IDR`
4. `_compute_g66` — conclusion text uses currency-appropriate unit scaling
5. `DEFAULT_RULES` templates — replace `IDR {idr_val}` with `{currency} {idr_val}` in the 4 affected templates
6. `messages.py` inline defaults — same 4 templates updated to match

The `generate_score()` service function (S01 output) already reads `marketplace` from `eval_inputs`. The only missing link is passing it to `calculate_score()`. This is a one-line change in `evaluations/service.py`.

**Do NOT create a DB migration for message templates.** The DB-stored templates are the source of truth for existing ID evaluations, and `_SafeDict` in `_format_message_template` already handles missing keys gracefully — if a template contains `IDR` literally, it stays as `IDR` (correct for ID marketplace). New `{currency}` placeholders in DEFAULT_RULES only apply when rules are loaded fresh or updated by admins.

## Implementation Landscape

### Key Files

- `backend/app/calculators/scoring/helpers.py` — Add `_fmt_currency(value, marketplace)` wrapping `_fmt_idr()` with currency code prefix. Keep `_fmt_idr()` as-is for backward compat.
- `backend/app/calculators/scoring/_calculator.py` — Add `marketplace: str = "ID"` param to `calculate_score()`. Pass it to message generators and `_score_competition`.
- `backend/app/calculators/scoring/messages.py` — Add `marketplace` param to `_generate_business_messages()` and `_generate_competition_messages()`. Replace `_fmt_idr` calls with `_fmt_currency` calls. Update 4 inline default templates to use `{currency}` placeholder.
- `backend/app/calculators/scoring/categories.py` — Add `marketplace` param to `_score_competition()`. Replace benchmark `f"IDR {_fmt_idr(market_price)}"` with `f"{currency_code} {_fmt_currency(...)}"`.
- `backend/app/calculators/scoring/rules.py` — Update 4 `DEFAULT_RULES` message templates: `"IDR {idr_val}"` → `"{currency} {idr_val}"`, `"IDR {selling_price}"` → `"{currency} {selling_price}"`, `"IDR {market_price}"` → `"{currency} {market_price}"`, `"IDR {idr_avg}"` → `"{currency} {idr_avg}"`.
- `backend/app/calculators/scoring/computations.py` — Add `marketplace` param to `_compute_g66()` and `_compute_g66_i18n()`. Change `juta` (millions) label to handle THB scale (THB values are ~500x smaller than IDR; the `/ 1_000_000` scaling with `juta` label is IDR-specific).
- `backend/app/calculators/scoring/__init__.py` — No change needed (re-exports stay the same).
- `backend/app/modules/evaluations/service.py` — Pass `marketplace=marketplace` to `calculate_score()` call (one-line addition around line 358).
- `backend/tests/unit/calculators/test_scoring.py` — Extend `TestMigrationTemplatesDrift` and `test_default_rules_produce_identical_messages` to cover THB marketplace. Add new tests for `_fmt_currency`, competition benchmark with THB, business messages with THB.
- `backend/tests/unit/test_generate_score_marketplace.py` — Verify `calculate_score` receives `marketplace` param.

### Build Order

**Task 1: Currency formatting helper + DEFAULT_RULES templates** (foundation)
- Add `_fmt_currency(value, marketplace)` to `helpers.py`
- Update 4 templates in `DEFAULT_RULES` (`rules.py`) with `{currency}` placeholder
- Unit tests for `_fmt_currency` with both ID and TH
- This unblocks all message generator changes

**Task 2: Thread marketplace through calculator and messages** (core logic)
- Add `marketplace` param to `calculate_score()` in `_calculator.py`
- Add `marketplace` param to `_generate_business_messages()`, `_generate_competition_messages()` in `messages.py`
- Update inline default templates in `messages.py` (4 locations)
- Add `marketplace` param to `_score_competition()` in `categories.py`
- Update `_compute_g66()` and `_compute_g66_i18n()` in `computations.py`
- Pass `marketplace` from `generate_score()` in `evaluations/service.py`
- Update `__init__.py` exports if any new public names added
- Comprehensive tests: THB business messages, THB competition messages, THB conclusion text

**Why this order:** Task 1 is independent and can be verified in isolation. Task 2 depends on Task 1's `_fmt_currency` helper and updated DEFAULT_RULES.

### Verification Approach

1. `backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py -x` — all 178 existing tests pass (no regression)
2. `backend/.venv/bin/python -m pytest backend/tests/unit/test_generate_score_marketplace.py -x` — marketplace wiring tests pass
3. New tests verify:
   - `_fmt_currency(100_000_000, "ID")` returns `"100,000,000"` (no prefix in raw formatter)
   - `_fmt_currency(190_000, "TH")` returns `"190,000"` (same formatting, different scale)
   - THB business messages contain `"THB"` not `"IDR"` 
   - THB competition messages contain `"THB"` not `"IDR"`
   - THB conclusion text uses appropriate scaling (not `juta`)
   - `TestMigrationTemplatesDrift` still passes (DEFAULT_RULES templates match DB)
   - `test_default_rules_produce_identical_messages` still passes for `marketplace='ID'`
4. `backend/.venv/bin/python -m pytest backend/tests/ -x --timeout=60` — full test suite passes

## Constraints

- **Three-location sync is mandatory:** `DEFAULT_RULES` (rules.py), inline defaults (messages.py), and DB migration templates must all agree on message format. The `TestMigrationTemplatesDrift` test is the gate. Since we're changing DEFAULT_RULES and inline defaults but NOT DB-stored templates, the test may break — we need to either: (a) create a migration that patches DB templates to use `{currency}` placeholder, or (b) ensure the test handles the case where DB templates use literal `IDR` and code uses `{currency}`. Option (b) is safer — DB templates with literal `IDR` are correct for existing ID rules.
- **`_SafeDict` makes `{currency}` safe for old DB templates.** If a DB-stored template contains literal `IDR` (no `{currency}` placeholder), `_format_message_template` returns it as-is. If it contains `{currency}`, the `_SafeDict.__missing__` returns `{currency}` literally if no `currency` kwarg is passed. This means the transition is backward-safe.
- **`calculate_score()` is a pure function — no DB I/O.** The marketplace parameter must be passed in from the service layer, not looked up internally.
- **Existing callers must not break.** `marketplace` param must default to `'ID'` everywhere.

## Common Pitfalls

- **Updating DEFAULT_RULES but not messages.py inline defaults** — `test_default_rules_produce_identical_messages` will catch this, but only if run. Both files must be updated atomically.
- **Forgetting to pass `currency` kwarg to `_format_message_template`** — templates with `{currency}` would render as literal `{currency}` thanks to `_SafeDict`, which looks like a bug in output but doesn't crash. Tests must assert the formatted output contains the expected currency code.
- **The `juta` scaling in `_compute_g66`** — `min_sales / 1_000_000` with `juta` label is IDR-specific. THB values at 190K scale divided by 1M gives `0 juta`. Either skip the `juta` label for THB or use appropriate scale factor. THB amounts are typically in hundreds of thousands, not hundreds of millions.
- **`_score_competition` benchmark string** — hardcodes `f"IDR {_fmt_idr(market_price)}"` at line 531 in categories.py. This is the E-column benchmark (not a message template), so it's not covered by the migration drift test. Must be updated manually.
