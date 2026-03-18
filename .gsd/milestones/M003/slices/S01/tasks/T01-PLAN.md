---
estimated_steps: 5
estimated_files: 4
---

# T01: Fix follower formatting, create migration 028, and add marketplace-aware ads min_cost

**Slice:** S01 — International formatting & marketplace-aware ads thresholds
**Milestone:** M003

## Description

Apply all four production code changes for the IDR cleanup slice. Three existing files get surgical edits (rules.py, messages.py, ads_keyword.py) and one new DB migration file is created. Each change is independent — they touch different files and different logic paths. The changes implement requirements R023 (follower threshold comma formatting), R024 (val_str comma separator), and R025 (marketplace-aware ads min_cost). R026 requires no code change — just verification in T02.

**Skill hint:** Load the `test` skill if you need to check existing test patterns, but this task is pure production code — no tests are written here.

## Steps

1. **Edit `backend/app/calculators/scoring/rules.py`** — In the `DEFAULT_RULES` dict, find the `"visitors"` → `"followers"` → `"message_fail"` value. It contains `>50.000`. Change it to `>50,000`. This is the only change in this file. There's a NOTE comment at lines 5-11 about keeping three sources of truth in sync — this is one of the three.

2. **Edit `backend/app/calculators/scoring/messages.py`** — Two changes in `_generate_visitors_messages`:
   - Find the line where `val_str` is computed for row 29 (followers). It reads `val_str = f"{int(row.value):,}".replace(",", ".")`. Remove the `.replace(",", ".")` call so it becomes `val_str = f"{int(row.value):,}"`. Python's `:,` format already produces comma-separated output which is what we want.
   - Find the inline fallback string for row 29 fail that contains `>50.000`. Change it to `>50,000`. This is the fail default message string — look for `"❌ Total Pengikut = {val_str} [Kurang Baik, nilai disarankan: >50.000]"` and change `>50.000` to `>50,000`.

3. **Edit `backend/app/calculators/ads_keyword.py`** — In the `calculate_sheet2` function, find `min_cost = 100000` (approximately line 497). Replace it with marketplace-aware branching:
   ```python
   min_cost = 100000 if marketplace != "TH" else 190
   ```
   The function already receives a `marketplace` parameter. Both the primary and fallback bottom queries that use `min_cost` will automatically pick up the new value since they reference the same variable. Do NOT import anything from `marketplace.py` — the value 190 is hardcoded per D029.

4. **Create `backend/app/db/migrations/versions/028_fix_follower_threshold_comma_separator.py`** — Follow the exact `_apply_patches` pattern from migration 027. The migration must:
   - Set `revision = "028"` and `down_revision = "027"`
   - Define a `PATCHES` list with one entry: `["visitors", "followers", "message_fail", ">50.000", ">50,000"]` (path segments + old value + new value, matching the pattern in migration 027)
   - Implement `_apply_patches(rules: dict, forward: bool = True)` that iterates PATCHES and replaces old↔new values
   - Implement `upgrade()` and `downgrade()` that load templates from DB, call `_apply_patches`, and write back
   - **Critical:** The `_apply_patches` function must be importable directly from the module — the drift test imports it as `m028._apply_patches(db, forward=True)`
   
   **Reference:** Read migration 027 (`backend/app/db/migrations/versions/027_update_message_templates_currency_placeholder.py`) as the pattern to copy. Adapt it for this single-patch case.

5. **Verify all imports work:**
   ```bash
   cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M003
   PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -c "
   from app.calculators.scoring import rules, messages
   from app.calculators import ads_keyword
   print('Production imports OK')
   # Verify rules change
   fr = rules.DEFAULT_RULES['visitors']['followers']['message_fail']
   assert '>50,000' in fr, f'Expected >50,000 in rules, got: {fr}'
   assert '>50.000' not in fr, f'Old >50.000 still in rules'
   print('Rules check OK')
   "
   ```

## Must-Haves

- [ ] `DEFAULT_RULES["visitors"]["followers"]["message_fail"]` contains `>50,000` (comma), not `>50.000` (dot)
- [ ] `messages.py` val_str line has no `.replace(",", ".")` call
- [ ] `messages.py` inline fallback uses `>50,000` not `>50.000`
- [ ] `ads_keyword.py` `min_cost` is 190 when marketplace is "TH", 100000 otherwise
- [ ] Migration 028 exists with `_apply_patches` function that patches `>50.000` → `>50,000`
- [ ] Migration 028 `down_revision` is `"027"`
- [ ] All production Python files import without errors

## Verification

- Run the import verification script from Step 5 — prints "Production imports OK" and "Rules check OK"
- Confirm migration 028 file exists and contains `_apply_patches` function
- Note: The drift test (`test_db_templates_match_default_rules`) will fail after this task because the replay chain doesn't include m028 yet — this is expected and correct (red state). T02 fixes it.

## Observability Impact

- **Migration 028 `_apply_patches`**: Returns `bool` indicating whether any change was made — callers (drift test replay chain) can assert on this to detect no-op vs actual patch application
- **`min_cost` branching**: No logging added — the value is deterministic from the `marketplace` parameter. Testable by inspecting `bottom_ads` filter output: TH marketplace will include lower-cost ads (>190 THB) that would be excluded under the ID threshold (>100,000 IDR)
- **Failure state**: If `>50.000` persists in any of the three sources of truth (DB, DEFAULT_RULES, inline fallbacks), the drift test and the new formatting tests in T02 will surface mismatches with exact key paths and expected values

## Inputs

- `backend/app/db/migrations/versions/027_update_message_templates_currency_placeholder.py` — Pattern template for creating migration 028. Read this file to understand the `_apply_patches` structure.
- `backend/app/calculators/scoring/rules.py` — Contains `DEFAULT_RULES` with the `>50.000` string to fix
- `backend/app/calculators/scoring/messages.py` — Contains val_str formatting and inline fallback to fix
- `backend/app/calculators/ads_keyword.py` — Contains `min_cost = 100000` to make marketplace-aware

## Expected Output

- `backend/app/calculators/scoring/rules.py` — `>50.000` replaced with `>50,000` in DEFAULT_RULES
- `backend/app/calculators/scoring/messages.py` — `.replace(",", ".")` removed; inline fallback changed to `>50,000`
- `backend/app/calculators/ads_keyword.py` — `min_cost` branched by marketplace (100000 / 190)
- `backend/app/db/migrations/versions/028_fix_follower_threshold_comma_separator.py` — New migration file with `_apply_patches` function
