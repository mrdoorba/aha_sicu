# S02: EvaluationDetailPage renderTranslatable() wiring — UAT

**Milestone:** M002
**Written:** 2026-03-18

## UAT Type

- UAT mode: mixed (artifact-driven tests verified; live-runtime visual check required)
- Why this mode is sufficient: Component tests prove i18n wiring is correct (keys rendered via t() and renderTranslatable()). Visual UAT confirms the actual translated strings appear correctly when switching languages in a running app.

## Preconditions

- Backend running (`uvicorn` or equivalent) with database containing at least one evaluation
- Frontend dev server running (`npm run dev` or `npx vite`)
- User logged in with access to evaluation history
- Language toggle visible in header (ID/EN/TH options)
- At least one evaluation exists that was scored **after** i18n support was added (has `scoring_summary` in `calculator_results`)
- At least one evaluation exists that was scored **before** i18n support (lacks `scoring_summary` / `_i18n` fields)

## Smoke Test

1. Navigate to Evaluation History → click any evaluation
2. Page loads without errors
3. Scroll to Calculator Results section — if scoring_summary exists, "Kesimpulan" heading is visible

## Test Cases

### 1. Category names translate when switching language

1. Set language toggle to **ID** (Indonesian)
2. Navigate to any evaluation detail page
3. Scroll to the Score Breakdown table
4. Note the category names (e.g. "Operasional", "Bisnis", "Alat Promo")
5. Switch language toggle to **EN**
6. **Expected:** Category names change to English equivalents (e.g. "Operations", "Business", "Promo Tools"). Table layout unchanged.
7. Switch language toggle to **TH**
8. **Expected:** Category names change to Thai equivalents. Table layout unchanged.

### 2. Scoring conclusion renders in selected language (post-i18n evaluation)

1. Set language toggle to **ID**
2. Open an evaluation that was scored after i18n support was added
3. Scroll to Calculator Results → find "Kesimpulan" section
4. Note the conclusion bullet points, marketing budget text, and closing message
5. Switch language toggle to **EN**
6. **Expected:** "Kesimpulan" heading changes to English equivalent. Conclusion bullet points, marketing budget, and closing message all render in English. Currency values remain correct.
7. Switch language toggle to **TH**
8. **Expected:** All three text sections render in Thai.

### 3. Pre-i18n evaluation shows raw Indonesian text

1. Set language toggle to **EN**
2. Open an evaluation that was scored before i18n support (lacks `_i18n` fields)
3. Scroll to Score Breakdown table
4. **Expected:** Category names display as Indonesian text (from CATEGORY_MAP translation via t() — the mapped categories should still translate). Unknown/unmapped categories show raw backend strings.
5. Scroll to Calculator Results section
6. **Expected:** If scoring_summary is absent, no "Kesimpulan" section appears. No errors, no blank sections.

### 4. Marketplace field present in API response

1. Open browser DevTools → Network tab
2. Navigate to any evaluation detail page
3. Find the `GET /api/v1/evaluations/{id}` request
4. Inspect response JSON
5. **Expected:** Response contains `"marketplace"` field with value `"ID"` or `"TH"` (never null, never missing)

### 5. Missing scoring_summary renders cleanly

1. Open any evaluation from before the i18n system was added
2. Open browser DevTools → Console tab
3. **Expected:** No JavaScript errors related to scoring_summary, renderTranslatable, or undefined property access. Page renders normally with all existing sections (score breakdown, discount, top SKU, ads keyword) intact.

## Edge Cases

### Unknown category name in score breakdown

1. If a future backend change adds a new category name not in CATEGORY_MAP
2. **Expected:** The raw backend string renders as-is in the table cell. No error, no blank cell.

### Evaluation with partial scoring_summary (some _i18n fields missing)

1. Open an evaluation where scoring_summary exists but some `_i18n` fields are absent (e.g. `marketing_budget_i18n` is null)
2. **Expected:** Fields with `_i18n` render translated; fields without `_i18n` fall back to raw string value. No errors.

### Rapid language switching

1. Open an evaluation detail page with scoring_summary
2. Quickly toggle ID → EN → TH → ID
3. **Expected:** Text updates reactively each time. No stale text, no layout shift, no console errors.

## Failure Signals

- **Blank category cells** in Score Breakdown table → CATEGORY_MAP import or lookup broken
- **"Kesimpulan" section missing** on a post-i18n evaluation → isScoringSummary() type guard rejecting valid data
- **Console errors** mentioning "Cannot read property of undefined" → scoring_summary field access without null check
- **Text not changing** when switching languages → renderTranslatable() not receiving the `t` function correctly, or _i18n fields not present in stored data
- **Raw i18n keys visible** (e.g. `scoring.conclusion.item1`) → locale file missing key, or t() returning key instead of translation
- **"marketplace" missing from API response** → backend SQL/service/schema wiring broken

## Requirements Proved By This UAT

- **R014** — Test cases 1, 2, 3 prove scoring text renders in active UI language with graceful fallback
- **R018** — Test case 4 proves API returns marketplace field
- **R019** — Test cases 3, 5 prove pre-i18n evaluations display without errors

## Not Proven By This UAT

- **R015** — Email language selector (S03 scope)
- **R016** — Email body rebuilt from i18n keys (S03 scope)
- **R017** — Locale file {{currency}} cleanup (S04 scope)
- **R020** — Adding a new language requires only locale JSON (S04 scope)
- **R014 full validation** — This UAT proves the wiring works; full validation requires confirming all scoring message types translate correctly across all 3 languages (which depends on locale file completeness)

## Notes for Tester

- The test i18n mock in automated tests returns translation keys (not actual translated strings). This UAT is the place where you verify actual Indonesian/English/Thai strings appear correctly.
- "Kesimpulan" is the Indonesian word for "Conclusion" — when switching to EN, this heading should change.
- The marketing budget line is labeled "Min. Anggaran Marketing" in Indonesian — verify it changes in EN/TH.
- Pre-i18n evaluations may be identified by their creation date (before the i18n scoring engine update) or by checking `calculator_results.scoring_summary` is absent in the API response JSON.
- Category translation via CATEGORY_MAP covers the standard categories (Operasional, Bisnis, Alat Promo, etc.). Custom or experimental categories will show raw text — this is expected behavior, not a bug.
