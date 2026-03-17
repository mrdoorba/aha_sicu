---
id: S01
parent: M002
milestone: M002
provides:
  - marketplace field in evaluation detail API response with dual-layer fallback (R018)
  - _i18n optional fields on RowScore and CategoryScore TypeScript interfaces (R021)
  - Category name translation via CATEGORY_MAP + t() in ScoreBreakdownTable with raw fallback (R014 partial, R019)
requires: []
affects:
  - S02
  - S03
key_files:
  - backend/app/db/queries/evaluations.py
  - backend/app/modules/evaluations/schemas.py
  - backend/app/modules/evaluations/service.py
  - frontend/src/hooks/useScoring.ts
  - frontend/src/pages/EvaluationDetailPage.tsx
  - frontend/src/pages/EvaluationDetailPage.test.tsx
key_decisions:
  - Dual-layer marketplace fallback (SQL COALESCE + Pydantic default) ensures pre-marketplace evaluations never produce null/missing marketplace
  - Reused existing CATEGORY_MAP + t() pattern from DetailedEvaluation.tsx — same lookup, same raw-string fallback
patterns_established:
  - Category translation pattern in ScoreBreakdownTable — CATEGORY_MAP.find() + t(labelKey) with raw fallback for unmapped names
observability_surfaces:
  - GET /api/evaluations/{id} response includes marketplace field — absent field indicates SQL or schema wiring is broken
drill_down_paths:
  - .gsd/milestones/M002/slices/S01/tasks/T01-SUMMARY.md
  - .gsd/milestones/M002/slices/S01/tasks/T02-SUMMARY.md
duration: 25m
verification_result: passed
completed_at: 2026-03-17
---

# S01: EvaluationDetailPage i18n rendering

**Backend evaluation detail API returns `marketplace` with fallback default; frontend TypeScript types declare `_i18n` fields; ScoreBreakdownTable translates category names via CATEGORY_MAP + t() with raw-string fallback for pre-i18n evaluations.**

## What Happened

Two tasks, both clean:

**T01 (backend):** Wired `marketplace` from DB through the evaluation detail pipeline. Added `COALESCE(e.marketplace, 'ID')` to the SQL SELECT in `get_evaluation_by_id`, `marketplace: str` to `EvaluationDetailRow` TypedDict, `marketplace: str = "ID"` to `EvaluationDetailResponse` Pydantic schema, and `marketplace=row.get("marketplace", "ID")` to the service constructor call. The dual-layer fallback (SQL COALESCE + Pydantic default) means pre-marketplace evaluations always return `"ID"` — no null or missing field possible.

**T02 (frontend):** Added `_i18n` optional fields (`metric_i18n`, `value_i18n`, `message_i18n`, `benchmark_i18n`) to `RowScore` and `category_i18n` to `CategoryScore` in `useScoring.ts`. Updated `ScoreBreakdownTable` in `EvaluationDetailPage.tsx` to look up each category via `CATEGORY_MAP.find(m => m.backend === String(cat.category))` and render `t(mapped.labelKey)` when found, raw `String(cat.category)` when not. Added two new tests: one proving Indonesian backend names translate via CATEGORY_MAP, one proving unknown category names pass through unchanged.

## Verification

- Backend `evaluation_detail` tests: 10/10 passed
- Frontend `EvaluationDetailPage.test.tsx`: 22/22 passed (20 existing + 2 new)
- Full frontend regression: 64 files, 553/553 passed, 0 failures
- Diagnostic fallback check: `EvaluationDetailResponse` defaults marketplace to `"ID"` — confirmed

## Requirements Advanced

- R014 — Category names in ScoreBreakdownTable now translate via CATEGORY_MAP + t(). Remaining R014 scope (scoring messages, conclusions, closing messages, marketing budget via renderTranslatable) is not yet wired in EvaluationDetailPage.
- R018 — Evaluation detail API returns marketplace field with dual-layer fallback. Fully satisfied.
- R019 — Pre-i18n evaluations render raw Indonesian category names via fallback. Proven by test with unknown category names.
- R021 — RowScore and CategoryScore TypeScript interfaces declare _i18n fields. Fully satisfied.

## Requirements Validated

- R018 — GET /api/evaluations/{id} returns marketplace field; SQL COALESCE and Pydantic default both fall back to "ID"; 10 backend tests pass.
- R021 — TypeScript interfaces explicitly declare _i18n fields; compilation succeeds; 553 frontend tests pass.

## New Requirements Surfaced

- none

## Requirements Invalidated or Re-scoped

- none

## Deviations

- T02 tests assert Indonesian locale values (the default locale) instead of English translations as suggested in the plan. Functionally equivalent — proves the CATEGORY_MAP → t() pipeline works regardless of active locale.
- ScoreBreakdownTable already receives `t` as a prop, so no `useTranslation()` import was needed — simpler than the plan anticipated.

## Known Limitations

- R014 is only partially addressed: category names translate, but scoring messages, conclusions, closing messages, and marketing budget text in EvaluationDetailPage still render raw Indonesian text. Full renderTranslatable() wiring for these fields was not in S01 scope.
- The `_i18n` fields on types are declared but not yet consumed by rendering logic in EvaluationDetailPage (will be consumed when renderTranslatable() is wired for message/conclusion display).

## Follow-ups

- none — remaining work is covered by S02 (email i18n) and S03 (locale cleanup). The full renderTranslatable() wiring for scoring messages on EvaluationDetailPage may need scoping in roadmap reassessment since it wasn't in S01-S03 plans.

## Files Created/Modified

- `backend/app/db/queries/evaluations.py` — Added `marketplace: str` to `EvaluationDetailRow`, added `COALESCE(e.marketplace, 'ID')` to SELECT
- `backend/app/modules/evaluations/schemas.py` — Added `marketplace: str = "ID"` to `EvaluationDetailResponse`
- `backend/app/modules/evaluations/service.py` — Added `marketplace=row.get("marketplace", "ID")` to response constructor
- `frontend/src/hooks/useScoring.ts` — Added `_i18n` optional fields to `RowScore` and `CategoryScore` interfaces
- `frontend/src/pages/EvaluationDetailPage.tsx` — Imported `CATEGORY_MAP`, updated `ScoreBreakdownTable` to translate categories
- `frontend/src/pages/EvaluationDetailPage.test.tsx` — Added 2 tests for i18n translation and raw fallback

## Forward Intelligence

### What the next slice should know
- `marketplace` is available in the evaluation detail API response — S02 can use it for currency formatting and email language context.
- `_i18n` fields are declared on TypeScript types but not yet rendered via `renderTranslatable()` in EvaluationDetailPage. S02's email body rebuild will need to consume these fields from score_breakdown data.
- The CATEGORY_MAP + t() pattern in ScoreBreakdownTable is identical to DetailedEvaluation.tsx — consistent codebase pattern.

### What's fragile
- Category translation depends on exact match between `CATEGORY_MAP[].backend` strings and the category names stored in score_breakdown JSONB. If backend scoring changes a category name, it won't match and will fall back to raw string (safe but untranslated).

### Authoritative diagnostics
- `GET /api/evaluations/{id}` response JSON — check for `marketplace` field presence. If missing, the SQL SELECT or schema wiring is broken.
- `EvaluationDetailPage.test.tsx` — 22 tests cover rendering, category translation, and fallback behavior. Fastest signal for regressions.

### What assumptions changed
- Plan assumed ScoreBreakdownTable would need a new `useTranslation()` call — it already receives `t` as a prop, so the wiring was simpler.
