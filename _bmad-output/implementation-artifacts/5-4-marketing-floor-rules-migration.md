# Story 5.4: Marketing Floor Rules Migration

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system owner**,
I want the marketing floor thresholds (0.15 fashion / 0.12 non-fashion) and related marketing calculation constants to be stored in the scoring rules database and configurable through the Rules page,
so that I can adjust marketing percentage recommendations without requiring code changes.

## Acceptance Criteria

1. **AC1: Marketing category added to rules JSONB schema**
   - Given the scoring_rules table exists with Fashion and Non-Fashion templates
   - When the migration runs
   - Then each template's rules JSONB contains a new `"marketing"` category with keys: `floor_fashion` → 0.15, `floor_non_fashion` → 0.12, `base_subtraction` → 0.03, `upper_limit_base` → 0.20, `fashion_adjustment` → 0.05, `minimum_threshold` → 0.10, `display_max` → 0.25, `display_min` → 0.10

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

- [ ] Task 1: Create migration 011 to add marketing category to rules JSONB (AC: #1, #2)
  - [ ] 1.1 Add `marketing` category to Fashion template defaults dict
  - [ ] 1.2 Add `marketing` category to Non-Fashion template defaults dict (note: `fashion_adjustment: 0.0`, `floor: 0.12`)
  - [ ] 1.3 Write migration that updates existing rows' JSONB to include marketing category
  - [ ] 1.4 Increment version for both templates
  - [ ] 1.5 Write downgrade that removes marketing category from JSONB

- [ ] Task 2: Refactor `_compute_g72()` to use rules (AC: #3)
  - [ ] 2.1 Add `marketing_rules = _get_rule_category(rules, "marketing")` at function start
  - [ ] 2.2 Replace `0.15` / `0.12` floor with `_get_rule_value(marketing_rules, "floor", "threshold", 0.15 if is_fashion else 0.12)` — **BUT** note: floor differs by template, so the correct approach is to use template-specific defaults from the rules row, with a single `floor` key per template
  - [ ] 2.3 Replace `0.03` with `_get_rule_value(marketing_rules, "base_subtraction", "value", 0.03)`
  - [ ] 2.4 Replace `0.20` with `_get_rule_value(marketing_rules, "upper_limit_base", "value", 0.20)`
  - [ ] 2.5 Replace `0.05` with `_get_rule_value(marketing_rules, "fashion_adjustment", "value", 0.05 if is_fashion else 0.0)` — same note: use template-specific value
  - [ ] 2.6 Replace `0.10` minimum with `_get_rule_value(marketing_rules, "minimum_threshold", "value", 0.10)`
  - [ ] 2.7 Verify the final `max(max(min_val, minimum), floor)` logic is preserved

- [ ] Task 3: Refactor `_compute_g73()` to use rules (AC: #4)
  - [ ] 3.1 Read `display_max` and `display_min` from marketing rules with fallback defaults
  - [ ] 3.2 Replace hardcoded 0.25 and 0.10 clamping values

- [ ] Task 4: Update frontend Rules page to display marketing category (AC: #5)
  - [ ] 4.1 Add `"marketing"` to `CATEGORY_ORDER` array in `RulesPage.tsx`
  - [ ] 4.2 Add display labels for marketing rule keys in `RulesCategoryCard.tsx` (`CATEGORY_LABELS` and `RULE_LABELS`)
  - [ ] 4.3 Verify `RulesCategoryCard` correctly renders marketing fields (threshold/value types)
  - [ ] 4.4 Add `"floor"` to `DIFFERING_KEYS` Set if Fashion/Non-Fashion values differ

- [ ] Task 5: Add backend unit tests for marketing rules (AC: #6, #7)
  - [ ] 5.1 Test `_compute_g72()` with custom marketing rules (all constants overridden)
  - [ ] 5.2 Test `_compute_g72()` with `rules=None` (fallback path)
  - [ ] 5.3 Test `_compute_g72()` with rules missing marketing category
  - [ ] 5.4 Test `_compute_g73()` with custom display bounds
  - [ ] 5.5 Test `_compute_g73()` with fallback defaults

- [ ] Task 6: Add integration tests (AC: #7)
  - [ ] 6.1 Test full `calculate_score()` with custom marketing rules
  - [ ] 6.2 Verify marketing changes propagate to G72, G73, and email body

- [ ] Task 7: Add frontend test for marketing category display (AC: #5)
  - [ ] 7.1 Test RulesPage renders marketing category card
  - [ ] 7.2 Test marketing fields are editable in edit mode

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

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
