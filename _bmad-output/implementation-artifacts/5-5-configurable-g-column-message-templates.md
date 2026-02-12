# Story 5.5: Configurable G-Column Message Templates

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **system owner**,
I want the G-column verdict message templates (pass/fail text for each scoring metric) to be stored alongside their thresholds in the scoring rules database and editable through the Rules page,
so that I can customize evaluation feedback messages without requiring code changes.

## Acceptance Criteria

1. **AC1: Message templates added to rules JSONB schema**
   - Given the scoring_rules table exists with Fashion and Non-Fashion templates
   - When the migration runs
   - Then each rule entry that has a verdict message gains `message_pass` and/or `message_fail` fields containing template strings with `{placeholder}` syntax for dynamic values
   - And the existing rule fields (threshold, points, comparison) are unchanged

2. **AC2: Seed data migration adds current messages as defaults**
   - Given both Fashion and Non-Fashion template rows exist
   - When migration 012 (or 011 if 5-4 is not yet merged) runs
   - Then every rule entry that generates a G-column message has its current hardcoded message text stored as the default template
   - And templates use named placeholders matching the runtime variables (e.g., `{val_str}`, `{threshold}`)
   - And the version is incremented for both templates

3. **AC3: Simple pass/fail message generators read from rules**
   - Given rules with message templates are passed to the scoring calculator
   - When message generators execute for categories with simple pass/fail patterns (operational, content, visitors, products_status, campaign, promo summary rows 42-43)
   - Then `message_pass` / `message_fail` templates are read from the rule entry using `_get_rule_value()` with hardcoded messages as fallback defaults
   - And placeholders are formatted with runtime values via Python `.format()` or `.format_map()`
   - And when rules is None, behavior is identical to current implementation

4. **AC4: Complex message generators read from rules where feasible**
   - Given rules with message templates are passed to the scoring calculator
   - When message generators execute for categories with complex patterns:
     - **Business row 13 (sales trend):** `message_pass` and `message_fail` templates with `{idr_val}`, `{change_pct}`, `{idr_avg}` placeholders; the `>25% drop` addendum stored as `message_fail_severe` template
     - **Ads row 51 (GMV ratio):** `message_pass`, `message_fail`, `message_no_ads` templates
     - **Ads row 52 (cost ratio):** `message_pass`, `message_fail`, `message_no_ads`, `message_too_minimal` templates
     - **Campaign row 57:** `message_pass`, `message_fail`, `message_no_data` templates
   - Then each variant is read from the rule entry with fallback to current hardcoded text
   - And placeholders are formatted with runtime values

5. **AC5: Promo individual rows (31-41) read message templates**
   - Given rules with message templates are passed to the scoring calculator
   - When promo individual row messages are generated
   - Then templates for variants (zero revenue, too dependent, fail, pass, pass afiliasi) are read from `promo_tools` rules
   - And `{metric}`, `{pct_str}`, `{benchmark}` placeholders are formatted with runtime values

6. **AC6: G75 closing messages read from rules**
   - Given rules with message templates are passed to the scoring calculator
   - When `_compute_g75()` generates the closing message
   - Then verdict-to-message mapping is read from rules `interpretation.closing_messages` (or similar key) with fallback to current hardcoded dict
   - And the 7 verdict keys are preserved

7. **AC7: Competition messages read from rules**
   - Given rules with message templates are passed to the scoring calculator
   - When competition row messages are generated
   - Then `message_pass` ("kompetitif") and `message_fail` ("tidak kompetitif...") templates are read from rules with `{market_price}` placeholder

8. **AC8: Rules page displays and allows editing message templates**
   - Given the user navigates to the Rules page and enters edit mode
   - When viewing a rule entry that has message templates
   - Then message templates are displayed as editable text fields below the threshold/points fields
   - And template placeholders (e.g., `{val_str}`) are visually distinct or documented so the user knows not to remove them
   - And saving respects the existing password-confirm flow

9. **AC9: All existing tests pass unchanged**
   - Given the refactoring uses fallback-first pattern
   - When the full test suite runs
   - Then all existing tests pass without modification (fallback defaults produce identical output)

10. **AC10: New tests cover message template functionality**
    - Given message templates are configurable
    - When tests run
    - Then unit tests verify each message generator reads templates from rules
    - And unit tests verify fallback to defaults when rules is None or templates missing
    - And unit tests verify placeholder substitution with custom template text
    - And integration tests verify end-to-end scoring output with custom messages

## Tasks / Subtasks

- [x] Task 1: Design message template schema (AC: #1)
  - [x] 1.1 Define `message_pass` / `message_fail` field structure for simple rules
  - [x] 1.2 Define multi-variant message fields for complex rules (`message_no_ads`, `message_too_minimal`, `message_fail_severe`, `message_no_data`)
  - [x] 1.3 Define promo individual row message templates structure (shared across all promo tool rows)
  - [x] 1.4 Define G75 closing messages structure under `interpretation` category
  - [x] 1.5 Document all placeholder names and their runtime sources

- [x] Task 2: Create migration to add message templates to rules JSONB (AC: #1, #2)
  - [x] 2.1 Add `message_pass` / `message_fail` to each rule entry in Fashion defaults
  - [x] 2.2 Add `message_pass` / `message_fail` to each rule entry in Non-Fashion defaults
  - [x] 2.3 Add multi-variant message fields for complex rules
  - [x] 2.4 Add promo shared message templates
  - [x] 2.5 Add G75 closing messages to `interpretation` category
  - [x] 2.6 Write migration that updates existing rows' JSONB to include message fields
  - [x] 2.7 Increment version for both templates
  - [x] 2.8 Write downgrade that removes message fields from JSONB

- [x] Task 3: Create message template helper function (AC: #3, #4)
  - [x] 3.1 Create `_format_message_template(template: str, **kwargs) -> str` helper that safely formats template strings, returning the template unchanged if a placeholder is missing (prevent KeyError)
  - [x] 3.2 Add unit tests for the helper

- [x] Task 4: Refactor simple message generators to use templates (AC: #3)
  - [x] 4.1 Refactor `_generate_operational_messages()` — rows 7, 8, 9, 10, 11
  - [x] 4.2 Refactor `_generate_content_messages()` — row 24
  - [x] 4.3 Refactor `_generate_visitors_messages()` — rows 28, 29
  - [x] 4.4 Refactor `_generate_products_messages()` — rows 45, 46
  - [x] 4.5 Refactor `_generate_campaign_messages()` — row 57 (simple pass/fail)
  - [x] 4.6 Refactor promo summary rows 42, 43 in `_generate_promo_messages()`
  - [x] 4.7 Pass `rules` parameter to all message generators that don't already receive it

- [x] Task 5: Refactor complex message generators to use templates (AC: #4, #5, #6, #7)
  - [x] 5.1 Refactor `_generate_business_messages()` — row 13 (sales with severe drop variant), row 20
  - [x] 5.2 Refactor `_generate_ads_messages()` — rows 50, 51, 52 (multiple variants each)
  - [x] 5.3 Refactor `_generate_campaign_messages()` — row 57 `message_no_data` variant
  - [x] 5.4 Refactor `_generate_promo_messages()` — individual promo rows 31-41 (5 variants)
  - [x] 5.5 Refactor `_generate_competition_messages()` — rows 61-63
  - [x] 5.6 Refactor `_compute_g75()` — verdict-based closing messages

- [x] Task 6: Update `calculate_score()` to pass rules to all message generators (AC: #3, #4)
  - [x] 6.1 Add `rules` parameter to message generator function signatures
  - [x] 6.2 Thread `rules` through from `calculate_score()` entry point
  - [x] 6.3 Verify all call sites pass rules correctly

- [x] Task 7: Update frontend Rules page for message templates (AC: #8)
  - [x] 7.1 Add message template display in `RulesCategoryCard.tsx` — show `message_pass` / `message_fail` as textarea fields below threshold/points
  - [x] 7.2 Add label annotations for placeholders (e.g., "Available: {val_str}, {threshold}")
  - [x] 7.3 Handle multi-variant messages (collapsible or grouped display)
  - [x] 7.4 Add G75 closing messages section in interpretation area of `RulesPage.tsx`
  - [x] 7.5 Ensure message fields are included in the save payload

- [x] Task 8: Add backend unit tests (AC: #9, #10)
  - [x] 8.1 Test each simple message generator with custom templates
  - [x] 8.2 Test each complex message generator with custom templates
  - [x] 8.3 Test fallback to defaults when rules is None
  - [x] 8.4 Test fallback when message fields missing from rule entry
  - [x] 8.5 Test `_compute_g75()` with custom closing messages
  - [x] 8.6 Test `_format_message_template()` edge cases (missing placeholders, extra kwargs)

- [x] Task 9: Add integration and frontend tests (AC: #10)
  - [x] 9.1 Integration test: full `calculate_score()` with custom message templates
  - [x] 9.2 Verify custom messages propagate to email body
  - [x] 9.3 Frontend test: RulesPage renders message template fields
  - [x] 9.4 Frontend test: message template edits included in save payload

## Dev Notes

### Design Decision from Epic 5 Retro
**Option A chosen:** Message templates stored **alongside thresholds** in rules JSONB, not in a separate section. When editing a threshold, the associated message is visible and editable in the same context.

### Rules JSONB Structure — Message Templates

**Simple rule entry (before → after):**
```json
// BEFORE (current)
"unfulfilled_order_rate": {"threshold": 1.0, "points": 4, "comparison": "lte"}

// AFTER (with messages)
"unfulfilled_order_rate": {
  "threshold": 1.0, "points": 4, "comparison": "lte",
  "message_pass": "✔️ Tingkat Pesanan Tidak Terselesaikan = {val_str} Sudah Baik",
  "message_fail": "❌ Tingkat Pesanan Tidak Terselesaikan = {val_str} Kurang Baik, nilai disarankan: <{threshold}%"
}
```

**Complex rule entry with multiple variants:**
```json
"gmv_ratio_threshold": {
  "threshold": 84.0, "points": 5, "comparison": "lt",
  "message_pass": "✔️ % GMV Iklan / GMV Toko = {pct_str} Sudah Baik",
  "message_fail": "❌ % GMV Iklan / GMV Toko = {pct_str} Terlalu bergantung terhadap Iklan, nilai disarankan: <{threshold}%",
  "message_no_ads": "❌ Iklan tidak aktif sama sekali"
}
```

**Promo individual row templates (shared, not per-tool):**
```json
"promo_tools": {
  "individual_messages": {
    "message_zero": "{verdict} {metric} nil pendapatan",
    "message_dependent": "{verdict} {metric} = {pct_str} Terlalu mengandalkan promo, nilai disarankan: 15%-50%",
    "message_fail": "❌ {metric} = {pct_str} Kurang Efektif, nilai disarankan: {benchmark}",
    "message_pass": "✔️ {metric} ({pct_str}) digunakan & persentase penggunaan baik",
    "message_pass_afiliasi": "✔️ {metric} ({pct_str}) digunakan"
  },
  "usage_pct_threshold": { ... },
  "effectiveness_pct_threshold": { ... }
}
```

**G75 closing messages under interpretation:**
```json
"interpretation": {
  "ranges": [ ... ],
  "closing_messages": {
    "✔️": "Berdasarkan data analisa diatas, potensi toko masih belum maksimal...",
    "❌": "Berdasarkan data analisa diatas, perlu mempertimbangkan...",
    "❌ Non Mall": "Toko belum berstatus Mall...",
    "❌ No Brand": "Toko bukan merupakan toko yang memiliki brand sendiri...",
    "": "Performa toko sudah cukup baik...",
    "❌ Opex": "Tingkat keterlambatan cukup tinggi...",
    "⭕️": ""
  }
}
```

### Placeholder Reference

| Placeholder | Source | Used In |
|-------------|--------|---------|
| `{val_str}` | Formatted value (varies: %.1f, %.0f, %.2f, comma-separated) | Most simple messages |
| `{threshold}` | Rule threshold value | Fail messages with "nilai disarankan" |
| `{idr_val}` | `_fmt_idr(current_sales)` | Business row 13 |
| `{idr_avg}` | `_fmt_idr(avg_6mo)` | Business row 13 |
| `{change_pct}` | `abs(change_pct):.1f` | Business row 13 |
| `{benchmark}` | `row.benchmark` string | Conversion, ROI, promo rows |
| `{pct_str}` | `_fmt_pct_1dp(value)` | Ads, promo, campaign rows |
| `{metric}` | `row.metric` name | Promo individual rows |
| `{verdict}` | `row.verdict` emoji | Promo zero-revenue rows |
| `{market_price}` | `_fmt_idr(market_price)` | Competition rows |
| `{value_int}` | `int(row.value)` | Products row 45 |
| `{store_status}` | `row.value` (string) | Products row 46 |

### Safe Template Formatting
Create a `_format_message_template()` helper that uses `.format_map()` with a defaultdict to prevent `KeyError` if a placeholder is missing. This makes the system resilient to template edits that accidentally remove or misspell placeholders:

```python
from collections import defaultdict

def _format_message_template(template: str, **kwargs: Any) -> str:
    """Format a message template safely — missing placeholders stay as-is."""
    class SafeDict(defaultdict):
        def __missing__(self, key: str) -> str:
            return f"{{{key}}}"
    return template.format_map(SafeDict(None, **kwargs))
```

### Core Refactoring Pattern
Each message generator function gains a `rules` parameter and follows this pattern:

```python
def _generate_operational_messages(cat: CategoryScore, manual_data: dict, rules: dict | None = None) -> None:
    ops_rules = _get_rule_category(rules, "operational")
    for row in cat.rows:
        if row.row == 7:
            val_str = f"{row.value:.1f}%"
            if row.verdict == "✔️":
                tmpl = _get_rule_value(ops_rules, "unfulfilled_order_rate", "message_pass",
                    "✔️ Tingkat Pesanan Tidak Terselesaikan = {val_str} Sudah Baik")
                row.message = _format_message_template(tmpl, val_str=val_str)
            else:
                tmpl = _get_rule_value(ops_rules, "unfulfilled_order_rate", "message_fail",
                    "❌ Tingkat Pesanan Tidak Terselesaikan = {val_str} Kurang Baik, nilai disarankan: <1%")
                row.message = _format_message_template(tmpl, val_str=val_str, threshold="1")
```

### Files to Modify

**Backend:**
- `backend/app/db/migrations/versions/` — New migration (012 or 011 depending on 5-4 merge status)
- `backend/app/calculators/scoring.py` — All 9 `_generate_*_messages()` functions (~lines 892-1135), `_compute_g75()` (~lines 1289-1319), `calculate_score()` entry point (~lines 1466-1581)

**Frontend:**
- `frontend/src/components/rules/RulesCategoryCard.tsx` — Add message template display/edit fields
- `frontend/src/pages/RulesPage.tsx` — Add G75 closing messages section in interpretation area

**Tests:**
- `backend/tests/unit/test_scoring_*.py` — Message template tests for each category
- `backend/tests/integration/test_scoring_*.py` — End-to-end with custom messages
- `frontend/src/pages/__tests__/` or `frontend/src/components/rules/__tests__/` — Frontend message template tests

### Previous Story Intelligence (from 5-3 and 5-4)
- Story 5.3 refactored all 10 scoring categories to use DB rules — the message generators are the remaining hardcoded layer
- The `_get_rule_category()` / `_get_rule_value()` pattern is the standard approach
- Story 5-4 (if done first) establishes the marketing category pattern which extends the JSONB schema similarly
- Dynamic E-column benchmarks (from 5.3) already showed that benchmark strings can use rule values — this story extends that to G-column messages

### Scope & Complexity Notes
This is the **largest story in Epic 5** by file change count. The scoring.py changes span ~250 lines across 11 functions. Approach:
1. Start with the simple message generators (Task 4) to establish the pattern
2. Move to complex generators (Task 5) reusing the same pattern with more variants
3. Frontend last (Task 7) since backend must be working first
4. Tests throughout — write tests as you refactor each function

### Lessons Learned Relevant to This Story
- **Percentage values stored as fractions** (0.15 not 15%) — but message template thresholds in display text use human-readable form (e.g., "disarankan: <1%")
- **Indonesian language text** — message templates are in Indonesian; preserve exact wording including emoji prefixes
- **Type precision** — use `str` for message templates; `Literal` not needed here
- **File list gaps** — this story explicitly lists all files
- **Code review trend** — Epic 5 averaged ~1.3 HIGH issues/story; keep refactoring mechanical to minimize risk

### Project Structure Notes

- Alignment with unified project structure: migration numbering sequential, scoring.py is the single source of truth for message generation
- JSONB schema extension follows established category pattern with new string fields
- Frontend component reuse: `RulesCategoryCard` needs textarea support for message fields (new field type)

### References

- [Source: backend/app/calculators/scoring.py#_generate_operational_messages — lines 892-925]
- [Source: backend/app/calculators/scoring.py#_generate_business_messages — lines 928-964]
- [Source: backend/app/calculators/scoring.py#_generate_content_messages — lines 967-975]
- [Source: backend/app/calculators/scoring.py#_generate_visitors_messages — lines 978-992]
- [Source: backend/app/calculators/scoring.py#_generate_promo_messages — lines 995-1035]
- [Source: backend/app/calculators/scoring.py#_generate_products_messages — lines 1038-1050]
- [Source: backend/app/calculators/scoring.py#_generate_ads_messages — lines 1053-1101]
- [Source: backend/app/calculators/scoring.py#_generate_campaign_messages — lines 1104-1119]
- [Source: backend/app/calculators/scoring.py#_generate_competition_messages — lines 1122-1135]
- [Source: backend/app/calculators/scoring.py#_compute_g75 — lines 1289-1319]
- [Source: backend/app/calculators/scoring.py#calculate_score — lines 1466-1581]
- [Source: backend/app/db/migrations/versions/010_create_scoring_rules_table.py — JSONB schema]
- [Source: frontend/src/components/rules/RulesCategoryCard.tsx — lines 19-30, 135-221]
- [Source: frontend/src/pages/RulesPage.tsx — lines 16-27, 237-307]
- [Source: _bmad-output/implementation-artifacts/epic-5-retro-2026-02-12.md#D2]
- [Source: _bmad-output/lessons-learned.md]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

- Fixed threshold formatting inconsistency: `str(90.0)` = "90.0" vs `str(90)` = "90". Solution: use `f"{threshold:g}"` format specifier to strip trailing zeros from floats.
- Fixed generic fallback defaults in `_generate_operational_messages`: when `rules=None`, rule_key name appeared in messages instead of proper Indonesian text. Added `_ROW_DEFAULTS` dict with proper hardcoded fallbacks.

### Completion Notes List

- All 9 tasks and 44 subtasks completed
- Backend: 624 tests pass (158 unit scoring + 12 integration scoring + rest of suite)
- Frontend: 301 tests pass (39 RulesPage including 9 new message template tests)
- 3 pre-existing frontend test failures (Firebase API key config) are unrelated
- Migration 012 adds message templates to both fashion and non_fashion rules
- WhatsApp link is a generic "check email" message and does not contain individual scoring messages (9.2 adjusted accordingly)

### Code Review (Adversarial)

**Reviewer:** Claude Opus 4.6 — Adversarial Senior Dev Review
**Findings:** 8 issues (1 HIGH, 3 MEDIUM, 4 LOW)

| # | Severity | Issue | Resolution |
|---|----------|-------|------------|
| 1 | HIGH | `_format_message_template` crashes on malformed templates (unmatched braces → `ValueError`) | Fixed: added `try/except (ValueError, KeyError)` returning raw template on error |
| 2 | MEDIUM | `_SafeDict` inner class + import recreated per call | Fixed: moved to module-level `dict` subclass |
| 3 | MEDIUM | Triple source of truth for message defaults (migration, DEFAULT_*_RULES, inline fallbacks) | Fixed: added cross-referencing comments in all three locations |
| 4 | MEDIUM | No length validation on message template text inputs | Fixed: added `maxLength={500}` to all 3 textarea locations |
| 5 | LOW | Deep clone via `JSON.parse(JSON.stringify())` on every keystroke | Deferred: acceptable for this data size |
| 6 | LOW | Flat competition structure inconsistent with category nesting | Deferred: matches original design spec |
| 7 | LOW | Limited frontend test coverage for edge cases | Deferred: core paths covered |
| 8 | LOW | Commit message quality inconsistent | N/A: retrospective observation |

**Post-fix test results:** 161 unit tests pass (3 new malformed-template tests added)

### File List

**Created:**
- `backend/app/db/migrations/versions/012_add_message_templates.py` — Migration adding message templates to scoring_rules JSONB

**Modified:**
- `backend/app/calculators/scoring.py` — Added `_format_message_template()` helper; refactored all 9 `_generate_*_messages()` functions + `_compute_g75()` to read templates from rules; updated `calculate_score()` to thread rules; added message templates to DEFAULT_FASHION_RULES and DEFAULT_NON_FASHION_RULES
- `frontend/src/hooks/useRules.ts` — Added message template fields to RuleThreshold interface; added competition and closing_messages to ScoringRules
- `frontend/src/components/rules/RulesCategoryCard.tsx` — Added message template display/edit with collapsible per-rule sections, textarea editing, placeholder hints
- `frontend/src/pages/RulesPage.tsx` — Added handleMessageChange, handleClosingMessageChange, handleCompetitionMessageChange handlers; added Competition Messages and G75 Closing Messages card sections
- `backend/tests/unit/calculators/test_scoring.py` — Added ~700 lines: TestFormatMessageTemplate (8 tests), message template tests for all 10 categories + G75 + end-to-end (34 tests total)
- `backend/tests/integration/api/test_scoring.py` — Added test_score_with_custom_message_templates integration test
- `frontend/src/components/rules/RulesPage.test.tsx` — Added Message templates describe block (9 tests)

### Change Log

| Commit | Description |
|--------|-------------|
| 1 | Add message template support to scoring rules JSONB (migration, helper, all generators refactored) |
| 2 | Add unit tests for message template functionality (34 new tests) |
| 3 | Add message template display and editing to Rules page UI |
| 4 | Add integration and frontend tests for message templates |
| 5 | Code review fixes: malformed template resilience, maxLength validation, source-of-truth comments |
