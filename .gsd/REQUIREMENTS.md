# Requirements

This file is the explicit capability and coverage contract for the project.

## Active

### R014 — EvaluationDetailPage renders scoring results in active UI language
- Class: core-capability
- Status: active
- Description: When a user views an evaluation in the history detail page, all scoring messages, category names, conclusions, closing messages, and marketing budget text render in the currently selected UI language (ID/EN/TH).
- Why it matters: This is the primary page staff use to review and share evaluation results. Indonesian-only output makes the system unusable for Thai staff and limits English-speaking reviewers.
- Source: user
- Primary owning slice: M002/S01
- Supporting slices: none
- Validation: unmapped
- Notes: Must use stored i18n keys when present; fall back to raw text for pre-i18n evaluations.

### R015 — Email language selector on all send dialogs
- Class: core-capability
- Status: active
- Description: All email send dialogs (history detail SendMailDialog, dashboard SendEmailDialog, evaluation page EmailOutput) include a language dropdown that lets the user choose the email language independently of the UI language, defaulting to the current UI language.
- Why it matters: Emails cross language boundaries — Thai staff may send to Indonesian brand owners. The email language must be decoupled from the UI language.
- Source: user
- Primary owning slice: M002/S02
- Supporting slices: none
- Validation: unmapped
- Notes: Dashboard SendEmailDialog already sends language to backend; needs UI selector. History SendMailDialog uses mailto — needs frontend-side i18n rendering.

### R016 — Email body rebuilt from i18n keys at render time
- Class: core-capability
- Status: active
- Description: Email body content is reconstructed from stored i18n structured data at render time in the chosen language, rather than displaying the pre-rendered Indonesian email_output string.
- Why it matters: Pre-rendered email_output is always Indonesian. To support language switching, the email body must be assembled dynamically from i18n keys.
- Source: user
- Primary owning slice: M002/S02
- Supporting slices: M002/S01
- Validation: unmapped
- Notes: The pre-rendered email_output in DB becomes a fallback for old evaluations without i18n data.

### R017 — Locale files use {{currency}} variable instead of hardcoded IDR
- Class: quality-attribute
- Status: active
- Description: All locale translation strings that reference currency use the {{currency}} interpolation variable (already provided by the backend) instead of hardcoded "IDR".
- Why it matters: Hardcoded IDR in locale strings produces incorrect output for THB marketplace evaluations when viewed in EN or TH.
- Source: inferred
- Primary owning slice: M002/S03
- Supporting slices: none
- Validation: unmapped
- Notes: 6 keys across all 3 locale files affected: scoring.monthlySales.pass/fail, scoring.competitionProduct.pass/fail, forms.competition.competitive/notCompetitive.

### R018 — Evaluation detail API returns marketplace field
- Class: integration
- Status: active
- Description: The GET evaluation detail API response includes the marketplace field from the evaluations table.
- Why it matters: Frontend needs marketplace to determine currency code for formatting and to pass to i18n variable resolution.
- Source: inferred
- Primary owning slice: M002/S01
- Supporting slices: none
- Validation: unmapped
- Notes: Requires adding e.marketplace to the SQL query and EvaluationDetailResponse schema.

### R019 — Old evaluations gracefully fall back to raw Indonesian text
- Class: continuity
- Status: active
- Description: Evaluations saved before the i18n system was added (which lack _i18n fields in score_breakdown) display their original Indonesian text. Evaluations with i18n keys translate. No evaluation becomes unreadable.
- Why it matters: Data continuity — staff must be able to view all historical evaluations without errors or blank fields.
- Source: user
- Primary owning slice: M002/S01
- Supporting slices: none
- Validation: unmapped
- Notes: renderTranslatable() pattern already handles this — falls back to raw text when i18n is null/undefined.

### R020 — Adding a new language requires only locale JSON + i18n.ts import
- Class: quality-attribute
- Status: active
- Description: After M002 is complete, adding a 4th language to the system requires only: (a) creating a new locale JSON file, (b) adding its import to i18n.ts, (c) adding it to the LanguageToggle LANGUAGES array and backend STRINGS/CATEGORY_MAP. No schema changes, no migrations, no new components.
- Why it matters: The user explicitly wants future language additions to be trivial.
- Source: user
- Primary owning slice: M002/S03
- Supporting slices: M002/S01, M002/S02
- Validation: unmapped
- Notes: Verification: document the exact steps and confirm no other changes are needed.

### R021 — Frontend types explicitly include i18n fields
- Class: quality-attribute
- Status: active
- Description: TypeScript interfaces for RowScore, CategoryScore, and ScoringResult in useScoring.ts and useEvaluationDetail.ts explicitly declare _i18n fields (metric_i18n, message_i18n, benchmark_i18n, value_i18n, category_i18n, conclusion_i18n, etc.).
- Why it matters: Currently i18n fields survive at runtime through untyped JSON passthrough but aren't declared in TypeScript types. Explicit types prevent accidental stripping and enable IDE support.
- Source: inferred
- Primary owning slice: M002/S01
- Supporting slices: none
- Validation: unmapped
- Notes: Low risk — additive type changes only.

### R022 — No database data loss from schema changes
- Class: constraint
- Status: active
- Description: All database schema changes in M002 are additive only (new columns, new fields in JSONB). No existing data is modified, deleted, or migrated destructively. Re-evaluation is acceptable.
- Why it matters: User explicitly requires zero data loss.
- Source: user
- Primary owning slice: M002
- Supporting slices: none
- Validation: unmapped
- Notes: The only DB change expected is adding marketplace to the evaluation detail query SELECT list — no schema migration needed.

## Validated

### SCORE-01 — `generate_score()` selects rules based on evaluation's marketplace
- Status: validated
- Class: core-capability
- Source: inferred
- Primary owning slice: M001/S02
- Validation: generate_score reads marketplace from eval_inputs, passes to calculate_score as keyword arg.

### SCORE-02 — Scoring message templates display correct currency (THB/IDR) based on marketplace
- Status: validated
- Class: core-capability
- Source: inferred
- Primary owning slice: M001/S02
- Validation: 24 unit tests prove THB messages show "THB" not "IDR".

### DATA-02 — Scoring rules table supports marketplace dimension
- Status: validated
- Class: core-capability
- Source: inferred
- Primary owning slice: M001/S01
- Validation: Migration 026 adds marketplace column with CHECK constraint.

### DATA-03 — THB scoring rule thresholds seeded from IDR conversion
- Status: validated
- Class: core-capability
- Source: inferred
- Primary owning slice: M001/S01
- Validation: Migration 026 seeds TH row with converted values.

### CSV-01 — Price parsing handles THB number format
- Status: validated
- Class: core-capability
- Source: inferred
- Primary owning slice: M001/S03
- Validation: 21 unit tests in test_price_parser.py.

### CSV-02 — Existing IDR parsing continues to work unchanged
- Status: validated
- Class: core-capability
- Source: inferred
- Primary owning slice: M001/S03
- Validation: 457 calculator tests passing.

### DATA-01 — Evaluation stores marketplace selection
- Status: validated
- Class: core-capability
- Source: inferred
- Primary owning slice: M001/S01
- Validation: Backend schema ready, frontend orchestrator manages marketplace state.

### RULES-01 — Rules page has marketplace tabs
- Status: validated
- Class: core-capability
- Source: inferred
- Primary owning slice: M001/S04
- Validation: 38/38 rules tests pass.

### RULES-02 — Admin can edit THB thresholds independently
- Status: validated
- Class: core-capability
- Source: inferred
- Primary owning slice: M001/S04
- Validation: PUT endpoint and UI tested.

### EVAL-01 — User can select marketplace on evaluation page
- Status: validated
- Class: core-capability
- Source: inferred
- Primary owning slice: M001/S04
- Validation: 536 frontend tests pass.

### EVAL-02 — Currency formatting shows code prefix based on marketplace
- Status: validated
- Class: core-capability
- Source: inferred
- Primary owning slice: M001/S04
- Validation: 9 CurrencyField tests pass.

### EVAL-03 — Evaluation results display currency values in correct format
- Status: validated
- Class: core-capability
- Source: inferred
- Primary owning slice: M001/S04
- Validation: 19 formUtils tests verify both marketplace formats.

## Deferred

(none)

## Out of Scope

### R030 — Live exchange rate integration
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
| R014 | core-capability | active | M002/S01 | none | unmapped |
| R015 | core-capability | active | M002/S02 | none | unmapped |
| R016 | core-capability | active | M002/S02 | M002/S01 | unmapped |
| R017 | quality-attribute | active | M002/S03 | none | unmapped |
| R018 | integration | active | M002/S01 | none | unmapped |
| R019 | continuity | active | M002/S01 | none | unmapped |
| R020 | quality-attribute | active | M002/S03 | M002/S01, M002/S02 | unmapped |
| R021 | quality-attribute | active | M002/S01 | none | unmapped |
| R022 | constraint | active | M002 | none | unmapped |
| SCORE-01 | core-capability | validated | M001/S02 | none | validated |
| SCORE-02 | core-capability | validated | M001/S02 | none | validated |
| DATA-02 | core-capability | validated | M001/S01 | none | validated |
| DATA-03 | core-capability | validated | M001/S01 | none | validated |
| CSV-01 | core-capability | validated | M001/S03 | none | validated |
| CSV-02 | core-capability | validated | M001/S03 | none | validated |
| DATA-01 | core-capability | validated | M001/S01 | none | validated |
| RULES-01 | core-capability | validated | M001/S04 | none | validated |
| RULES-02 | core-capability | validated | M001/S04 | none | validated |
| EVAL-01 | core-capability | validated | M001/S04 | none | validated |
| EVAL-02 | core-capability | validated | M001/S04 | none | validated |
| EVAL-03 | core-capability | validated | M001/S04 | none | validated |
| R030 | constraint | out-of-scope | none | none | n/a |

## Coverage Summary

- Active requirements: 9
- Mapped to slices: 9
- Validated: 12
- Unmapped active requirements: 0
