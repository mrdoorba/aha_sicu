# Story 5.4: Marketing Floor Rules Migration

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system owner**,
I want the marketing floor thresholds (0.15 fashion / 0.12 non-fashion) and related marketing calculation constants to be stored in the scoring rules database and configurable through the Rules page,
so that I can adjust marketing percentage recommendations without requiring code changes.

## Acceptance Criteria

1. **AC1: Marketing category added to rules JSONB schema**
   - Given the scoring_rules table exists with Fashion and Non-Fashion templates
   - When the migration runs
   - Then each template's rules JSONB contains a new `"marketing"` category with keys: `floor`, `base_subtraction`, `upper_limit_base`, `fashion_adjustment`, `minimum_threshold`, `display_max`, `display_min` — each wrapped as `{"value": <number>}` per the established rules JSONB convention
   - And the Fashion template has `floor: 0.15`, `fashion_adjustment: 0.05`
   - And the Non-Fashion template has `floor: 0.12`, `fashion_adjustment: 0.0`
   - And both share: `base_subtraction: 0.03`, `upper_limit_base: 0.20`, `minimum_threshold: 0.10`, `display_max: 0.25`, `display_min: 0.10`

2. **AC2: Seed data migration adds marketing defaults**
   - Given both Fashion and Non-Fashion template rows exist
   - When migration 011 runs
   - Then Fashion template has marketing category with `floor: 0.15`, `upper_limit_base: 0.20`, `fashion_adjustment: 0.05`, `base_subtraction: 0.03`, `minimum_threshold: 0.10`, `display_max: 0.25`, `display_min: 0.10`
   - And Non-Fashion template has marketing category with `floor: 0.12`, `upper_limit_base: 0.20`, `fashion_adjustment: 0.0`, `base_subtraction: 0.03`, `minimum_threshold: 0.10`, `display_max: 0.25`, `display_min: 0.10`
   - And the version is incremented for both templates

3. **AC3: `_compute_g72()` reads from rules with fallback defaults**
   - Given rules are passed to the scoring calculator
   - When `_compute_g72()` executes
   - Then all 6 hardcoded constants (0.15/0.12, 0.03, 0.20, 0.05, 0.10) are read from `rules["marketing"]` using `_get_rule_value()` with the current hardcoded values as fallback defaults
   - And when rules is None, behavior is identical to current implementation

4. **AC4: `_compute_g73()` reads display bounds from rules**
   - Given rules are passed to the scoring calculator
   - When `_compute_g73()` formats the marketing percentage display
   - Then `display_max` (0.25) and `display_min` (0.10) are read from `rules["marketing"]` with fallback defaults
   - And display output is identical when using default values

5. **AC5: Rules page displays marketing category**
   - Given the user navigates to the Rules page
   - When the page loads
   - Then the marketing category appears in the category list with all configurable fields
   - And each field shows its current value with appropriate labels
   - And the category respects the existing edit/save/password-confirm flow

6. **AC6: All existing tests pass unchanged**
   - Given the refactoring uses fallback-first pattern (rules: dict | None = None)
   - When the full test suite runs
   - Then all 855+ existing tests pass without modification
   - And new tests verify rules-based behavior for marketing calculations

7. **AC7: New tests cover marketing rules**
   - Given the marketing category is configurable
   - When tests run
   - Then unit tests verify `_compute_g72()` reads each constant from rules
   - And unit tests verify fallback to defaults when rules is None
   - And unit tests verify fallback to defaults when marketing category is missing
   - And integration tests verify end-to-end scoring with custom marketing rules

## Tasks / Subtasks

- [x] Task 1: Create migration 011 to add marketing category to rules JSONB (AC: #1, #2)
  - [x] 1.1 Add `marketing` category to Fashion template defaults dict
  - [x] 1.2 Add `marketing` category to Non-Fashion template defaults dict (note: `fashion_adjustment: 0.0`, `floor: 0.12`)
  - [x] 1.3 Write migration that updates existing rows' JSONB to include marketing category
  - [x] 1.4 Increment version for both templates
  - [x] 1.5 Write downgrade that removes marketing category from JSONB

- [x] Task 2: Refactor `_compute_g72()` to use rules (AC: #3)
  - [x] 2.1 Add `marketing_rules = _get_rule_category(rules, "marketing")` at function start
  - [x] 2.2 Replace `0.15` / `0.12` floor with `_get_rule_value(marketing_rules, "floor", "threshold", 0.15 if is_fashion else 0.12)` — **BUT** note: floor differs by template, so the correct approach is to use template-specific defaults from the rules row, with a single `floor` key per template
  - [x] 2.3 Replace `0.03` with `_get_rule_value(marketing_rules, "base_subtraction", "value", 0.03)`
  - [x] 2.4 Replace `0.20` with `_get_rule_value(marketing_rules, "upper_limit_base", "value", 0.20)`
  - [x] 2.5 Replace `0.05` with `_get_rule_value(marketing_rules, "fashion_adjustment", "value", 0.05 if is_fashion else 0.0)` — same note: use template-specific value
  - [x] 2.6 Replace `0.10` minimum with `_get_rule_value(marketing_rules, "minimum_threshold", "value", 0.10)`
  - [x] 2.7 Verify the final `max(max(min_val, minimum), floor)` logic is preserved

- [x] Task 3: Refactor `_compute_g73()` to use rules (AC: #4)
  - [x] 3.1 Read `display_max` and `display_min` from marketing rules with fallback defaults
  - [x] 3.2 Replace hardcoded 0.25 and 0.10 clamping values

- [x] Task 4: Update frontend Rules page to display marketing category (AC: #5)
  - [x] 4.1 Add `"marketing"` to `CATEGORY_ORDER` array in `RulesPage.tsx`
  - [x] 4.2 Add display labels for marketing rule keys in `RulesCategoryCard.tsx` (`CATEGORY_LABELS` and `RULE_LABELS`)
  - [x] 4.3 Verify `RulesCategoryCard` correctly renders marketing fields (threshold/value types)
  - [x] 4.4 Add `"floor"` to `DIFFERING_KEYS` Set if Fashion/Non-Fashion values differ

- [x] Task 5: Add backend unit tests for marketing rules (AC: #6, #7)
  - [x] 5.1 Test `_compute_g72()` with custom marketing rules (all constants overridden)
  - [x] 5.2 Test `_compute_g72()` with `rules=None` (fallback path)
  - [x] 5.3 Test `_compute_g72()` with rules missing marketing category
  - [x] 5.4 Test `_compute_g73()` with custom display bounds
  - [x] 5.5 Test `_compute_g73()` with fallback defaults

- [x] Task 6: Add integration tests (AC: #7)
  - [x] 6.1 Test full `calculate_score()` with custom marketing rules
  - [x] 6.2 Verify marketing changes propagate to G72, G73, and email body

- [x] Task 7: Add frontend test for marketing category display (AC: #5)
  - [x] 7.1 Test RulesPage renders marketing category card
  - [x] 7.2 Test marketing fields are editable in edit mode

## Dev Notes

### Core Refactoring Strategy
Follow the **fallback-first pattern** established in Story 5.3: `rules: dict | None = None` with hardcoded defaults as fallback. This ensures zero risk of breaking existing behavior.

### Rules JSONB Structure — Marketing Category
The marketing category uses a slightly different structure than other categories because it contains standalone configuration values rather than threshold/points pairs:

```json
{
  "marketing": {
    "floor": {"value": 0.15},
    "base_subtraction": {"value": 0.03},
    "upper_limit_base": {"value": 0.20},
    "fashion_adjustment": {"value": 0.05},
    "minimum_threshold": {"value": 0.10},
    "display_max": {"value": 0.25},
    "display_min": {"value": 0.10}
  }
}
```

**Key design decision:** `floor` and `fashion_adjustment` differ between Fashion (0.15 / 0.05) and Non-Fashion (0.12 / 0.0) templates. Since each template has its own rules row in the database, the values are stored per-template. The `is_fashion` parameter in `_compute_g72()` is no longer needed for these values — the correct floor/adjustment comes from the rules row for the selected template.

### Helper Pattern
Use the established `_get_rule_category()` + `_get_rule_value()` pattern:
```python
mkt_rules = _get_rule_category(rules, "marketing")
floor = _get_rule_value(mkt_rules, "floor", "value", 0.15)  # Fashion default
```

### Files to Modify

**Backend:**
- `backend/app/db/migrations/versions/` — New migration 011
- `backend/app/calculators/scoring.py` — `_compute_g72()` (lines ~1176-1203), `_compute_g73()` (line ~1217)

**Frontend:**
- `frontend/src/pages/RulesPage.tsx` — Add "marketing" to `CATEGORY_ORDER` (line ~16), potentially `DIFFERING_KEYS` (line ~29)
- `frontend/src/components/rules/RulesCategoryCard.tsx` — Add labels for marketing fields (lines ~19-30)

**Tests:**
- `backend/tests/unit/test_scoring_*.py` — New marketing rules tests
- `backend/tests/integration/test_scoring_*.py` — Integration tests with marketing rules
- `frontend/src/pages/__tests__/` or `frontend/src/components/rules/__tests__/` — Frontend marketing tests

### Previous Story Intelligence (from 5-3)
- Story 5.3 successfully refactored all 10 scoring categories to use DB rules with fallback defaults
- The `_get_rule_category()` / `_get_rule_value()` pattern was established and is consistent across all categories
- Dynamic E-column benchmarks were added as a bonus — consider whether marketing benchmarks should also be dynamic
- 121 tests passed after 5.3 (102 unit + 11 integration + 8 frontend)

### Git Intelligence (recent commits)
- `21a0e63`: Applied code review fixes including dynamic benchmarks and additional tests
- `e484d0c`: Added frontend test for dynamic rule_version in save payload
- Pattern: code review fixes are separate commits, tests accompany feature work

### Lessons Learned Relevant to This Story
- **Percentage values stored as fractions** (0.15 not 15%) — marketing floor is already in fraction form, maintain this
- **Type precision matters** — use `float` for marketing values, `Literal` types where applicable
- **File list gaps in story specs** — this story explicitly lists all files to modify
- **Lightweight dev self-check** — verify AC coverage and error handling before marking done

### Project Structure Notes

- Alignment with unified project structure: migration numbering follows sequential pattern (010 → 011)
- Rules JSONB schema extension follows established category pattern
- Frontend component reuse: `RulesCategoryCard` already handles various field types

### References

- [Source: backend/app/calculators/scoring.py#_compute_g72 — lines 1176-1203]
- [Source: backend/app/calculators/scoring.py#_compute_g73 — line 1217]
- [Source: backend/app/calculators/scoring.py#_get_rule_category — lines 161-165]
- [Source: backend/app/calculators/scoring.py#_get_rule_value — lines 168-170]
- [Source: backend/app/db/migrations/versions/010_create_scoring_rules_table.py — JSONB schema]
- [Source: frontend/src/pages/RulesPage.tsx#CATEGORY_ORDER — line 16]
- [Source: frontend/src/components/rules/RulesCategoryCard.tsx — lines 19-30]
- [Source: _bmad-output/implementation-artifacts/epic-5-retro-2026-02-12.md#D1]
- [Source: _bmad-output/lessons-learned.md]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

No blocking issues encountered during implementation.

### Completion Notes List

- Migration 011 created using `jsonb_set()` to add marketing category to existing scoring_rules rows, with version increment. Downgrade removes category using `rules - 'marketing'`.
- `DEFAULT_FASHION_RULES` and `DEFAULT_NON_FASHION_RULES` in scoring.py updated with marketing category for fallback path.
- `_compute_g72()` refactored: all 5 hardcoded constants (floor, base_subtraction, upper_limit_base, fashion_adjustment, minimum_threshold) now read from `rules["marketing"]` via `_get_rule_value()` with is_fashion-aware defaults as fallback.
- `_compute_g73()` refactored: `display_max` and `display_min` now read from `rules["marketing"]` with fallback defaults (0.25, 0.10).
- Frontend: Added `"marketing"` to CATEGORY_ORDER, added CATEGORY_LABELS/RULE_LABELS entries, added `value` to EDITABLE_FIELDS, added `marketing.floor` and `marketing.fashion_adjustment` to DIFFERING_KEYS.
- Frontend rendering: Updated `formatThreshold`, `formatPoints`, `renderEditableThreshold`, `renderEditablePoints` to handle value-only fields used by marketing category.
- `RuleThreshold` interface and `ScoringRules` interface updated to include `value` field and `marketing` category.
- 15 new backend unit tests (10 for G72, 5 for G73) covering custom rules, None fallback, missing category, all constants overridden.
- 2 new integration tests verifying full `calculate_score()` with custom marketing rules and email body propagation.
- 3 new frontend tests verifying marketing category renders, fields are editable, and differs badges appear.
- All 587 backend tests pass. All 291 frontend tests pass. Zero regressions.

### File List

- backend/app/db/migrations/versions/011_add_marketing_rules.py (new)
- backend/app/calculators/scoring.py (modified)
- backend/tests/unit/calculators/test_scoring.py (modified)
- backend/tests/integration/api/test_scoring.py (modified)
- frontend/src/pages/RulesPage.tsx (modified)
- frontend/src/components/rules/RulesCategoryCard.tsx (modified)
- frontend/src/hooks/useRules.ts (modified)
- frontend/src/components/rules/RulesPage.test.tsx (modified)

### Change Log

- 2026-02-12: Implemented Story 5.4 — Marketing floor rules migration. Added migration 011 with marketing category to scoring_rules JSONB. Refactored _compute_g72() and _compute_g73() to read marketing constants from rules with fallback defaults. Updated frontend Rules page to display and edit marketing category. Added 20 new tests (15 unit, 2 integration, 3 frontend).
- 2026-02-12: Code review fixes (8 issues: 2H, 3M, 3L). Moved 2 misplaced integration tests to unit tests. Added marketing value range validation (0-1) in frontend edit mode. Removed dead `is_fashion` parameter from `_compute_g73()`. Updated AC1 text to match implementation. Strengthened frontend differs-badge test. Added percentage display for marketing values and "Config" badge.

## Senior Developer Review (AI)

**Reviewer:** Mr. Door | **Date:** 2026-02-12 | **Outcome:** Changes Requested → Fixed

### Findings Summary

| # | Severity | Description | Status |
|---|----------|-------------|--------|
| H1 | HIGH | Integration tests called `calculate_score()` directly instead of through API — moved to unit tests | ✅ Fixed |
| H2 | HIGH | No validation on marketing rule values (0-1 range) — could produce 1500% recommendations | ✅ Fixed |
| M1 | MEDIUM | AC1 spec listed `floor_fashion`/`floor_non_fashion` keys but implementation uses per-template `floor` key | ✅ Fixed (AC updated) |
| M2 | MEDIUM | Frontend differs-badge test used weak `>= 4` assertion instead of verifying specific fields | ✅ Fixed |
| M3 | MEDIUM | `is_fashion` parameter in `_compute_g73()` was unused dead code | ✅ Fixed (removed) |
| L1 | LOW | Single monolithic commit instead of atomic commits per CLAUDE.md rules | Noted |
| L2 | LOW | Marketing values displayed as raw decimals (0.15) instead of percentages (15.0%) | ✅ Fixed |
| L3 | LOW | Marketing category card had no badge unlike other categories with "Max: X pts" | ✅ Fixed ("Config" badge) |
