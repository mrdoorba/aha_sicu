# M005: Evaluation Detail Page Content i18n

**Gathered:** 2026-03-18
**Status:** Ready for planning

## Project Description

The evaluation history detail page displays scoring output as raw Indonesian text in three areas: calculator output sections (ads keyword, discount), the email output section (full scoring report with section headers and per-row messages), and top SKU labels. The backend already generates `message_i18n` TranslatableText for all scoring rows, and the frontend has 106 `scoring.*` keys + 31 `ads.*` keys + `emailBody.section.*` headers in all 3 locale files. The dashboard components already implement i18n rendering for the same data. This milestone brings the evaluation detail page to parity.

## Why This Milestone

The evaluation history detail page is the primary page staff use to review past evaluations. After M002-M004 completed i18n for UI chrome, form labels, and section headings, the actual scoring content inside those sections still renders in Indonesian. Thai and English users see translated headings wrapping untranslated Indonesian content — a broken experience.

## User-Visible Outcome

### When this milestone is complete, the user can:

- View any evaluation in the history detail page with all scoring content rendered in their selected language (ID/EN/TH)
- See the email output section with translated section headers, per-row scoring messages, conclusion, marketing budget, and closing message
- View pre-i18n evaluations (saved before M002) with graceful fallback to raw Indonesian text

### Entry point / environment

- Entry point: `/history/:id` route in the frontend SPA
- Environment: browser (local dev / production)
- Live dependencies involved: none (all data is already stored in evaluation records)

## Completion Class

- Contract complete means: frontend renders i18n content through `renderTranslatable` / `buildI18nEmailBody` instead of raw text; tests pass
- Integration complete means: detail page displays translated content for real evaluations with i18n data in the DB
- Operational complete means: none

## Final Integrated Acceptance

To call this milestone complete, we must prove:

- An evaluation with i18n data displays all calculator sections and email output in English when the UI language is set to English
- An evaluation without i18n data (pre-M002) still displays readable Indonesian text without errors
- All frontend tests pass (612+ tests)

## Risks and Unknowns

- Pre-i18n evaluations may have unexpected data shapes in calculator_results — fallback rendering must be robust
- The discount section's i18n data path differs from ads keyword (value_i18n on row 73 vs structured details) — need to handle both patterns

## Existing Codebase / Prior Art

- `frontend/src/components/dashboard/DataIntelligence.tsx` — already renders ads keyword from i18n structured data using `renderTranslatable`, `renderAdList`, `renderFlagList`
- `frontend/src/utils/buildI18nEmailBody.ts` — already reconstructs full email body from `score_breakdown` i18n data, used by `SendMailDialog`
- `frontend/src/utils/renderTranslatable.ts` — core utility for resolving TranslatableText with raw fallback
- `frontend/src/pages/EvaluationDetailPage.tsx` — the target page; currently dumps `output_text` and `email_output` as raw strings
- `frontend/src/components/evaluations/SendMailDialog.tsx` — already uses `buildI18nEmailBody` with `hasI18nData` guard for backward compat
- `frontend/src/lib/calculatorGuards.ts` — `isAdsKeywordDetails` type guard used by DataIntelligence
- `backend/app/calculators/scoring/categories.py` — generates `value_i18n` on discount row 73 with `scoring.discountCheckup.pass/fail` keys
- `backend/app/calculators/scoring/messages.py` — generates `message_i18n` TranslatableText for all scoring category rows

> See `.gsd/DECISIONS.md` for all architectural and pattern decisions — it is an append-only register; read it during planning, append to it during execution.

## Relevant Requirements

- R034 — Ads keyword section renders translated from i18n structured data
- R035 — Discount section renders translated from i18n structured data
- R036 — Email output section renders scoring messages in selected language
- R037 — Pre-i18n evaluations fall back to raw Indonesian text without errors
- R038 — All existing frontend tests pass

## Scope

### In Scope

- Updating AdsKeywordSection in EvaluationDetailPage to render from structured i18n details (mirroring DataIntelligence.tsx pattern)
- Updating DiscountSection in EvaluationDetailPage to render from i18n data (scoring.discountCheckup.pass/fail via score_breakdown)
- Updating EmailOutputSection in EvaluationDetailPage to use buildI18nEmailBody instead of raw email_output
- Backward compatibility for pre-i18n evaluations
- Updating affected tests

### Out of Scope / Non-Goals

- Adding new locale keys (all needed keys already exist)
- Backend changes (all i18n structured data is already generated and stored)
- Adding a separate language selector to the detail page (uses active UI language)
- Changing the SendMailDialog (already works with i18n)

## Technical Constraints

- Must reuse existing patterns from DataIntelligence.tsx and buildI18nEmailBody.ts — no new i18n infrastructure
- Must preserve backward compat for evaluations without _i18n fields
- No backend changes required — all structured data already exists in DB

## Integration Points

- `score_breakdown` JSONB in evaluations table — contains per-row `message_i18n` TranslatableText objects
- `calculator_results` JSONB — contains ads keyword `details` with `ak2_i18n`, `al2_i18n`, etc.
- `calculator_results.scoring_summary` — contains `conclusion_i18n`, `marketing_budget_i18n`, `closing_message_i18n`

## Open Questions

- None — all building blocks exist and are proven in other components
