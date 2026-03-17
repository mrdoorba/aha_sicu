# S01: EvaluationDetailPage i18n rendering — UAT

**Milestone:** M002
**Written:** 2026-03-17

## UAT Type

- UAT mode: mixed (artifact-driven for backend API, human-experience for frontend visual check)
- Why this mode is sufficient: Backend marketplace field is verified by automated tests; category translation requires visual confirmation that the correct language renders on screen when toggling languages.

## Preconditions

- Dev server running (`npm run dev` in frontend, backend API server running)
- At least one evaluation exists in history (ideally one created after M001 with i18n data, and one pre-M001 without)
- User is logged in and can access `/history` page

## Smoke Test

1. Open any evaluation from history (`/history/:id`)
2. Verify the page loads without errors and displays score breakdown with category names

## Test Cases

### 1. Marketplace field present in API response

1. Open browser dev tools → Network tab
2. Navigate to `/history/:id` for any evaluation
3. Find the `GET /api/evaluations/{id}` request
4. Inspect the JSON response body
5. **Expected:** Response includes `"marketplace": "ID"` (or `"TH"` for Thai evaluations). Field is never null or absent.

### 2. Category names translate when switching to English

1. Set language toggle to **EN** (top-right language switcher)
2. Navigate to `/history/:id` for an evaluation
3. Look at the score breakdown table — the category column
4. **Expected:** Indonesian backend category names (`Kesehatan Operasional Toko`, `Bisnis Analisis`, `Data Iklan`, etc.) display as their English equivalents (`Operational`, `Business`, `Ads Data`, etc.) via the CATEGORY_MAP translation.

### 3. Category names translate when switching to Thai

1. Set language toggle to **TH**
2. Navigate to `/history/:id` for an evaluation
3. Look at the score breakdown table — the category column
4. **Expected:** Category names display in Thai translations matching the `th.json` locale file entries for each CATEGORY_MAP labelKey.

### 4. Category names revert when switching back to Indonesian

1. Set language toggle to **ID**
2. Open the same evaluation
3. Look at the score breakdown table — the category column
4. **Expected:** Category names display in Indonesian (matching the `id.json` locale values for the CATEGORY_MAP labelKeys).

### 5. Pre-i18n evaluation renders without errors

1. Set language toggle to **EN**
2. Open an evaluation that was created before the M001 i18n changes (it will have no `_i18n` fields in score_breakdown)
3. **Expected:** Page loads without errors. Category names display as raw Indonesian backend strings (e.g., `Kesehatan Operasional Toko` renders as `Operational` if in CATEGORY_MAP, or as-is if not mapped). Scoring messages display as raw Indonesian text. No blank fields, no console errors.

## Edge Cases

### Unknown category name fallback

1. If any evaluation has a category name not present in CATEGORY_MAP (custom or renamed category)
2. **Expected:** The raw category name string displays as-is — no error, no blank cell.

### Pre-marketplace evaluation (created before M001)

1. Open an evaluation created before the marketplace column existed
2. Check the API response in Network tab
3. **Expected:** `marketplace` field is `"ID"` (the default fallback). Page renders normally.

## Failure Signals

- API response for `/api/evaluations/{id}` missing `marketplace` field → SQL SELECT or schema wiring broken
- Category names show as raw Indonesian strings in EN/TH mode for known categories → CATEGORY_MAP import or t() wiring broken
- Page shows blank cells or crashes → TypeScript type mismatch or rendering error
- Console errors about undefined properties on score_breakdown items → _i18n field access on pre-i18n data not handled

## Requirements Proved By This UAT

- R018 — Marketplace field present in evaluation detail API response (Test Case 1)
- R019 — Pre-i18n evaluations render without errors (Test Case 5)
- R021 — TypeScript types declare _i18n fields (verified by compilation + automated tests, not UAT-visible)
- R014 (partial) — Category names translate via CATEGORY_MAP + t() (Test Cases 2-4)

## Not Proven By This UAT

- R014 full scope — Scoring messages, conclusions, closing messages, marketing budget text are not yet translated via renderTranslatable() in EvaluationDetailPage. Only category names translate.
- R015, R016 — Email language selector and email body i18n rebuild (S02 scope)
- R017, R020 — Locale hardcode cleanup and future-proofing (S03 scope)

## Notes for Tester

- Scoring messages (the text in each row's message column) will still display in Indonesian regardless of language toggle — this is expected and not a bug. Only category names translate in S01. Full message translation is a gap to be addressed.
- The language toggle is in the top-right header area. Changes take effect immediately without page reload.
- If no pre-M001 evaluations exist in the test environment, skip Test Case 5 — the automated test suite covers this path.
