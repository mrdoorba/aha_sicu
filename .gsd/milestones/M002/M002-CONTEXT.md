# M002: Evaluation Results i18n

**Gathered:** 2026-03-17
**Status:** Ready for planning

## Project Description

Make evaluation results fully translatable across the AHA SICU system. The EvaluationDetailPage (Riwayat/history view) currently renders all scoring output in hardcoded Indonesian regardless of the language toggle. Email send dialogs don't let users choose the email language independently of the UI language. This milestone makes the history page language-aware and adds email language selection.

## Why This Milestone

The system already has 3-language support (ID/EN/TH) for UI chrome, and the backend already generates i18n structured data alongside Indonesian strings. The presentation dashboard already renders evaluation results in the active language. But the history detail page — the most-visited page for reviewing and sharing evaluations — ignores all i18n data and shows raw Indonesian strings. Thai staff and English-speaking reviewers can't read evaluation results in their language.

## User-Visible Outcome

### When this milestone is complete, the user can:

- View any evaluation in the history detail page in their selected language (ID/EN/TH)
- Open any email send dialog and pick the email language independently of the UI language
- See the email body preview update in real-time when switching email language
- View old (pre-i18n) evaluations with graceful Indonesian fallback — no blank fields or errors

### Entry point / environment

- Entry point: Browser at evaluation detail page (`/history/:id`), email send dialogs
- Environment: local dev / browser
- Live dependencies involved: none (i18n is client-side rendering)

## Completion Class

- Contract complete means: all scoring text on EvaluationDetailPage renders through i18n; email dialogs have language selector; locale files have no hardcoded IDR
- Integration complete means: backend evaluation detail API returns marketplace; frontend uses stored i18n keys for rendering
- Operational complete means: none — no service lifecycle changes

## Final Integrated Acceptance

To call this milestone complete, we must prove:

- Switch UI to EN → open a history evaluation detail → all scoring messages, categories, conclusions display in English
- Switch UI to TH → same evaluation → all text displays in Thai
- Open email send dialog → change language to TH → email body preview renders in Thai while UI stays in current language
- View a pre-i18n evaluation → Indonesian text displays correctly, no errors or blank fields
- All existing tests pass with zero regressions

## Risks and Unknowns

- **Pre-i18n evaluation data** — Evaluations saved before the i18n system may lack `_i18n` fields in `score_breakdown`. Risk: graceful fallback must work correctly. Mitigation: `renderTranslatable()` pattern already handles null i18n gracefully.
- **History page email dialog uses mailto: links** — The `SendMailDialog` on the history page composes email body client-side and opens a mailto: link. Unlike the dashboard's SMTP-based `SendEmailDialog`, there's no backend rendering. The email body must be assembled from i18n keys entirely on the frontend. Risk: the frontend needs an email body assembly function that mirrors `_assemble_email_body` logic.

## Existing Codebase / Prior Art

- `frontend/src/utils/renderTranslatable.ts` — proven pattern for resolving i18n keys with fallback
- `frontend/src/lib/categoryMap.ts` — maps Indonesian backend category names to i18n label keys
- `frontend/src/components/dashboard/CategoryMetricCard.tsx` — already uses `renderTranslatable()` for scoring rows
- `frontend/src/components/dashboard/KesimpulanSection.tsx` — already renders conclusion/closing/marketing via i18n
- `frontend/src/components/dashboard/DetailedEvaluation.tsx` — already passes `_i18n` fields from stored score_breakdown
- `backend/app/modules/email/template.py` — HTML email renderer already supports `language` parameter with `STRINGS`, `CATEGORY_MAP`, and `_translate()` using frontend locale files
- `backend/app/calculators/scoring/models.py` — `TranslatableText` dataclass with key + vars
- `frontend/src/hooks/useScoring.ts` — `ScoringResult` type (missing `_i18n` fields on `RowScore`)
- `frontend/src/components/layout/LanguageToggle.tsx` — `LANGUAGES` array is source of available languages

> See `.gsd/DECISIONS.md` for all architectural and pattern decisions — it is an append-only register; read it during planning, append to it during execution.

## Relevant Requirements

- R014 — EvaluationDetailPage i18n rendering
- R015 — Email language selector on all send dialogs
- R016 — Email body rebuilt from i18n keys at render time
- R017 — Locale files use {{currency}} instead of hardcoded IDR
- R018 — Evaluation detail API returns marketplace
- R019 — Old evaluations fall back to Indonesian gracefully
- R020 — Adding a new language is locale-file-only
- R021 — Frontend types explicitly include i18n fields
- R022 — No database data loss

## Scope

### In Scope

- EvaluationDetailPage rendering scoring results through i18n
- Email language selector on SendMailDialog (history), SendEmailDialog (dashboard), EmailOutput (evaluation page)
- Frontend email body assembly from i18n keys for mailto-based dialog
- Backend evaluation detail API returning marketplace field
- TypeScript type fixes for i18n fields
- Locale file cleanup (hardcoded IDR → {{currency}})
- Verification that adding a new language is trivial

### Out of Scope / Non-Goals

- Backend scoring engine changes — i18n data generation is already complete
- New database migrations — marketplace column already exists on evaluations table
- New translation keys — all needed keys already exist in locale files
- Changing how the presentation dashboard works — it's already correct

## Technical Constraints

- `renderTranslatable()` is the established pattern — use it, don't invent alternatives
- Email send dialogs have two different architectures: mailto (history) vs SMTP (dashboard). Language selector must work for both.
- `i18n.getFixedT(lang)` can render in a specific language without changing global UI language — use this for email body rendering
- No schema migrations — only query changes to SELECT marketplace from existing column

## Integration Points

- Backend evaluation detail API — add marketplace to SELECT
- Backend EvaluationDetailResponse schema — add marketplace field
- Frontend locale JSON files — fix hardcoded IDR strings
- Frontend i18n.ts — no changes needed (already imports all 3 locales)

## Open Questions

- None — all decisions resolved during discussion
