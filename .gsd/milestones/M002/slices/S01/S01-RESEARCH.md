# S01 — EvaluationDetailPage i18n rendering — Research

**Date:** 2026-03-17
**Depth:** Targeted

## Summary

The EvaluationDetailPage (`/history/:id`) currently renders all scoring data as raw Indonesian strings. The dashboard components (`DetailedEvaluation`, `KesimpulanSection`, `CategoryMetricCard`) already demonstrate the correct i18n pattern: use `CATEGORY_MAP` + `t()` for category names, use `renderTranslatable()` for row-level text, and use `_i18n` fields from stored score_breakdown JSONB. The data pipeline already preserves `_i18n` fields end-to-end — the backend scoring API generates them, the orchestrator saves them via shallow `toRecord()` spreads, and the JSONB round-trips them. The work is straightforward pattern replication.

Two backend changes are needed: (1) add `e.marketplace` to the evaluation detail SQL query, and (2) add `marketplace` to `EvaluationDetailRow` TypedDict and `EvaluationDetailResponse` schema. The frontend `EvaluationDetail` type already declares `marketplace?: string` — it just needs the backend to populate it. The main frontend work is updating `ScoreBreakdownTable` to translate category names via `CATEGORY_MAP`, adding `_i18n` fields to TypeScript types (`RowScore`, `CategoryScore`, `ScoringResult`), and ensuring `renderTranslatable()` is available for any future row-level rendering on this page.

## Recommendation

Follow the dashboard pattern exactly. The dashboard's `DetailedEvaluation.tsx` is the reference implementation — it declares local `RowScore`/`CategoryBreakdown` interfaces with `_i18n` fields and passes them to `CategoryMetricCard` which calls `renderTranslatable()`. For S01, apply this same pattern to:

1. **Backend first** — add `marketplace` to query + schema (2 files, 3 lines each)
2. **Frontend types** — add `_i18n` field declarations to `useScoring.ts` types (R021)
3. **`ScoreBreakdownTable`** — translate category names via `CATEGORY_MAP` + `t()` (R014)
4. **Tests** — update existing tests to verify i18n rendering and add fallback test (R019)

Do NOT add conclusion/closing/marketing rendering to EvaluationDetailPage in S01 — those sections don't exist on this page and adding them would be new feature work, not i18n.

## Implementation Landscape

### Key Files

**Backend (2 files):**

- `backend/app/db/queries/evaluations.py` — `EvaluationDetailRow` TypedDict (line 52) needs `marketplace: str` field. `get_evaluation_by_id` SQL query (line 257) needs `e.marketplace` added to SELECT list.
- `backend/app/modules/evaluations/schemas.py` — `EvaluationDetailResponse` (near line 186) needs `marketplace: str = "ID"` field.
- `backend/app/modules/evaluations/service.py` — `get_evaluation_detail` (line 258) needs to pass `marketplace=row.get("marketplace", "ID")` to the response constructor.

**Frontend types (1 file):**

- `frontend/src/hooks/useScoring.ts` — `RowScore` interface (line 7) needs: `metric_i18n?: TranslatableText | null`, `value_i18n?: TranslatableText | null`, `message_i18n?: TranslatableText | null`, `benchmark_i18n?: TranslatableText | null`. `CategoryScore` interface (line 17) needs: `category_i18n?: TranslatableText | null`. These match `RowScoreItem` / `CategoryScoreItem` in the backend schema.

**Frontend rendering (1 file):**

- `frontend/src/pages/EvaluationDetailPage.tsx` — `ScoreBreakdownTable` component (line 97) currently renders `String(cat.category)`. Change to use `CATEGORY_MAP` + `t()` pattern from `DetailedEvaluation.tsx` (import `CATEGORY_MAP` from `../../lib/categoryMap`). Lookup: `const mapped = CATEGORY_MAP.find(m => m.backend === String(cat.category)); const label = mapped ? t(mapped.labelKey) : String(cat.category);`

**Frontend test (1 file):**

- `frontend/src/pages/EvaluationDetailPage.test.tsx` — Score breakdown test (line ~135) asserts `screen.getByText('Operational')` which is the raw category name from mock data. Since mock data uses English category names (not Indonesian backend names like "Kesehatan Operasional Toko"), the CATEGORY_MAP lookup won't find a match and falls back to the raw string — so existing tests should still pass. Add a new test with Indonesian category names to verify i18n translation works.

**Reference files (read-only, don't modify):**

- `frontend/src/utils/renderTranslatable.ts` — the `renderTranslatable()` utility
- `frontend/src/lib/categoryMap.ts` — `CATEGORY_MAP` array mapping backend Indonesian names to i18n keys
- `frontend/src/components/dashboard/DetailedEvaluation.tsx` — reference implementation for category i18n
- `frontend/src/components/dashboard/CategoryMetricCard.tsx` — reference implementation for row-level i18n

### Build Order

1. **Backend: marketplace in detail API** — Add `e.marketplace` to SQL query, TypedDict, schema, and service. This is the smallest change and unblocks the frontend knowing the marketplace for currency formatting (already partially working via `evaluation.marketplace` in the page).

2. **Frontend types: add `_i18n` fields** — Update `RowScore` and `CategoryScore` in `useScoring.ts` to declare `_i18n` optional fields. Import `TranslatableText` (already imported in the file). Purely additive, no behavior change. Satisfies R021.

3. **Frontend rendering: translate category names** — Import `CATEGORY_MAP` into `EvaluationDetailPage.tsx`. Update `ScoreBreakdownTable` to use the same lookup pattern as `DetailedEvaluation.tsx`. Satisfies R014 for category names.

4. **Tests: verify i18n and fallback** — Add test with Indonesian category names (`Kesehatan Operasional Toko`) that verifies translation. Add test with category names NOT in `CATEGORY_MAP` that verifies raw fallback (R019). Verify existing tests pass unchanged (the mock uses English names which fall through to raw display).

### Verification Approach

**Backend:**
```bash
cd backend && PYTHONPATH=. ../.venv/bin/python -m pytest tests/ -x -k "evaluation_detail" --no-header -q
```
Or simply verify the query returns marketplace:
```bash
PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -c "
from app.db.queries.evaluations import EvaluationDetailRow
print('marketplace' in EvaluationDetailRow.__annotations__)
"
```

**Frontend:**
```bash
cd frontend && npx vitest run src/pages/EvaluationDetailPage.test.tsx --no-color
```

**Full regression:**
```bash
cd frontend && npx vitest run --no-color
```

**Observable behavior:** Switch language to EN → open `/history/:id` → category names in score breakdown table display in English (e.g., "Operational Health" instead of "Kesehatan Operasional Toko"). Switch to TH → same category names display in Thai. Open a pre-i18n evaluation (whose score_breakdown has no `_i18n` fields) → raw Indonesian text displays as-is, no errors.

## Constraints

- `renderTranslatable()` is the mandated pattern for i18n rendering — D019 decision. Do not invent alternatives.
- `EvaluationDetailPage` does NOT render conclusion, closing message, or marketing budget — those sections don't exist on this page. Do not add them in S01.
- `toRecord()` in `typeGuards.ts` does a shallow spread — `_i18n` fields on `RowScore` survive because rows are nested objects copied by reference. Do not change `toRecord()`.
- The `marketplace` column already exists on the `evaluations` table (added in M001 migration 026). No schema migration needed — only a query SELECT change.

## Common Pitfalls

- **Mock data in existing tests uses English category names** — `ScoreBreakdownTable` tests use `'Operational'`, `'Business'`, `'Promo Tools'` which aren't in `CATEGORY_MAP` (which maps Indonesian names). The fallback path will render them as-is. This is correct behavior and tests should pass unchanged. Don't break tests by assuming they need updating.
- **`EvaluationDetail` type already has `marketplace?: string`** — Don't add it again. The backend just needs to populate it.
- **`TranslatableText` is already imported in `useScoring.ts`** (line 4) — Don't add a duplicate import.
