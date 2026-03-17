---
estimated_steps: 9
estimated_files: 8
---

# T01: Thread marketplace through scoring engine and create migration 027

**Slice:** S02 — Scoring Engine Marketplace Awareness
**Milestone:** M001

## Description

Thread a `marketplace: str = "ID"` parameter through the entire pure scoring calculator, replacing all 10 IDR-hardcoded locations with marketplace-aware currency formatting. This is atomic — all template updates, function signature changes, and the DB migration must land together so the `TestMigrationTemplatesDrift` test continues to pass.

**Relevant skill:** `test` (for running existing test suite to verify no regression)

**Key import from S01:** `from app.core.marketplace import MARKETPLACE_CURRENCY` — this maps `'ID' → 'IDR'`, `'TH' → 'THB'`.

## Steps

1. **Add `_fmt_currency` helper to `backend/app/calculators/scoring/helpers.py`:**
   - Add import: `from app.core.marketplace import MARKETPLACE_CURRENCY`
   - Add function after `_fmt_idr`:
     ```python
     def _fmt_currency(value: float, marketplace: str = "ID") -> str:
         """Format a currency value with comma thousands separator.
         
         Returns the formatted number only (no currency prefix).
         The currency code is injected via message template placeholders.
         """
         return _fmt_idr(value)
     ```
   - Note: `_fmt_currency` delegates to `_fmt_idr` — the formatting is identical for both marketplaces (comma thousands). The currency *code* (IDR/THB) is handled by template placeholders, not by this function.
   - Keep `_fmt_idr` as-is for backward compatibility (other files may import it).

2. **Update 4 DEFAULT_RULES templates in `backend/app/calculators/scoring/rules.py`:**
   - Line ~45 `message_pass`: `"✔️ Penjualan = IDR {idr_val} [Meningkat..."` → `"✔️ Penjualan = {currency} {idr_val} [Meningkat {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: {currency} {idr_avg}]"`
   - Line ~46 `message_fail`: `"❌ Penjualan = IDR {idr_val} [Menurun..."` → `"❌ Penjualan = {currency} {idr_val} [Menurun {change_pct}% dibandingkan dengan rata² 6 bulan terakhir: {currency} {idr_avg}]"`
   - Line ~147 `message_pass`: `"{name} (IDR {selling_price}) = ✅[kompetitif]"` → `"{name} ({currency} {selling_price}) = ✅[kompetitif]"`
   - Line ~148 `message_fail`: `"{name} (IDR {selling_price}) = ❌[tidak kompetitif (harga kisaran pasaran: IDR {market_price})]"` → `"{name} ({currency} {selling_price}) = ❌[tidak kompetitif (harga kisaran pasaran: {currency} {market_price})]"`

3. **Update 4 inline default templates in `backend/app/calculators/scoring/messages.py`:**
   - Add imports: `from app.core.marketplace import MARKETPLACE_CURRENCY` and `from .helpers import _fmt_currency` (keep `_fmt_idr` import for other uses)
   - Line ~97 business pass inline default: replace `"IDR {idr_val}"` and `"IDR {idr_avg}"` with `"{currency} {idr_val}"` and `"{currency} {idr_avg}"`
   - Line ~105 business fail inline default: same replacement
   - Line ~478 competition fail inline default: replace `"IDR {selling_price}"` and `"IDR {market_price}"` with `"{currency} {selling_price}"` and `"{currency} {market_price}"`
   - Line ~497 competition pass inline default: replace `"IDR {selling_price}"` with `"{currency} {selling_price}"`
   - Add `marketplace: str = "ID"` parameter to `_generate_business_messages()` signature
   - In row 13 processing: add `currency_code = MARKETPLACE_CURRENCY.get(marketplace, "IDR")` at the top, replace `_fmt_idr(current)` → `_fmt_currency(current, marketplace)`, `_fmt_idr(avg_6mo)` → `_fmt_currency(avg_6mo, marketplace)`, and pass `currency=currency_code` to ALL `_format_message_template` calls in this function (both pass and fail branches for row 13)
   - Add `marketplace: str = "ID"` parameter to `_generate_competition_messages()` signature
   - In the competition function: add `currency_code = MARKETPLACE_CURRENCY.get(marketplace, "IDR")`, replace ALL `_fmt_idr(selling_price)` → `_fmt_currency(selling_price, marketplace)`, `_fmt_idr(market_price)` → `_fmt_currency(market_price, marketplace)`, and pass `currency=currency_code` to ALL `_format_message_template` calls. Also update the i18n `vars` dicts to use `_fmt_currency` instead of `_fmt_idr`.

4. **Update `_score_competition` in `backend/app/calculators/scoring/categories.py`:**
   - Add import: `from app.core.marketplace import MARKETPLACE_CURRENCY`
   - Add `marketplace: str = "ID"` parameter to `_score_competition()` signature
   - Replace line ~531: `benchmark=f"IDR {_fmt_idr(market_price)}" if market_price > 0 else "-"` → `benchmark=f"{MARKETPLACE_CURRENCY.get(marketplace, 'IDR')} {_fmt_idr(market_price)}" if market_price > 0 else "-"`

5. **Update `_compute_g66` and `_compute_g66_i18n` in `backend/app/calculators/scoring/computations.py`:**
   - Add `marketplace: str = "ID"` parameter to both functions
   - In `_compute_g66`: change the sales range block:
     ```python
     if valid_sales:
         if marketplace == "TH":
             min_s = f"{min(valid_sales):,.0f}"
             max_s = f"{max(valid_sales):,.0f}"
             lines.append(
                 f"- Omset toko di kisaran {min_s} - {max_s} "
                 f"per bulan sejak 6 bulan terakhir"
             )
         else:
             min_sales = min(valid_sales) / 1_000_000
             max_sales = max(valid_sales) / 1_000_000
             lines.append(
                 f"- Omset toko di kisaran {min_sales:.0f} juta - {max_sales:.0f} juta "
                 f"per bulan sejak 6 bulan terakhir"
             )
     ```
   - In `_compute_g66_i18n`: same marketplace-aware logic for the `conclusion.salesRange` vars — for THB use raw formatted numbers, for IDR use `/ 1_000_000` scaling

6. **Add `marketplace` param to `calculate_score()` in `backend/app/calculators/scoring/_calculator.py`:**
   - Add `marketplace: str = "ID"` to the function signature (after `rule_version`)
   - Pass `marketplace=marketplace` to `_score_competition(manual_data, calculator_results, marketplace=marketplace)` (line ~95)
   - Pass `marketplace=marketplace` to `_generate_business_messages(cat_business, manual_data, rules, marketplace=marketplace)` (line ~118)
   - Pass `marketplace=marketplace` to `_generate_competition_messages(cat_competition, manual_data, rules, marketplace=marketplace)` (line ~124)
   - Pass `marketplace=marketplace` to `_compute_g66(all_categories, manual_data, g68, marketplace=marketplace)` (line ~139)
   - Pass `marketplace=marketplace` to `_compute_g66_i18n(all_categories, manual_data, g68, marketplace=marketplace)` (line ~143)

7. **Wire `marketplace` from `generate_score()` to `calculate_score()` in `backend/app/modules/evaluations/service.py`:**
   - Around line ~358 where `calculate_score(...)` is called, add `marketplace=marketplace` to the kwargs. The `marketplace` variable already exists at line ~340 (`marketplace = (eval_inputs or {}).get("marketplace", "ID")`).

8. **Create migration 027: `backend/app/db/migrations/versions/027_update_message_templates_currency_placeholder.py`:**
   - Follow the same `_apply_patches` pattern used in migration 021
   - Revision: generate a proper alembic revision ID (use `from alembic import op` and standard boilerplate)
   - Down_revision: the revision ID from migration 026 (read it from the 026 file)
   - PATCHES list — 4 entries, each replacing `IDR` with `{currency}` in the template string:
     - `(["business", "monthly_sales_trend", "message_pass"], old_pass, new_pass)` — replace all `IDR ` with `{currency} `
     - `(["business", "monthly_sales_trend", "message_fail"], old_fail, new_fail)` — same
     - `(["competition", "message_pass"], old_comp_pass, new_comp_pass)` — same
     - `(["competition", "message_fail"], old_comp_fail, new_comp_fail)` — same
   - The upgrade function: for each scoring_rules row, load `rules` JSONB, apply patches (replace `IDR` with `{currency}` in the 4 template fields), write back
   - The downgrade function: reverse (replace `{currency}` with `IDR`)
   - **Critical:** Read the revision ID from 026 to set `down_revision` correctly

9. **Run existing test suite to verify no regression:**
   - `backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py -x`
   - If the drift test (`TestMigrationTemplatesDrift`) fails, check that migration 027 patches are correctly applied in `_build_effective_db_templates`. The test replays migrations 012 → 019 → 020 → 021. You must add 027 to the replay chain.
   - Fix any failures in the existing tests. Common issues: (a) `_generate_business_messages` now requires `marketplace` kwarg — but it defaults to `"ID"` so existing callers should be fine; (b) drift test needs to import and apply migration 027 patches.

## Must-Haves

- [ ] `_fmt_currency(value, marketplace)` exists in helpers.py and returns comma-formatted number
- [ ] `_fmt_idr` still exists and works (backward compat)
- [ ] All 4 DEFAULT_RULES templates use `{currency}` instead of `IDR`
- [ ] All 4 inline default templates in messages.py use `{currency}` instead of `IDR`
- [ ] `_generate_business_messages` accepts and uses `marketplace` param
- [ ] `_generate_competition_messages` accepts and uses `marketplace` param
- [ ] `_score_competition` accepts `marketplace` and uses correct currency code in benchmark
- [ ] `_compute_g66` and `_compute_g66_i18n` accept `marketplace` and handle THB scaling (no `juta`)
- [ ] `calculate_score()` accepts `marketplace: str = "ID"` and passes it to all sub-functions
- [ ] `generate_score()` passes `marketplace` to `calculate_score()`
- [ ] Migration 027 patches DB templates from `IDR` to `{currency}`
- [ ] All existing scoring tests pass (including `TestMigrationTemplatesDrift`)

## Verification

- `backend/.venv/bin/python -m pytest backend/tests/unit/calculators/test_scoring.py -x` — all existing tests pass
- `backend/.venv/bin/python -m pytest backend/tests/unit/test_generate_score_marketplace.py -x` — marketplace wiring tests pass
- Quick manual check: `python -c "from app.calculators.scoring.helpers import _fmt_currency; print(_fmt_currency(190_000, 'TH'))"` → `"190,000"`

## Inputs

- `backend/app/core/marketplace.py` — provides `MARKETPLACE_CURRENCY` dict (`{'ID': 'IDR', 'TH': 'THB'}`)
- `backend/app/db/migrations/versions/026_add_marketplace_to_schema.py` — need its revision ID for migration 027's `down_revision`
- S01 summary — `generate_score()` already reads `marketplace` from eval_inputs at line ~340

## Expected Output

- `backend/app/calculators/scoring/helpers.py` — `_fmt_currency` function added
- `backend/app/calculators/scoring/rules.py` — 4 DEFAULT_RULES templates updated
- `backend/app/calculators/scoring/messages.py` — 4 inline defaults updated, `marketplace` param added to 2 generator functions, `_fmt_idr` → `_fmt_currency` in currency-formatting calls
- `backend/app/calculators/scoring/categories.py` — `_score_competition` accepts `marketplace`, benchmark uses dynamic currency code
- `backend/app/calculators/scoring/computations.py` — `_compute_g66` and `_compute_g66_i18n` accept `marketplace`, THB uses raw numbers instead of juta scaling
- `backend/app/calculators/scoring/_calculator.py` — `calculate_score` accepts `marketplace`, passes to 5 sub-functions
- `backend/app/modules/evaluations/service.py` — `marketplace=marketplace` added to `calculate_score()` call
- `backend/app/db/migrations/versions/027_update_message_templates_currency_placeholder.py` — migration patching 4 message templates from `IDR` to `{currency}`
