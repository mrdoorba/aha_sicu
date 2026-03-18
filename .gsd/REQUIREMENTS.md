# Requirements

This file is the explicit capability and coverage contract for the project.

## Validated

### R014 — When a user views an evaluation in the history detail page, all scoring messages, category names, conclusions, closing messages, and marketing budget text render in the currently selected UI language (ID/EN/TH).
- Class: core-capability
- Status: validated
- Description: When a user views an evaluation in the history detail page, all scoring messages, category names, conclusions, closing messages, and marketing budget text render in the currently selected UI language (ID/EN/TH).
- Why it matters: This is the primary page staff use to review and share evaluation results. Indonesian-only output makes the system unusable for Thai staff and limits English-speaking reviewers.
- Source: user
- Primary owning slice: M002/S01
- Supporting slices: none
- Validation: EvaluationDetailPage renders category names via CATEGORY_MAP + t(), conclusion/marketing_budget/closing_message via renderTranslatable() + ScoringConclusionSection. 25 EvaluationDetailPage tests pass including 5 i18n-specific. ScoreBreakdownTable translates categories with raw-string fallback. Pre-i18n evaluations fall back to raw Indonesian text.
- Notes: Must use stored i18n keys when present; fall back to raw text for pre-i18n evaluations.

### R015 — All email send dialogs (history detail SendMailDialog, dashboard SendEmailDialog, evaluation page EmailOutput) include a language dropdown that lets the user choose the email language independently of the UI language, defaulting to the current UI language.
- Class: core-capability
- Status: validated
- Description: All email send dialogs (history detail SendMailDialog, dashboard SendEmailDialog, evaluation page EmailOutput) include a language dropdown that lets the user choose the email language independently of the UI language, defaulting to the current UI language.
- Why it matters: Emails cross language boundaries — Thai staff may send to Indonesian brand owners. The email language must be decoupled from the UI language.
- Source: user
- Primary owning slice: M002/S03
- Supporting slices: none
- Validation: validated
- Notes: Dashboard SendEmailDialog already sends language to backend; needs UI selector. History SendMailDialog uses mailto — needs frontend-side i18n rendering.

### R016 — Email body content is reconstructed from stored i18n structured data at render time in the chosen language, rather than displaying the pre-rendered Indonesian email_output string.
- Class: core-capability
- Status: validated
- Description: Email body content is reconstructed from stored i18n structured data at render time in the chosen language, rather than displaying the pre-rendered Indonesian email_output string.
- Why it matters: Pre-rendered email_output is always Indonesian. To support language switching, the email body must be assembled dynamically from i18n keys.
- Source: user
- Primary owning slice: M002/S03
- Supporting slices: M002/S01
- Validation: validated
- Notes: The pre-rendered email_output in DB becomes a fallback for old evaluations without i18n data.

### R017 — All locale translation strings that reference currency use the {{currency}} interpolation variable (already provided by the backend) instead of hardcoded "IDR".
- Class: quality-attribute
- Status: validated
- Description: All locale translation strings that reference currency use the {{currency}} interpolation variable (already provided by the backend) instead of hardcoded "IDR".
- Why it matters: Hardcoded IDR in locale strings produces incorrect output for THB marketplace evaluations when viewed in EN or TH.
- Source: inferred
- Primary owning slice: M002/S03
- Supporting slices: none
- Validation: validated
- Notes: 6 keys across all 3 locale files affected.

### R018 — The GET evaluation detail API response includes the marketplace field from the evaluations table.
- Class: integration
- Status: validated
- Description: The GET evaluation detail API response includes the marketplace field from the evaluations table.
- Why it matters: Frontend needs marketplace to determine currency code for formatting and to pass to i18n variable resolution.
- Source: inferred
- Primary owning slice: M002/S01
- Supporting slices: none
- Validation: validated
- Notes: Triple-layer fallback (SQL COALESCE → service row.get → Pydantic default) ensures non-null.

### R019 — Evaluations saved before the i18n system was added (which lack _i18n fields in score_breakdown) display their original Indonesian text. Evaluations with i18n keys translate. No evaluation becomes unreadable.
- Class: continuity
- Status: validated
- Description: Evaluations saved before the i18n system was added (which lack _i18n fields in score_breakdown) display their original Indonesian text. Evaluations with i18n keys translate. No evaluation becomes unreadable.
- Why it matters: Data continuity — staff must be able to view all historical evaluations without errors or blank fields.
- Source: user
- Primary owning slice: M002/S01
- Supporting slices: none
- Validation: validated
- Notes: renderTranslatable() pattern already handles this — falls back to raw text when i18n is null/undefined.

### R020 — After M002 is complete, adding a 4th language to the system requires only: (a) creating a new locale JSON file, (b) adding its import to i18n.ts, (c) adding it to the LanguageToggle LANGUAGES array and backend STRINGS/CATEGORY_MAP. No schema changes, no migrations, no new components.
- Class: quality-attribute
- Status: validated
- Description: After M002 is complete, adding a 4th language to the system requires only: (a) creating a new locale JSON file, (b) adding its import to i18n.ts, (c) adding it to the LanguageToggle LANGUAGES array and backend STRINGS/CATEGORY_MAP. No schema changes, no migrations, no new components.
- Why it matters: The user explicitly wants future language additions to be trivial.
- Source: user
- Primary owning slice: M002/S03
- Supporting slices: M002/S01, M002/S02
- Validation: validated
- Notes: Documented in docs/adding-a-language.md.

### R021 — TypeScript interfaces for RowScore, CategoryScore, and ScoringResult in useScoring.ts and useEvaluationDetail.ts explicitly declare _i18n fields.
- Class: quality-attribute
- Status: validated
- Description: TypeScript interfaces for RowScore, CategoryScore, and ScoringResult in useScoring.ts and useEvaluationDetail.ts explicitly declare _i18n fields.
- Why it matters: Explicit types prevent accidental stripping and enable IDE support.
- Source: inferred
- Primary owning slice: M002/S01
- Supporting slices: none
- Validation: validated
- Notes: Low risk — additive type changes only.

### R022 — All database schema changes in M002 are additive only. No existing data is modified, deleted, or migrated destructively.
- Class: constraint
- Status: validated
- Description: All database schema changes in M002 are additive only. No existing data is modified, deleted, or migrated destructively.
- Why it matters: User explicitly requires zero data loss.
- Source: user
- Primary owning slice: M002
- Supporting slices: none
- Validation: validated
- Notes: M002 made zero database schema changes.

### R023 — The follower count threshold display in scoring messages uses international comma convention (>50,000) instead of Indonesian dot convention (>50.000).
- Class: quality-attribute
- Status: validated
- Description: The follower count threshold display in scoring messages uses international comma convention (>50,000) instead of Indonesian dot convention (>50.000).
- Why it matters: Dot-as-thousands-separator is Indonesian locale-specific.
- Source: user
- Primary owning slice: M003/S01
- Supporting slices: none
- Validation: validated
- Notes: Affects rules.py, messages.py inline fallback, and DB migration 028.

### R024 — The follower count value displayed in scoring messages uses comma as thousands separator instead of being converted from comma to dot.
- Class: quality-attribute
- Status: validated
- Description: The follower count value displayed in scoring messages uses comma as thousands separator instead of being converted from comma to dot.
- Why it matters: The .replace(",", ".") forced Indonesian number formatting on all marketplaces.
- Source: user
- Primary owning slice: M003/S01
- Supporting slices: none
- Validation: validated
- Notes: Single line change in messages.py.

### R025 — The BOTTOM ads cost floor in ads_keyword.py uses marketplace-appropriate values.
- Class: core-capability
- Status: validated
- Description: The BOTTOM ads cost floor in ads_keyword.py uses marketplace-appropriate values.
- Why it matters: 100,000 THB is far too high for Thai marketplace ads.
- Source: user
- Primary owning slice: M003/S01
- Supporting slices: none
- Validation: validated
- Notes: Uses IDR_TO_THB_RATE from marketplace.py.

### R026 — The sales range conclusion continues to divide by 1,000,000 and append "juta" for ID. THB uses raw comma-formatted numbers.
- Class: constraint
- Status: validated
- Description: The sales range conclusion continues to divide by 1,000,000 and append "juta" for ID. THB uses raw comma-formatted numbers.
- Why it matters: Juta is the correct Indonesian convention for large IDR amounts.
- Source: user
- Primary owning slice: M003/S01
- Supporting slices: none
- Validation: validated
- Notes: No code change needed — existing branching is correct.

### R027 — All UI strings in EvaluationHistoryTable, DeleteEvaluationDialog, DowntimeWarningDialog, and SelectField use i18n `t()` calls with keys from locale files instead of hardcoded Indonesian text.
- Class: core-capability
- Status: validated
- Description: All UI strings in EvaluationHistoryTable, DeleteEvaluationDialog, DowntimeWarningDialog, and SelectField use i18n `t()` calls with keys from locale files instead of hardcoded Indonesian text.
- Why it matters: These 4 components render entirely in Indonesian regardless of language selection — the History page is completely broken for Thai/English users.
- Source: user
- Primary owning slice: M004/S01
- Supporting slices: none
- Validation: All 4 target components use t() for every visible string. 34 new locale keys across 3 JSON files. rg for hardcoded Indonesian in all 4 components returns zero hits. 612 frontend tests pass with key-based assertions.
- Notes: ~40 hardcoded strings across 4 components. EvaluationHistoryTable is the largest (~25 strings).

### R028 — All 8 files with hardcoded `Intl.DateTimeFormat('id-ID', ...)` or `toLocaleDateString('id-ID', ...)` use the active i18n language to determine the Intl locale.
- Class: core-capability
- Status: validated
- Description: All 8 files with hardcoded `Intl.DateTimeFormat('id-ID', ...)` or `toLocaleDateString('id-ID', ...)` use the active i18n language to determine the Intl locale.
- Why it matters: Dates always display in Indonesian format regardless of language selection. Thai users see Indonesian month names and formatting.
- Source: user
- Primary owning slice: M004/S02
- Supporting slices: none
- Validation: All 8 affected files (EvaluationHistoryTable, AccountsPage, EvaluationDetailPage, DashboardFooter, BusinessForm, DiscountResults, TopSkuResults, AdsKeywordResults) use getIntlLocale(i18n.language) for date/number formatting. rg "id-ID" frontend/src | grep -v test | grep -v locale | grep -v localeMap returns zero hits. 612 frontend tests pass.
- Notes: Affected files: EvaluationHistoryTable, AccountsPage, EvaluationDetailPage, DashboardFooter, BusinessForm, DiscountResults, TopSkuResults, AdsKeywordResults. Need a locale mapping util (id→id-ID, en→en-US, th→th-TH).

### R029 — All 51 field labels in fields.ts, the GENERIC_LABELS array, and the 2 hardcoded labels in DiscountResults.tsx use `t()` calls with locale file keys instead of hardcoded Indonesian text.
- Class: core-capability
- Status: validated
- Description: All 51 field labels in fields.ts, the GENERIC_LABELS array, and the 2 hardcoded labels in DiscountResults.tsx use `t()` calls with locale file keys instead of hardcoded Indonesian text.
- Why it matters: Every evaluation form renders Indonesian field labels regardless of language. This is the largest single batch of untranslated strings.
- Source: user
- Primary owning slice: M004/S02
- Supporting slices: none
- Validation: All 47 field labels resolve through t(field.labelKey!) in 7 form components + EvaluationDetailPage. GENERIC_LABELS contains i18n keys resolved via t(). DiscountResults uses t() for all visible strings. rg for hardcoded Indonesian labels in form components and EvaluationDetailPage returns zero rendered-string hits. 612 tests pass.
- Notes: Plan estimated 51 fields; actual codebase has 47. All 47 have labelKey. DiscountResults 2 hardcoded labels extracted to discount.* keys.

### R030 — INDO_MONTHS array uses standard English month abbreviations (Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec) instead of Indonesian ones (Mei→May, Agu→Aug, Okt→Oct, Des→Dec). Same across all languages.
- Class: quality-attribute
- Status: validated
- Description: INDO_MONTHS array uses standard English month abbreviations (Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec) instead of Indonesian ones (Mei→May, Agu→Aug, Okt→Oct, Des→Dec). Same across all languages.
- Why it matters: User explicitly requested English months for all languages — simpler, no per-locale month names needed.
- Source: user
- Primary owning slice: M004/S02
- Supporting slices: none
- Validation: INDO_MONTHS renamed to MONTHS with English abbreviations: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec. rg "INDO_MONTHS" returns zero hits. formConfig.test.ts validates all 12 month abbreviations. 4 corrections applied: Mei→May, Agu→Aug, Okt→Oct, Des→Dec.
- Notes: Only 4 values actually change: Mei→May, Agu→Aug, Okt→Oct, Des→Dec. Rename constant from INDO_MONTHS to MONTHS.

### R031 — Zero hardcoded Indonesian UI text remains in .tsx/.ts source files (excluding test files and locale files). A professional translator edits only their one locale JSON file to translate the entire application.
- Class: quality-attribute
- Status: validated
- Description: Zero hardcoded Indonesian UI text remains in .tsx/.ts source files (excluding test files and locale files). A professional translator edits only their one locale JSON file to translate the entire application.
- Why it matters: User explicitly wants one-file-per-language workflow for professional translators. Currently ~100 strings are buried in source code.
- Source: user
- Primary owning slice: M004/S03
- Supporting slices: M004/S01, M004/S02
- Validation: Full rg sweep for 55 common Indonesian words across all non-test, non-locale .tsx/.ts source files returns zero rendered-string hits. All remaining hits are classified as: (a) inert `label`/`benchmark`/`displayName` properties in fields.ts — dead code, resolved via labelKey/benchmarkKey/displayNameKey at render time; (b) code comments in JSX; (c) backend column name matchers (categoryMap.ts, buildI18nEmailBody.ts, DetailedEvaluation.tsx, PresentationDashboard.tsx, CategoryMetricCard.tsx, EvaluationDetailPage.tsx shortLabel regex); (d) i18n key strings containing Indonesian words (topSku.totalOmzet, topSku.namaProduk, etc.); (e) TypeScript property names (promoToko, paketDiskon, etc.). 720 locale keys across 3 JSON files (id, en, th) in perfect sync. A translator edits only their one locale JSON file to fully localize the app.
- Notes: Verified by grep/rg sweep for Indonesian words in non-test, non-locale source files.

### R032 — All existing frontend tests pass after i18n extraction, with test assertions updated to use translation key patterns where needed.
- Class: quality-attribute
- Status: validated
- Description: All existing frontend tests pass after i18n extraction, with test assertions updated to use translation key patterns where needed.
- Why it matters: Tests currently assert hardcoded Indonesian strings — they'll break when strings move to locale files. Tests need updating in lockstep.
- Source: inferred
- Primary owning slice: M004/S03
- Supporting slices: M004/S01, M004/S02
- Validation: 612/612 frontend tests pass across 68 test files after all i18n extraction. Test assertions updated in lockstep: SectionNav.test.tsx assertions updated from hardcoded Indonesian labels to i18n key strings, PromoToolsForm.test.tsx benchmark assertions updated to key strings, EvaluationHistoryTable.test.tsx assertions updated in S01. All updates use the established vi.mock('react-i18next') pattern where mock t() returns key as-is, making assertions stable against locale changes.
- Notes: EvaluationHistoryTable.test.tsx has the most assertions against hardcoded Indonesian text. Other test files may be affected by fields.ts label changes.

## Out of Scope

### R033 — No automatic currency conversion. Thresholds are set manually.
- Class: constraint
- Status: out-of-scope
- Description: No automatic currency conversion. Thresholds are set manually.
- Why it matters: Prevents scope creep into financial data integration.
- Source: user
- Primary owning slice: none
- Supporting slices: none
- Validation: n/a
- Notes: Established in M001.

## Traceability

| ID | Class | Status | Primary owner | Supporting | Proof |
|---|---|---|---|---|---|
| R014 | core-capability | validated | M002/S01 | none | EvaluationDetailPage renders category names via CATEGORY_MAP + t(), conclusion/marketing_budget/closing_message via renderTranslatable() + ScoringConclusionSection. 25 EvaluationDetailPage tests pass including 5 i18n-specific. ScoreBreakdownTable translates categories with raw-string fallback. Pre-i18n evaluations fall back to raw Indonesian text. |
| R015 | core-capability | validated | M002/S03 | none | validated |
| R016 | core-capability | validated | M002/S03 | M002/S01 | validated |
| R017 | quality-attribute | validated | M002/S03 | none | validated |
| R018 | integration | validated | M002/S01 | none | validated |
| R019 | continuity | validated | M002/S01 | none | validated |
| R020 | quality-attribute | validated | M002/S03 | M002/S01, M002/S02 | validated |
| R021 | quality-attribute | validated | M002/S01 | none | validated |
| R022 | constraint | validated | M002 | none | validated |
| R023 | quality-attribute | validated | M003/S01 | none | validated |
| R024 | quality-attribute | validated | M003/S01 | none | validated |
| R025 | core-capability | validated | M003/S01 | none | validated |
| R026 | constraint | validated | M003/S01 | none | validated |
| R027 | core-capability | validated | M004/S01 | none | All 4 target components use t() for every visible string. 34 new locale keys across 3 JSON files. rg for hardcoded Indonesian in all 4 components returns zero hits. 612 frontend tests pass with key-based assertions. |
| R028 | core-capability | validated | M004/S02 | none | All 8 affected files (EvaluationHistoryTable, AccountsPage, EvaluationDetailPage, DashboardFooter, BusinessForm, DiscountResults, TopSkuResults, AdsKeywordResults) use getIntlLocale(i18n.language) for date/number formatting. rg "id-ID" frontend/src | grep -v test | grep -v locale | grep -v localeMap returns zero hits. 612 frontend tests pass. |
| R029 | core-capability | validated | M004/S02 | none | All 47 field labels resolve through t(field.labelKey!) in 7 form components + EvaluationDetailPage. GENERIC_LABELS contains i18n keys resolved via t(). DiscountResults uses t() for all visible strings. rg for hardcoded Indonesian labels in form components and EvaluationDetailPage returns zero rendered-string hits. 612 tests pass. |
| R030 | quality-attribute | validated | M004/S02 | none | INDO_MONTHS renamed to MONTHS with English abbreviations: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec. rg "INDO_MONTHS" returns zero hits. formConfig.test.ts validates all 12 month abbreviations. 4 corrections applied: Mei→May, Agu→Aug, Okt→Oct, Des→Dec. |
| R031 | quality-attribute | validated | M004/S03 | M004/S01, M004/S02 | Full rg sweep for 55 common Indonesian words across all non-test, non-locale .tsx/.ts source files returns zero rendered-string hits. All remaining hits are classified as: (a) inert `label`/`benchmark`/`displayName` properties in fields.ts — dead code, resolved via labelKey/benchmarkKey/displayNameKey at render time; (b) code comments in JSX; (c) backend column name matchers (categoryMap.ts, buildI18nEmailBody.ts, DetailedEvaluation.tsx, PresentationDashboard.tsx, CategoryMetricCard.tsx, EvaluationDetailPage.tsx shortLabel regex); (d) i18n key strings containing Indonesian words (topSku.totalOmzet, topSku.namaProduk, etc.); (e) TypeScript property names (promoToko, paketDiskon, etc.). 720 locale keys across 3 JSON files (id, en, th) in perfect sync. A translator edits only their one locale JSON file to fully localize the app. |
| R032 | quality-attribute | validated | M004/S03 | M004/S01, M004/S02 | 612/612 frontend tests pass across 68 test files after all i18n extraction. Test assertions updated in lockstep: SectionNav.test.tsx assertions updated from hardcoded Indonesian labels to i18n key strings, PromoToolsForm.test.tsx benchmark assertions updated to key strings, EvaluationHistoryTable.test.tsx assertions updated in S01. All updates use the established vi.mock('react-i18next') pattern where mock t() returns key as-is, making assertions stable against locale changes. |
| R033 | constraint | out-of-scope | none | none | n/a |

## Coverage Summary

- Active requirements: 0
- Mapped to slices: 0
- Validated: 19 (R014, R015, R016, R017, R018, R019, R020, R021, R022, R023, R024, R025, R026, R027, R028, R029, R030, R031, R032)
- Unmapped active requirements: 0
