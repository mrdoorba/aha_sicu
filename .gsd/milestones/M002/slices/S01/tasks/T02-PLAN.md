---
estimated_steps: 6
estimated_files: 3
---

# T02: Add _i18n fields to TS types and translate category names in ScoreBreakdownTable

**Slice:** S01 — EvaluationDetailPage i18n rendering
**Milestone:** M002

## Description

The dashboard components already translate category names and render i18n text — this task replicates that pattern for the EvaluationDetailPage. Three changes: (1) declare `_i18n` fields on `RowScore`/`CategoryScore` TypeScript interfaces so the type system knows about i18n data, (2) update `ScoreBreakdownTable` to translate category names via `CATEGORY_MAP` + `t()`, (3) add tests proving translation works and pre-i18n fallback works. Satisfies R014, R019, R021.

**Relevant skill:** Load `frontend-design` skill for UI component patterns.

## Steps

1. Open `frontend/src/hooks/useScoring.ts`. Find the `RowScore` interface (near line 7). Add optional `_i18n` fields: `metric_i18n?: TranslatableText | null`, `value_i18n?: TranslatableText | null`, `message_i18n?: TranslatableText | null`, `benchmark_i18n?: TranslatableText | null`. Note: `TranslatableText` is already imported in this file (line 4) — do NOT add a duplicate import.
2. In the same file, find the `CategoryScore` interface (near line 17). Add: `category_i18n?: TranslatableText | null`.
3. Open `frontend/src/pages/EvaluationDetailPage.tsx`. Find the `ScoreBreakdownTable` component (near line 97). Add imports: `useTranslation` from `react-i18next`, `CATEGORY_MAP` from `../../lib/categoryMap`. Inside the component, get `const { t } = useTranslation()`. Find where `cat.category` is rendered (currently `String(cat.category)`). Replace with the CATEGORY_MAP lookup pattern:
   ```tsx
   const mapped = CATEGORY_MAP.find(m => m.backend === String(cat.category));
   const label = mapped ? t(mapped.labelKey) : String(cat.category);
   ```
   Then render `label` instead of `String(cat.category)`.

   **Reference implementation:** See `frontend/src/components/dashboard/DetailedEvaluation.tsx` for the exact same pattern in use.

4. Open `frontend/src/pages/EvaluationDetailPage.test.tsx`. Find the existing score breakdown test (near line 135). Existing mock data uses English category names like `'Operational'`, `'Business'`, `'Promo Tools'` — these are NOT in `CATEGORY_MAP` (which maps Indonesian backend names). They will fall through to raw string display via the fallback path. **Do not change existing mock data or existing test assertions** — they should pass unchanged.

5. Add a new test: `it('should translate Indonesian category names via CATEGORY_MAP')`. Create mock evaluation data with Indonesian category names that ARE in CATEGORY_MAP (e.g., `'Kesehatan Operasional Toko'` for Operational Health). Render the component. Assert that the translated English name appears (e.g., `screen.getByText('Operational Health')` or whatever the EN locale value is for that key). The test uses `useTranslation` mock — verify the mock returns the key's English value or the key itself.

6. Add a new test: `it('should fall back to raw category name when not in CATEGORY_MAP')`. Create mock data with a category name not in CATEGORY_MAP (e.g., `'Unknown Category XYZ'`). Assert it renders as-is: `screen.getByText('Unknown Category XYZ')`. This proves R019 — pre-i18n data with arbitrary category strings won't break.

## Must-Haves

- [ ] `RowScore` interface declares `metric_i18n`, `value_i18n`, `message_i18n`, `benchmark_i18n` as `TranslatableText | null` optional fields
- [ ] `CategoryScore` interface declares `category_i18n` as `TranslatableText | null` optional field
- [ ] `ScoreBreakdownTable` translates category names via `CATEGORY_MAP.find()` + `t()` with raw string fallback
- [ ] Test proves Indonesian category names get translated
- [ ] Test proves unknown category names fall back to raw string display
- [ ] All existing `EvaluationDetailPage` tests pass without modification

## Verification

- Run: `cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M002/frontend && npx vitest run src/pages/EvaluationDetailPage.test.tsx --no-color`
  Expected: all tests pass including the 2 new ones
- Run full frontend regression: `cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M002/frontend && npx vitest run --no-color`
  Expected: no regressions

## Inputs

- `frontend/src/hooks/useScoring.ts` — current `RowScore`/`CategoryScore` interfaces without `_i18n` fields
- `frontend/src/pages/EvaluationDetailPage.tsx` — current `ScoreBreakdownTable` rendering raw `String(cat.category)`
- `frontend/src/pages/EvaluationDetailPage.test.tsx` — existing tests with English mock category names
- `frontend/src/lib/categoryMap.ts` — `CATEGORY_MAP` array mapping Indonesian backend names to i18n label keys (read-only reference)
- `frontend/src/components/dashboard/DetailedEvaluation.tsx` — reference implementation of category i18n pattern (read-only reference)
- T01 completed — `marketplace` field now available in backend API response (but T02 doesn't directly depend on it for rendering)

## Expected Output

- `frontend/src/hooks/useScoring.ts` — `RowScore` and `CategoryScore` interfaces with explicit `_i18n` fields
- `frontend/src/pages/EvaluationDetailPage.tsx` — `ScoreBreakdownTable` translates categories via `CATEGORY_MAP` + `t()` with fallback
- `frontend/src/pages/EvaluationDetailPage.test.tsx` — 2 new tests (i18n translation, fallback) passing alongside existing tests
