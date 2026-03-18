# Requirements

This file is the explicit capability and coverage contract for the project.

## Active

### R034 — Ads keyword section on evaluation detail page renders translated from i18n structured data
- Class: core-capability
- Status: active
- Description: The AdsKeywordSection on EvaluationDetailPage renders ads keyword output from structured i18n details (ak2_i18n, ak3_i18n, ak4_i18n, al2_i18n, etc.) instead of raw Indonesian output_text. Falls back to output_text when details are unavailable.
- Why it matters: Ads keyword output is currently a raw Indonesian string dumped into a <pre> block, unreadable for Thai/English users.
- Source: user
- Primary owning slice: M005/S01
- Supporting slices: none
- Validation: unmapped
- Notes: Dashboard DataIntelligence.tsx already implements this pattern — reuse renderTranslatable/renderAdList/renderFlagList.

### R035 — Discount section on evaluation detail page renders translated from i18n structured data
- Class: core-capability
- Status: active
- Description: The DiscountSection on EvaluationDetailPage renders discount output from i18n structured data (scoring.discountCheckup.pass/fail keys with interpolation vars) instead of raw Indonesian output_text. Falls back to output_text when i18n data is unavailable.
- Why it matters: Discount output is currently a raw Indonesian string ("% Diskon TOP SKU:", "Paket Diskon", "📌 Berpotensi menggunakan 'fake discount'"), unreadable for Thai/English users.
- Source: user
- Primary owning slice: M005/S01
- Supporting slices: none
- Validation: unmapped
- Notes: Backend already generates value_i18n on discount row 73 with scoring.discountCheckup.pass/fail keys. Locale keys exist in all 3 languages.

### R036 — Email output section on evaluation detail page renders scoring messages in selected language
- Class: core-capability
- Status: active
- Description: The EmailOutputSection on EvaluationDetailPage reconstructs the email body from score_breakdown i18n data using buildI18nEmailBody, rendering all scoring messages (operational, business, visitor, promo, ads, campaign, competition, conclusion) in the active UI language instead of displaying the pre-rendered Indonesian email_output string.
- Why it matters: The email output section shows the full scoring report — section headers ("Performa Operasional Toko:"), per-row messages ("❌ Tingkat Pesanan Tidak Terselesaikan = 1.4%"), conclusion, and marketing budget — all in Indonesian regardless of language selection.
- Source: user
- Primary owning slice: M005/S02
- Supporting slices: M005/S01
- Validation: unmapped
- Notes: buildI18nEmailBody.ts already exists and is used by SendMailDialog. Reuse the same pattern with i18n.language as the rendering language.

### R037 — Pre-i18n evaluations (without message_i18n data) fall back to raw Indonesian text without errors
- Class: continuity
- Status: active
- Description: Evaluations saved before the i18n system was added (which lack _i18n fields in score_breakdown and details) display their original Indonesian text on the evaluation detail page. No evaluation becomes unreadable or errors out.
- Why it matters: Data continuity — staff must be able to view all historical evaluations without errors or blank fields.
- Source: inferred
- Primary owning slice: M005/S01
- Supporting slices: M005/S02
- Validation: unmapped
- Notes: renderTranslatable() already handles fallback. AdsContent in DataIntelligence.tsx falls back to output_text when details are missing — same pattern applies.

### R038 — All existing frontend tests pass after detail page i18n changes
- Class: quality-attribute
- Status: active
- Description: All existing frontend tests pass after the evaluation detail page i18n rendering changes, with test assertions updated where needed.
- Why it matters: Ensures no regressions from rendering changes on the detail page.
- Source: inferred
- Primary owning slice: M005/S02
- Supporting slices: M005/S01
- Validation: unmapped
- Notes: EvaluationDetailPage.test.tsx may need updated assertions if mock data shape changes.

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
- Validation: All 8 affected files use getIntlLocale(i18n.language) for date/number formatting. rg "id-ID" returns zero hits in source. 612 frontend tests pass.
- Notes: Affected files: EvaluationHistoryTable, AccountsPage, EvaluationDetailPage, DashboardFooter, BusinessForm, DiscountResults, TopSkuResults, AdsKeywordResults.

### R029 — All 51 field labels in fields.ts, the GENERIC_LABELS array, and the 2 hardcoded labels in DiscountResults.tsx use `t()` calls with locale file keys instead of hardcoded Indonesian text.
- Class: core-capability
- Status: validated
- Description: All 51 field labels in fields.ts, the GENERIC_LABELS array, and the 2 hardcoded labels in DiscountResults.tsx use `t()` calls with locale file keys instead of hardcoded Indonesian text.
- Why it matters: Every evaluation form renders Indonesian field labels regardless of language. This is the largest single batch of untranslated strings.
- Source: user
- Primary owning slice: M004/S02
- Supporting slices: none
- Validation: All 47 field labels resolve through t(field.labelKey!) in 7 form components + EvaluationDetailPage. 612 tests pass.
- Notes: Plan estimated 51 fields; actual codebase has 47.

### R030 — INDO_MONTHS array uses standard English month abbreviations (Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec) instead of Indonesian ones.
- Class: quality-attribute
- Status: validated
- Description: INDO_MONTHS array uses standard English month abbreviations instead of Indonesian ones. Same across all languages.
- Why it matters: User explicitly requested English months for all languages.
- Source: user
- Primary owning slice: M004/S02
- Supporting slices: none
- Validation: INDO_MONTHS renamed to MONTHS with English abbreviations. 4 corrections applied: Mei→May, Agu→Aug, Okt→Oct, Des→Dec.
- Notes: Only 4 values actually change.

### R031 — Zero hardcoded Indonesian UI text remains in .tsx/.ts source files (excluding test files and locale files).
- Class: quality-attribute
- Status: validated
- Description: Zero hardcoded Indonesian UI text remains in .tsx/.ts source files (excluding test files and locale files). A professional translator edits only their one locale JSON file to translate the entire application.
- Why it matters: User explicitly wants one-file-per-language workflow for professional translators.
- Source: user
- Primary owning slice: M004/S03
- Supporting slices: M004/S01, M004/S02
- Validation: Full rg sweep returns zero rendered-string hits. 720 locale keys across 3 JSON files in perfect sync.
- Notes: Verified by grep/rg sweep for Indonesian words in non-test, non-locale source files.

### R032 — All existing frontend tests pass after i18n extraction, with test assertions updated to use translation key patterns where needed.
- Class: quality-attribute
- Status: validated
- Description: All existing frontend tests pass after i18n extraction, with test assertions updated to use translation key patterns where needed.
- Why it matters: Tests currently assert hardcoded Indonesian strings — they'll break when strings move to locale files.
- Source: inferred
- Primary owning slice: M004/S03
- Supporting slices: M004/S01, M004/S02
- Validation: 612/612 frontend tests pass across 68 test files.
- Notes: All updates use the established vi.mock('react-i18next') pattern.

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
| R034 | core-capability | active | M005/S01 | none | unmapped |
| R035 | core-capability | active | M005/S01 | none | unmapped |
| R036 | core-capability | active | M005/S02 | M005/S01 | unmapped |
| R037 | continuity | active | M005/S01 | M005/S02 | unmapped |
| R038 | quality-attribute | active | M005/S02 | M005/S01 | unmapped |
| R014 | core-capability | validated | M002/S01 | none | validated |
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
| R027 | core-capability | validated | M004/S01 | none | validated |
| R028 | core-capability | validated | M004/S02 | none | validated |
| R029 | core-capability | validated | M004/S02 | none | validated |
| R030 | quality-attribute | validated | M004/S02 | none | validated |
| R031 | quality-attribute | validated | M004/S03 | M004/S01, M004/S02 | validated |
| R032 | quality-attribute | validated | M004/S03 | M004/S01, M004/S02 | validated |
| R033 | constraint | out-of-scope | none | none | n/a |

## Coverage Summary

- Active requirements: 5
- Mapped to slices: 5
- Validated: 19
- Unmapped active requirements: 0
