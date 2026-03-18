---
id: S02
parent: M002
milestone: M002
provides:
  - EvaluationDetailPage renders all scoring text through i18n with language reactivity
  - ScoringConclusionSection renders conclusion (bullet list), marketing_budget, closing_message from scoring_summary via renderTranslatable()
  - ScoreBreakdownTable translates category names via CATEGORY_MAP + t() with raw-string fallback
  - Backend evaluation detail API returns marketplace field with triple-layer fallback (SQL COALESCE → service row.get() → Pydantic default)
  - Frontend RowScore/CategoryScore types declare optional _i18n fields
  - Pre-i18n evaluations (missing scoring_summary or _i18n fields) render gracefully — no errors, no blank fields
requires:
  - slice: S01
    provides: renderTranslatable() utility, CATEGORY_MAP, KesimpulanSection pattern, frontend i18n infrastructure
affects:
  - S03
key_files:
  - backend/app/db/queries/evaluations.py
  - backend/app/modules/evaluations/schemas.py
  - backend/app/modules/evaluations/service.py
  - backend/tests/integration/api/test_evaluation_detail.py
  - frontend/src/hooks/useScoring.ts
  - frontend/src/pages/EvaluationDetailPage.tsx
  - frontend/src/pages/EvaluationDetailPage.test.tsx
key_decisions:
  - Triple-layer marketplace fallback (SQL COALESCE → service row.get() → Pydantic default) ensures marketplace is never absent from API response
  - ScoringConclusionSection inlined in EvaluationDetailPage.tsx (not separate file) — matches local component pattern used by ScoreBreakdownTable, AdsKeywordSection, TopSkuSection, DiscountSection
  - CATEGORY_MAP.find() + t() with raw-string fallback for unmapped categories — no errors for unknown category names
  - isScoringSummary() type guard + parseBulletPoints() + renderTranslatable() as the standard pattern for consuming scoring_summary data on detail pages
patterns_established:
  - CATEGORY_MAP.find() + t() pattern for translating Indonesian backend category names in table components
  - isScoringSummary() type guard + renderTranslatable() for scoring_summary consumption on detail pages (mirrors KesimpulanSection from dashboard)
  - parseBulletPoints() for splitting raw conclusion text into bullet list items (pre-i18n fallback)
observability_surfaces:
  - GET /api/v1/evaluations/{id} response includes "marketplace" field (always non-empty string, default "ID")
  - ScoreBreakdownTable renders translated category text for mapped categories, raw backend string for unmapped
  - "Kesimpulan" heading visible in Calculator Results card when scoring_summary exists; absent when missing
  - Switching locale changes conclusion items, marketing budget, and closing message text when _i18n fields present
drill_down_paths:
  - .gsd/milestones/M002/slices/S02/tasks/T01-SUMMARY.md
  - .gsd/milestones/M002/slices/S02/tasks/T02-SUMMARY.md
duration: 27m
verification_result: passed
completed_at: 2026-03-18
---

# S02: EvaluationDetailPage renderTranslatable() wiring

**EvaluationDetailPage now renders all scoring text — category names, conclusion bullet list, marketing budget, closing message — through the i18n pipeline with language reactivity. Pre-i18n evaluations fall back to raw Indonesian text with no errors.**

## What Happened

Two tasks delivered the full S02 scope:

**T01** wired the prerequisite infrastructure that S01 designed but hadn't committed to this worktree branch. The backend evaluation detail API gained a `marketplace` field with triple-layer fallback (SQL `COALESCE(e.marketplace, 'ID')` → service `row.get("marketplace", "ID")` → Pydantic default `"ID"`). Frontend `RowScore` and `CategoryScore` types received optional `_i18n` fields. `ScoreBreakdownTable` was updated to translate Indonesian backend category names (e.g. "Kesehatan Operasional Toko") into locale-appropriate text via `CATEGORY_MAP.find()` + `t()`, with unknown categories rendering as raw strings.

**T02** delivered the core S02 deliverable: a `ScoringConclusionSection` component inline in `EvaluationDetailPage.tsx`. It extracts `scoring_summary` from `calculator_results` via an `isScoringSummary()` type guard and renders:
- **Conclusion** as a bullet list — via `conclusion_i18n` array (each item → `t(item.key, item.vars)`) with fallback to `parseBulletPoints(conclusion)` for pre-i18n evaluations
- **Marketing budget** via `renderTranslatable()` using `marketing_budget_i18n` with raw-string fallback
- **Closing message** via `renderTranslatable()` using `closing_message_i18n` with raw-string fallback

When `scoring_summary` is absent (all pre-existing evaluations), the component returns `null` silently — zero regressions against the existing 22 tests.

## Verification

| # | Check | Result | Detail |
|---|-------|--------|--------|
| 1 | Backend evaluation detail tests | ✅ 11/11 pass | Including new `test_get_evaluation_detail_has_marketplace` |
| 2 | Frontend EvaluationDetailPage tests | ✅ 25/25 pass | 22 existing + 3 new (i18n rendering, raw fallback, missing scoring_summary) |
| 3 | Full frontend regression | ✅ 556/556 pass | 64 test files, 0 failures, 1 skipped (pre-existing) |
| 4 | Pre-i18n graceful degradation | ✅ proven | Existing tests use MOCK_EVALUATION without scoring_summary — all pass, no console errors |

## Requirements Advanced

- **R014** — EvaluationDetailPage now renders scoring messages, category names, conclusion, marketing budget, and closing message through i18n. Language reactivity is wired via `renderTranslatable()` and `t()`. This requirement is substantively delivered — full proof requires visual UAT (switching language toggle and viewing evaluation).
- **R018** — Evaluation detail API now returns `marketplace` field with triple-layer fallback. Fully delivered and tested.
- **R019** — Pre-i18n evaluations (without `_i18n` fields or `scoring_summary`) display raw Indonesian text without errors. Proven by existing tests continuing to pass with mocks that lack i18n data.

## Requirements Validated

- **R018** — Backend test `test_get_evaluation_detail_has_marketplace` proves API returns marketplace field; triple-layer fallback ensures it's never absent.

## New Requirements Surfaced

- none

## Requirements Invalidated or Re-scoped

- none

## Deviations

None — both tasks executed exactly as planned.

## Known Limitations

- **Visual language reactivity not machine-verified**: Tests prove i18n keys are rendered via `t()` and `renderTranslatable()`, but actual locale switching (seeing "Operations" vs "Operasional") requires human UAT since test i18n mock returns keys directly.
- **R014 not yet fully validated**: Component-level proof is complete. Visual UAT (switch language toggle → view evaluation → verify text changes) is needed for full validation.
- **Email rendering not yet wired**: S03 handles email language selector and i18n body rebuild — the evaluation detail page rendering is complete but email output still uses pre-rendered Indonesian text.

## Follow-ups

- none — all remaining work is in S03 (email language selector) and S04 (locale hardcode cleanup), which are already planned.

## Files Created/Modified

- `backend/app/db/queries/evaluations.py` — Added `marketplace: str` to `EvaluationDetailRow` TypedDict; added `COALESCE(e.marketplace, 'ID')` to detail query SQL
- `backend/app/modules/evaluations/schemas.py` — Added `marketplace: str = "ID"` to `EvaluationDetailResponse`
- `backend/app/modules/evaluations/service.py` — Added `marketplace=row.get("marketplace", "ID")` to response constructor
- `backend/tests/integration/api/test_evaluation_detail.py` — Added marketplace to fixture; added `test_get_evaluation_detail_has_marketplace`
- `frontend/src/hooks/useScoring.ts` — Added optional `_i18n` fields to `RowScore` and `CategoryScore`
- `frontend/src/pages/EvaluationDetailPage.tsx` — Imported `CATEGORY_MAP` and `renderTranslatable`; wired `ScoreBreakdownTable` category translation; added `ScoringConclusionSection` with `isScoringSummary()` type guard, `parseBulletPoints()`, and `renderTranslatable()` wiring
- `frontend/src/pages/EvaluationDetailPage.test.tsx` — Added 5 tests: category translation (2), i18n rendering with scoring_summary, raw fallback, graceful missing scoring_summary

## Forward Intelligence

### What the next slice should know
- `renderTranslatable()` is now used in two places: dashboard `KesimpulanSection` and history detail `ScoringConclusionSection`. S03 email body assembly can follow the same pattern but will need `i18n.getFixedT(selectedLang)` instead of the component-scoped `t()` to render in a language different from the UI.
- The `scoring_summary` shape is validated by `isScoringSummary()` type guard — S03 can reuse this guard when extracting data for email body assembly.
- `CATEGORY_MAP` is now imported in both `EvaluationDetailPage.tsx` and backend `template.py` — when adding a new category, both must be updated.

### What's fragile
- `CATEGORY_MAP` lookup is string-based against Indonesian backend category names — if backend changes category naming, the map silently falls back to raw strings (graceful but invisible). Monitor by checking rendered category names match locale expectations.
- `parseBulletPoints()` splits on newlines and strips `•/-` prefixes — unusual bullet formats from backend would break the split.

### Authoritative diagnostics
- `GET /api/v1/evaluations/{id}` → check `marketplace` field in response JSON — should always be a non-empty string
- DOM inspection: look for "Kesimpulan" heading in Calculator Results card — presence confirms scoring_summary exists and rendered
- Test mock `MOCK_EVALUATION` deliberately lacks `scoring_summary` — if a test adds it, the ScoringConclusionSection will render and may need new assertions

### What assumptions changed
- No assumptions changed — S01 type declarations and renderTranslatable() utility worked exactly as expected.
