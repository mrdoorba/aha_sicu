---
id: T02
parent: S01
milestone: M002
provides:
  - _i18n optional fields on RowScore and CategoryScore TypeScript interfaces (R021)
  - Category name translation via CATEGORY_MAP + t() in ScoreBreakdownTable (R014)
  - Pre-i18n fallback — unknown category names render as-is (R019)
key_files:
  - frontend/src/hooks/useScoring.ts
  - frontend/src/pages/EvaluationDetailPage.tsx
  - frontend/src/pages/EvaluationDetailPage.test.tsx
key_decisions:
  - Reused existing CATEGORY_MAP + t() pattern from DetailedEvaluation.tsx — same lookup, same fallback behavior
  - ScoreBreakdownTable receives t() as prop (already wired), so no new useTranslation() call needed inside the component
patterns_established:
  - none — followed existing pattern from DetailedEvaluation.tsx
observability_surfaces:
  - Category translation is display-only with raw-string fallback; no new error paths or API calls
duration: 15m
verification_result: passed
completed_at: 2026-03-17
blocker_discovered: false
---

# T02: Add _i18n fields to TS types and translate category names in ScoreBreakdownTable

**Added `_i18n` optional fields to `RowScore`/`CategoryScore` interfaces and wired `CATEGORY_MAP` + `t()` translation into `ScoreBreakdownTable` with raw-string fallback for unknown categories.**

## What Happened

1. Added `metric_i18n`, `value_i18n`, `message_i18n`, `benchmark_i18n` (all `TranslatableText | null`) to `RowScore` interface in `useScoring.ts`. Added `category_i18n` to `CategoryScore`. `TranslatableText` was already imported — no new imports needed.

2. In `EvaluationDetailPage.tsx`, imported `CATEGORY_MAP` from `../lib/categoryMap`. Updated `ScoreBreakdownTable` to look up each category via `CATEGORY_MAP.find(m => m.backend === String(cat.category))` and render `t(mapped.labelKey)` when found, raw `String(cat.category)` when not. The component already received `t` as a prop, so no `useTranslation()` call was added.

3. Added two new tests to `EvaluationDetailPage.test.tsx`:
   - `should translate Indonesian category names via CATEGORY_MAP` — uses Indonesian backend names (`Kesehatan Operasional Toko`, `Bisnis Analisis`, `Data Iklan`) and asserts the id-locale translated labels appear (`Operasional`, `Bisnis`, `Iklan`).
   - `should fall back to raw category name when not in CATEGORY_MAP` — uses `Unknown Category XYZ` and asserts it renders unchanged.

4. All 20 existing tests pass unchanged — their English mock category names (`Operational`, `Business`, `Promo Tools`) fall through the CATEGORY_MAP lookup to raw string display, matching existing assertions.

## Verification

- `npx vitest run src/pages/EvaluationDetailPage.test.tsx` — **22 tests passed** (20 existing + 2 new)
- `npx vitest run` (full frontend) — **64 test files, 553 tests passed**, 0 failures, no regressions

### Slice-level verification status (T02 is final task in S01):
- ✅ Frontend: `EvaluationDetailPage.test.tsx` — 22/22 pass
- ✅ Full frontend regression: 553/553 pass
- ⏭️ Backend `evaluation_detail` tests — T01 verified these; not re-run here (no backend changes in T02)
- ✅ Diagnostic failure-path — marketplace default fallback verified in T01

## Diagnostics

- If category translation breaks (wrong CATEGORY_MAP entry, missing locale key), the category renders as the raw Indonesian backend string — visually wrong but not an error.
- Categories not in CATEGORY_MAP pass through unchanged. Verify by inspecting any evaluation with non-standard category names.
- TypeScript will fail compilation if backend `_i18n` fields don't match `TranslatableText` shape.

## Deviations

- Plan step 5 suggested asserting English translations (e.g., `Operational Health`), but tests use real i18n (not mocked) with default locale `id`. Asserted Indonesian locale values instead (`Operasional`, `Bisnis`, `Iklan`). Functionally equivalent — proves the CATEGORY_MAP → t() pipeline works.
- Plan step 3 suggested adding `useTranslation` import — `ScoreBreakdownTable` already receives `t` as a prop, so no additional import or hook call was needed.

## Known Issues

None.

## Files Created/Modified

- `frontend/src/hooks/useScoring.ts` — Added `_i18n` optional fields to `RowScore` and `CategoryScore` interfaces
- `frontend/src/pages/EvaluationDetailPage.tsx` — Imported `CATEGORY_MAP`, updated `ScoreBreakdownTable` to translate categories via lookup + `t()`
- `frontend/src/pages/EvaluationDetailPage.test.tsx` — Added 2 new tests for i18n translation and raw fallback
