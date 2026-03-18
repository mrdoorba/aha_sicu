---
id: T02
parent: S03
milestone: M002
provides:
  - buildI18nEmailBody utility mirroring backend _assemble_email_body section ordering with i18n support
  - buildI18nEmailSubject utility for translated email subjects
  - ScoringConclusionData type exported for downstream dialogs
  - EmailLanguageSelector wired into SendEmailDialog with language flowing to mutation + preview URL
  - Backend preview endpoint accepts optional language query param
  - emailBody.section.* locale keys in all 3 locale files (en/id/th)
key_files:
  - frontend/src/utils/buildI18nEmailBody.ts
  - frontend/src/utils/buildI18nEmailBody.test.ts
  - frontend/src/components/dashboard/SendEmailDialog.tsx
  - frontend/src/components/dashboard/SendEmailDialog.test.tsx
  - backend/app/modules/email/router.py
  - frontend/src/locales/en.json
  - frontend/src/locales/id.json
  - frontend/src/locales/th.json
key_decisions:
  - Used dedicated emailBody.section.* locale keys for email section headers instead of reusing rules.category.* keys — the email headers differ from the category names (e.g. "Store Operational Performance" vs "Operations")
  - Promo row filter uses actual backend constants (PROMO_START_ROW=31, 11 tools → rows 31-41 + summary 42,43) rather than the plan's stated "rows 34-41" which was incorrect
patterns_established:
  - SECTION_DEFS array in buildI18nEmailBody.ts as declarative definition of email section ordering, row filters, and emoji prefixes — mirrors backend _assemble_email_body exactly
  - fetchPreview uses URLSearchParams for clean query string construction with language param
observability_surfaces:
  - data-testid="email-language-select" in SendEmailDialog for test/automation targeting
  - Preview endpoint accepts ?language=th|en|id query param for testing email preview in specific languages
  - buildI18nEmailBody is a pure function — verify via npx vitest run src/utils/buildI18nEmailBody.test.ts
duration: 20m
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T02: Create buildI18nEmailBody utility + wire SendEmailDialog language selector

**Add buildI18nEmailBody/buildI18nEmailSubject utilities mirroring backend email assembly with i18n support, wire EmailLanguageSelector into SendEmailDialog, and add language query param to backend preview endpoint — 20 new tests passing, full regression 588/588.**

## What Happened

1. **Added `emailBody.section.*` locale keys** to all 3 locale files (en/id/th) for 10 email section headers: operational, business, visitors, promoTools, productsStatus, ads, campaign, competition, conclusion, marketingEstimation.

2. **Created `frontend/src/utils/buildI18nEmailBody.ts`** with three exports:
   - `ScoringConclusionData` interface — typing for scoring summary fields used in email assembly
   - `buildI18nEmailSubject(brandName, period, t)` — returns translated subject using `t('sendMailUtils.subject', ...)`
   - `buildI18nEmailBody(categoryScores, scoringSummary, t)` — mirrors backend `_assemble_email_body` exactly:
     - 8 category sections with correct emoji prefixes and row filters
     - Promo section uses rows 31-41 (tool rows) + 42,43 (summary rows)
     - Business rows 13, 20; Visitors 28, 29; Ads 50-53; Campaign 57
     - Uses `renderTranslatable()` for each row message (i18n → raw fallback)
     - Conclusion, marketing estimation, marketing budget, closing message sections from `scoringSummary`
     - Null `scoringSummary` gracefully omits conclusion/marketing/closing sections

3. **Wrote 20 unit tests** in `buildI18nEmailBody.test.ts` covering: section ordering, row filtering for all filtered sections (business, visitors, ads, campaign, promo), i18n translation, raw fallback, conclusion/marketing/budget/closing rendering, null summary handling, empty categories, and full integration ordering.

4. **Wired `SendEmailDialog`** with `EmailLanguageSelector`:
   - Added `emailLanguage` state defaulting to `i18n.language`
   - Placed selector between recipient section and note section
   - `handleSend` passes `language: emailLanguage` in mutation payload
   - `fetchPreview` uses `URLSearchParams` to include `language` param alongside `note`
   - `handleClose` resets `emailLanguage` to `i18n.language`

5. **Updated backend preview endpoint** in `router.py`:
   - Added `language: str | None = Query(default=None)` parameter
   - Resolution: `lang = language or current_user.get("language", "id")`
   - Uses `lang` variable consistently for both `_chart_placeholder_svg` and `render_email_html`

6. **Added 4 new tests** to `SendEmailDialog.test.tsx`: language selector renders, mutation payload includes default language, mutation payload includes changed language, preview URL includes language param.

## Verification

- `buildI18nEmailBody.test.ts`: 20/20 passed
- `SendEmailDialog.test.tsx`: 22/22 passed (18 existing + 4 new)
- Full regression: 66 test files, 588 tests passed, 1 skipped, 0 failures
- Backend import check: `preview_email_endpoint` imports successfully with new `language` param

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `cd frontend && npx vitest run src/utils/buildI18nEmailBody.test.ts --reporter=verbose` | 0 | ✅ pass | 0.9s |
| 2 | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx --reporter=verbose` | 0 | ✅ pass | 1.8s |
| 3 | `cd frontend && npx vitest run --reporter=verbose 2>&1 \| tail -5` | 0 | ✅ pass | 31.6s |
| 4 | `PYTHONPATH=backend python -c "from app.modules.email.router import preview_email_endpoint; print('OK')"` | 0 | ✅ pass | 27.6s |

### Slice-level verification (partial — T02 is second of 3 tasks)

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | EmailLanguageSelector.test.tsx | ✅ pass | 8/8 tests (T01) |
| 2 | buildI18nEmailBody.test.ts | ✅ pass | 20/20 tests (T02) |
| 3 | SendMailDialog.test.tsx (evaluations) | ✅ pass | 14/14 tests (existing, T03 will add more) |
| 4 | SendEmailDialog.test.tsx (dashboard) | ✅ pass | 22/22 tests (T02) |
| 5 | EmailOutput.test.tsx | ✅ pass | 4/4 tests (existing, T03 will add more) |
| 6 | Full regression | ✅ pass | 588 passed, 0 failures |
| 7 | Backend preview endpoint test | ⏳ not applicable | No integration test file exists |

## Diagnostics

- **buildI18nEmailBody:** Pure function with no runtime side effects. Validate via test suite. If section ordering is wrong, compare `SECTION_DEFS` array against backend `_assemble_email_body` in `computations.py:328-440`.
- **SendEmailDialog language selector:** Visible as native `<select>` with `data-testid="email-language-select"`. The selected value flows to: (a) `mutate()` payload's `language` field, (b) preview URL as `?language=X` query param.
- **Backend preview endpoint:** The `language` query param is optional. When absent, falls back to `current_user.get("language", "id")`. Test with: `GET /api/v1/email/preview/123?language=th`.
- **Locale keys:** New `emailBody.section.*` keys in all 3 locale files. If a section header appears untranslated, check the locale JSON for the corresponding key.

## Deviations

- **Promo row filter corrected:** The plan stated "rows 34-41" but the actual backend uses `PROMO_START_ROW=31` with 11 tools (rows 31-41) plus summary rows 42, 43. Followed the actual backend logic, not the plan's incorrect row numbers.
- **Added emailBody.section.\* locale keys:** The plan didn't explicitly mention adding new locale keys for email section headers, but they were needed because the backend hardcodes Indonesian header text, and we need translatable versions. Used descriptive keys matching the backend section names.

## Known Issues

None.

## Files Created/Modified

- `frontend/src/utils/buildI18nEmailBody.ts` — **new** utility with `buildI18nEmailBody`, `buildI18nEmailSubject`, `ScoringConclusionData` type
- `frontend/src/utils/buildI18nEmailBody.test.ts` — **new** 20 comprehensive unit tests
- `frontend/src/components/dashboard/SendEmailDialog.tsx` — added EmailLanguageSelector, emailLanguage state, wired to mutation + preview
- `frontend/src/components/dashboard/SendEmailDialog.test.tsx` — added 4 new tests for language selector integration
- `backend/app/modules/email/router.py` — added optional `language` query param to preview endpoint
- `frontend/src/locales/en.json` — added `emailBody.section.*` keys (10 section headers)
- `frontend/src/locales/id.json` — added `emailBody.section.*` keys (10 section headers)
- `frontend/src/locales/th.json` — added `emailBody.section.*` keys (10 section headers)
- `.gsd/milestones/M002/slices/S03/tasks/T02-PLAN.md` — added Observability Impact section (pre-flight fix)
