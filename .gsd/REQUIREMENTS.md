# Requirements

This file is the explicit capability and coverage contract for the project.

## Active

### R023 — Follower count threshold in scoring messages uses international comma separator (>50,000 not >50.000)
- Class: quality-attribute
- Status: active
- Description: The follower count threshold display in scoring messages uses international comma convention (>50,000) instead of Indonesian dot convention (>50.000). Applies to DEFAULT_RULES fallback, inline message fallbacks, and DB-stored message templates.
- Why it matters: Dot-as-thousands-separator is Indonesian locale-specific. International convention (comma) is consistent with how all other numbers are formatted in the system.
- Source: user
- Primary owning slice: M003/S01
- Supporting slices: none
- Validation: unmapped
- Notes: Affects rules.py, messages.py inline fallback, and requires a DB migration for stored templates.

### R024 — Follower val_str formatted with comma thousands separator, not dot
- Class: quality-attribute
- Status: active
- Description: The follower count value displayed in scoring messages (val_str) uses comma as thousands separator instead of being converted from comma to dot via .replace(",", ".").
- Why it matters: The .replace(",", ".") on messages.py:164 forces Indonesian number formatting on all marketplaces. International comma convention should be used.
- Source: user
- Primary owning slice: M003/S01
- Supporting slices: none
- Validation: unmapped
- Notes: Single line change in messages.py:164.

### R025 — Ads calculator BOTTOM ads min_cost threshold is marketplace-aware
- Class: core-capability
- Status: active
- Description: The BOTTOM ads cost floor in ads_keyword.py uses marketplace-appropriate values: 100,000 for IDR, 190 for THB (converted via IDR_TO_THB_RATE 0.0019).
- Why it matters: 100,000 THB ≈ $2,800 USD — far too high to be a meaningful cost floor for Thai marketplace ads. The threshold must match currency scale.
- Source: user
- Primary owning slice: M003/S01
- Supporting slices: none
- Validation: unmapped
- Notes: Use existing IDR_TO_THB_RATE from marketplace.py for conversion.

### R026 — Juta display convention preserved for Indonesian marketplace
- Class: constraint
- Status: active
- Description: The sales range conclusion (G66) continues to divide by 1,000,000 and append "juta" for the Indonesian (ID) marketplace. THB marketplace continues to use raw comma-formatted numbers.
- Why it matters: "Juta" is the correct Indonesian-language convention for displaying large IDR amounts. This is intentional, not a bug.
- Source: user
- Primary owning slice: M003/S01
- Supporting slices: none
- Validation: unmapped
- Notes: No code change needed — existing marketplace branching in _compute_g66 is correct. Verify it stays correct.

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
- Validation: All 3 dialogs have EmailLanguageSelector: SendEmailDialog (22 tests, including 4 language-selector-specific), SendMailDialog (21 tests, including 5 language-selector-specific), EmailOutput (11 tests, including 7 language-selector-specific). Selector defaults to i18n.language, onChange updates email body preview without changing global UI language.
- Notes: Dashboard SendEmailDialog already sends language to backend; needs UI selector. History SendMailDialog uses mailto — needs frontend-side i18n rendering.

### R016 — Email body content is reconstructed from stored i18n structured data at render time in the chosen language, rather than displaying the pre-rendered Indonesian email_output string.
- Class: core-capability
- Status: validated
- Description: Email body content is reconstructed from stored i18n structured data at render time in the chosen language, rather than displaying the pre-rendered Indonesian email_output string.
- Why it matters: Pre-rendered email_output is always Indonesian. To support language switching, the email body must be assembled dynamically from i18n keys.
- Source: user
- Primary owning slice: M002/S03
- Supporting slices: M002/S01
- Validation: buildI18nEmailBody utility (20 unit tests) assembles email body from stored i18n structured data matching backend _assemble_email_body section ordering. buildI18nEmailSubject constructs translated subject. Both use i18n.getFixedT(selectedLang) for language-specific rendering. Pre-i18n evaluations fall back to raw email_output string. Wired into all 3 dialogs with verified body updates on language change.
- Notes: The pre-rendered email_output in DB becomes a fallback for old evaluations without i18n data.

### R017 — All locale translation strings that reference currency use the {{currency}} interpolation variable (already provided by the backend) instead of hardcoded "IDR".
- Class: quality-attribute
- Status: validated
- Description: All locale translation strings that reference currency use the {{currency}} interpolation variable (already provided by the backend) instead of hardcoded "IDR".
- Why it matters: Hardcoded IDR in locale strings produces incorrect output for THB marketplace evaluations when viewed in EN or TH.
- Source: inferred
- Primary owning slice: M002/S03
- Supporting slices: none
- Validation: All 6 keys across 3 locale files replaced with {{currency}} interpolation. grep -c "IDR" on all locale files returns 0. grep -c "{{currency}}" returns 6 per file. Full regression: 602 tests pass.
- Notes: 6 keys across all 3 locale files affected: scoring.monthlySales.pass/fail, scoring.competitionProduct.pass/fail, forms.competition.competitive/notCompetitive.

### R018 — The GET evaluation detail API response includes the marketplace field from the evaluations table.
- Class: integration
- Status: validated
- Description: The GET evaluation detail API response includes the marketplace field from the evaluations table.
- Why it matters: Frontend needs marketplace to determine currency code for formatting and to pass to i18n variable resolution.
- Source: inferred
- Primary owning slice: M002/S01
- Supporting slices: none
- Validation: Backend test test_get_evaluation_detail_has_marketplace proves API returns marketplace field. Triple-layer fallback (SQL COALESCE → service row.get → Pydantic default) ensures non-null.
- Notes: Requires adding e.marketplace to the SQL query and EvaluationDetailResponse schema.

### R019 — Evaluations saved before the i18n system was added (which lack _i18n fields in score_breakdown) display their original Indonesian text. Evaluations with i18n keys translate. No evaluation becomes unreadable.
- Class: continuity
- Status: validated
- Description: Evaluations saved before the i18n system was added (which lack _i18n fields in score_breakdown) display their original Indonesian text. Evaluations with i18n keys translate. No evaluation becomes unreadable.
- Why it matters: Data continuity — staff must be able to view all historical evaluations without errors or blank fields.
- Source: user
- Primary owning slice: M002/S01
- Supporting slices: none
- Validation: 602 frontend tests pass with mocks lacking _i18n fields and scoring_summary — no errors or blank fields. ScoringConclusionSection returns null when scoring_summary absent. ScoreBreakdownTable falls back to raw category string for unmapped names. hasI18nData guard in SendMailDialog falls back to original Indonesian body for pre-i18n evaluations.
- Notes: renderTranslatable() pattern already handles this — falls back to raw text when i18n is null/undefined.

### R020 — After M002 is complete, adding a 4th language to the system requires only: (a) creating a new locale JSON file, (b) adding its import to i18n.ts, (c) adding it to the LanguageToggle LANGUAGES array and backend STRINGS/CATEGORY_MAP. No schema changes, no migrations, no new components.
- Class: quality-attribute
- Status: validated
- Description: After M002 is complete, adding a 4th language to the system requires only: (a) creating a new locale JSON file, (b) adding its import to i18n.ts, (c) adding it to the LanguageToggle LANGUAGES array and backend STRINGS/CATEGORY_MAP. No schema changes, no migrations, no new components.
- Why it matters: The user explicitly wants future language additions to be trivial.
- Source: user
- Primary owning slice: M002/S03
- Supporting slices: M002/S01, M002/S02
- Validation: docs/adding-a-language.md (267 lines) covers all 7 touch points with file paths, locations, and code snippets. LanguageCode type derives from LANGUAGES array (single source of truth) — zero inline 'id' | 'en' | 'th' unions in non-test source. Process requires: (1) new locale JSON, (2) i18n.ts import, (3) LANGUAGES array entry, (4) backend auth Literal, (5) backend email regex, (6) backend STRINGS/CATEGORY_MAP. No schema changes, migrations, or new components. 602 tests pass.
- Notes: Validated in S04. Documentation checklist + LanguageCode type centralization together prove that adding a 4th language is locale-file-only + config additions.

### R021 — TypeScript interfaces for RowScore, CategoryScore, and ScoringResult in useScoring.ts and useEvaluationDetail.ts explicitly declare _i18n fields (metric_i18n, message_i18n, benchmark_i18n, value_i18n, category_i18n, conclusion_i18n, etc.).
- Class: quality-attribute
- Status: validated
- Description: TypeScript interfaces for RowScore, CategoryScore, and ScoringResult in useScoring.ts and useEvaluationDetail.ts explicitly declare _i18n fields (metric_i18n, message_i18n, benchmark_i18n, value_i18n, category_i18n, conclusion_i18n, etc.).
- Why it matters: Currently i18n fields survive at runtime through untyped JSON passthrough but aren't declared in TypeScript types. Explicit types prevent accidental stripping and enable IDE support.
- Source: inferred
- Primary owning slice: M002/S01
- Supporting slices: none
- Validation: useScoring.ts declares 8 optional _i18n fields on RowScore and CategoryScore (metric_i18n, value_i18n, message_i18n, benchmark_i18n, category_i18n, conclusion_i18n, marketing_budget_i18n, closing_message_i18n). TypeScript compilation succeeds. 602 frontend tests pass.
- Notes: Low risk — additive type changes only.

### R022 — All database schema changes in M002 are additive only (new columns, new fields in JSONB). No existing data is modified, deleted, or migrated destructively. Re-evaluation is acceptable.
- Class: constraint
- Status: validated
- Description: All database schema changes in M002 are additive only (new columns, new fields in JSONB). No existing data is modified, deleted, or migrated destructively. Re-evaluation is acceptable.
- Why it matters: User explicitly requires zero data loss.
- Source: user
- Primary owning slice: M002
- Supporting slices: none
- Validation: M002 made zero database schema changes. Only change was adding COALESCE(e.marketplace, 'ID') to the evaluation detail SELECT query — reads an existing column. No migrations, no data modifications, no destructive changes.
- Notes: The only DB change expected is adding marketplace to the evaluation detail query SELECT list — no schema migration needed.

## Out of Scope

### R030 — No automatic currency conversion. Thresholds are set manually.
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
| R023 | quality-attribute | active | M003/S01 | none | unmapped |
| R024 | quality-attribute | active | M003/S01 | none | unmapped |
| R025 | core-capability | active | M003/S01 | none | unmapped |
| R026 | constraint | active | M003/S01 | none | unmapped |
| R014 | core-capability | validated | M002/S01 | none | EvaluationDetailPage renders category names via CATEGORY_MAP + t(), conclusion/marketing_budget/closing_message via renderTranslatable() + ScoringConclusionSection. 25 EvaluationDetailPage tests pass including 5 i18n-specific. ScoreBreakdownTable translates categories with raw-string fallback. Pre-i18n evaluations fall back to raw Indonesian text. |
| R015 | core-capability | validated | M002/S03 | none | All 3 dialogs have EmailLanguageSelector: SendEmailDialog (22 tests, including 4 language-selector-specific), SendMailDialog (21 tests, including 5 language-selector-specific), EmailOutput (11 tests, including 7 language-selector-specific). Selector defaults to i18n.language, onChange updates email body preview without changing global UI language. |
| R016 | core-capability | validated | M002/S03 | M002/S01 | buildI18nEmailBody utility (20 unit tests) assembles email body from stored i18n structured data matching backend _assemble_email_body section ordering. buildI18nEmailSubject constructs translated subject. Both use i18n.getFixedT(selectedLang) for language-specific rendering. Pre-i18n evaluations fall back to raw email_output string. Wired into all 3 dialogs with verified body updates on language change. |
| R017 | quality-attribute | validated | M002/S03 | none | All 6 keys across 3 locale files replaced with {{currency}} interpolation. grep -c "IDR" on all locale files returns 0. grep -c "{{currency}}" returns 6 per file. Full regression: 602 tests pass. |
| R018 | integration | validated | M002/S01 | none | Backend test test_get_evaluation_detail_has_marketplace proves API returns marketplace field. Triple-layer fallback (SQL COALESCE → service row.get → Pydantic default) ensures non-null. |
| R019 | continuity | validated | M002/S01 | none | 602 frontend tests pass with mocks lacking _i18n fields and scoring_summary — no errors or blank fields. ScoringConclusionSection returns null when scoring_summary absent. ScoreBreakdownTable falls back to raw category string for unmapped names. hasI18nData guard in SendMailDialog falls back to original Indonesian body for pre-i18n evaluations. |
| R020 | quality-attribute | validated | M002/S03 | M002/S01, M002/S02 | docs/adding-a-language.md (267 lines) covers all 7 touch points with file paths, locations, and code snippets. LanguageCode type derives from LANGUAGES array (single source of truth) — zero inline 'id' | 'en' | 'th' unions in non-test source. Process requires: (1) new locale JSON, (2) i18n.ts import, (3) LANGUAGES array entry, (4) backend auth Literal, (5) backend email regex, (6) backend STRINGS/CATEGORY_MAP. No schema changes, migrations, or new components. 602 tests pass. |
| R021 | quality-attribute | validated | M002/S01 | none | useScoring.ts declares 8 optional _i18n fields on RowScore and CategoryScore (metric_i18n, value_i18n, message_i18n, benchmark_i18n, category_i18n, conclusion_i18n, marketing_budget_i18n, closing_message_i18n). TypeScript compilation succeeds. 602 frontend tests pass. |
| R022 | constraint | validated | M002 | none | M002 made zero database schema changes. Only change was adding COALESCE(e.marketplace, 'ID') to the evaluation detail SELECT query — reads an existing column. No migrations, no data modifications, no destructive changes. |
| R030 | constraint | out-of-scope | none | none | n/a |

## Coverage Summary

- Active requirements: 4
- Mapped to slices: 4
- Validated: 9 (R014-R022)
- Unmapped active requirements: 0
