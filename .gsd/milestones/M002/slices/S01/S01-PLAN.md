# S01: EvaluationDetailPage i18n rendering

**Goal:** The EvaluationDetailPage (`/history/:id`) renders all scoring text through i18n — category names translate via `CATEGORY_MAP` + `t()`, TypeScript types declare `_i18n` fields, and the backend populates `marketplace` in the detail API response. Pre-i18n evaluations fall back to raw Indonesian text.
**Demo:** Switch language to EN → open any evaluation in history → category names in score breakdown display in English. Switch to TH → same names display in Thai. Open a pre-i18n evaluation → raw Indonesian text displays as-is, no errors.

## Must-Haves

- Backend evaluation detail API returns `marketplace` field (R018)
- `RowScore`, `CategoryScore` TypeScript interfaces declare `_i18n` optional fields (R021)
- `ScoreBreakdownTable` translates category names via `CATEGORY_MAP` + `t()` with raw fallback (R014)
- Pre-i18n evaluations (no `_i18n` fields) render original Indonesian text without errors (R019)

## Proof Level

- This slice proves: integration
- Real runtime required: no (frontend component tests + backend unit tests sufficient)
- Human/UAT required: yes (visual check — switch language, view evaluation, verify text changes)

## Verification

- Backend: `cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M002 && PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/ -x -k "evaluation_detail" --no-header -q`
- Frontend: `cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M002/frontend && npx vitest run src/pages/EvaluationDetailPage.test.tsx --no-color`
- Full frontend regression: `cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M002/frontend && npx vitest run --no-color`
- Diagnostic failure-path: `cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M002 && PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -c "from app.modules.evaluations.schemas import EvaluationDetailResponse; r = EvaluationDetailResponse(id=1, brand_id=1, brand_name='test', final_score=0.0, verdict='x', template='default', score_breakdown=[], calculator_results={}, manual_inputs={}, evaluator_email='a@b.c', created_at='2025-01-01T00:00:00', rule_version=1); assert r.marketplace == 'ID', f'Default marketplace wrong: {r.marketplace}'; print('OK: default marketplace fallback works')"` — verifies marketplace default fallback for pre-marketplace evaluations.

## Observability / Diagnostics

- **API response inspection:** `GET /api/evaluations/{id}` response JSON includes `marketplace` field — agents can `curl` or inspect network logs to verify the field is present and non-null.
- **Failure visibility:** If `marketplace` is NULL in the DB (pre-M001 rows), the SQL COALESCE and Pydantic default both fall back to `"ID"` — no 500 errors. A missing `marketplace` in the JSON response indicates the backend schema or SQL wiring is broken.
- **Diagnostic failure-path check:** `cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M002 && PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -c "from app.modules.evaluations.schemas import EvaluationDetailResponse; r = EvaluationDetailResponse(id=1, brand_id=1, brand_name='test', final_score=0.0, verdict='x', template='default', score_breakdown=[], calculator_results={}, manual_inputs={}, evaluator_email='a@b.c', created_at='2025-01-01T00:00:00', rule_version=1); assert r.marketplace == 'ID', f'Default marketplace wrong: {r.marketplace}'; print('OK: default marketplace fallback works')"` — verifies default fallback for rows without marketplace.
- **Redaction:** No sensitive data involved — `marketplace` is a two-letter country code.

## Integration Closure

- Upstream surfaces consumed: `renderTranslatable()` from `utils/renderTranslatable.ts`, `CATEGORY_MAP` from `lib/categoryMap.ts`, `TranslatableText` type from `types/i18n.ts`
- New wiring introduced in this slice: `marketplace` field wired from backend SQL → TypedDict → schema → frontend type; `CATEGORY_MAP` + `t()` wired into `ScoreBreakdownTable`
- What remains before the milestone is truly usable end-to-end: S02 (email language selector + i18n body rebuild), S03 (locale hardcode cleanup)

## Tasks

- [x] **T01: Add marketplace to evaluation detail API response** `est:20m` `actual:10m`
  - Why: Frontend needs `marketplace` to determine currency code for formatting. The column already exists on the `evaluations` table (M001 migration 026) but isn't selected in the detail query. Satisfies R018.
  - Files: `backend/app/db/queries/evaluations.py`, `backend/app/modules/evaluations/schemas.py`, `backend/app/modules/evaluations/service.py`
  - Do: Add `e.marketplace` to the SELECT list in `get_evaluation_by_id`. Add `marketplace: str` to `EvaluationDetailRow` TypedDict. Add `marketplace: str = "ID"` to `EvaluationDetailResponse` schema. Pass `marketplace=row.get("marketplace", "ID")` in the service constructor call.
  - Verify: `cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M002 && PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -c "from app.db.queries.evaluations import EvaluationDetailRow; print('marketplace' in EvaluationDetailRow.__annotations__)"` prints `True`. Existing evaluation detail tests pass.
  - Done when: `EvaluationDetailRow` has `marketplace` field, SQL query selects it, schema exposes it with default `"ID"`, and no backend test regressions.

- [x] **T02: Add _i18n fields to TS types and translate category names in ScoreBreakdownTable** `est:40m` `actual:15m`
  - Why: Core i18n rendering for the evaluation detail page. Adds type declarations (R021), translates category names (R014), and verifies pre-i18n fallback (R019). Skill: load `frontend-design` for UI component patterns.
  - Files: `frontend/src/hooks/useScoring.ts`, `frontend/src/pages/EvaluationDetailPage.tsx`, `frontend/src/pages/EvaluationDetailPage.test.tsx`
  - Do: (1) Add `_i18n` optional fields to `RowScore` and `CategoryScore` in `useScoring.ts` — `metric_i18n`, `value_i18n`, `message_i18n`, `benchmark_i18n` on `RowScore`; `category_i18n` on `CategoryScore`. `TranslatableText` is already imported. (2) In `EvaluationDetailPage.tsx`, import `CATEGORY_MAP` from `../../lib/categoryMap` and `useTranslation`. Update `ScoreBreakdownTable` to look up category via `CATEGORY_MAP.find(m => m.backend === String(cat.category))` and render `t(mapped.labelKey)` when found, raw `String(cat.category)` when not. (3) Add test with Indonesian category names (`Kesehatan Operasional Toko`) verifying English translation appears. Add test with unknown category names verifying raw fallback. Existing tests use English mock names that won't match CATEGORY_MAP — they should pass unchanged via fallback.
  - Verify: `cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M002/frontend && npx vitest run src/pages/EvaluationDetailPage.test.tsx --no-color`
  - Done when: `RowScore`/`CategoryScore` declare `_i18n` fields, category names translate through `CATEGORY_MAP` + `t()`, unknown categories fall back to raw string, all existing + new tests pass.

## Files Likely Touched

- `backend/app/db/queries/evaluations.py`
- `backend/app/modules/evaluations/schemas.py`
- `backend/app/modules/evaluations/service.py`
- `frontend/src/hooks/useScoring.ts`
- `frontend/src/pages/EvaluationDetailPage.tsx`
- `frontend/src/pages/EvaluationDetailPage.test.tsx`
