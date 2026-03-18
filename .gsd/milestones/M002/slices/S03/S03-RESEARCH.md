# S03: Email language selector & i18n body rebuild — Research

**Date:** 2026-03-18
**Depth:** Targeted

## Summary

S03 adds a language selector to all three email dialogs and rebuilds the email body from i18n keys in the selected language. There are three distinct email dialog architectures to handle:

1. **SendMailDialog** (history detail page) — composes a plain-text email body client-side and opens a `mailto:` link. The body currently uses the pre-rendered `email_output` string stored in the DB (always Indonesian). This needs a complete frontend email body assembly function that mirrors `_assemble_email_body` from the backend but uses `i18n.getFixedT(selectedLang)` to render each row's `message_i18n` in the chosen language.

2. **SendEmailDialog** (dashboard) — sends via SMTP through the backend API (`POST /api/v1/email/send`). Already passes `language: i18n.language` in the mutation payload. The backend `render_email_html()` already accepts a `language` parameter. This only needs the UI language selector dropdown — the plumbing is done.

3. **EmailOutput** (evaluation scoring page) — a read-only copy-paste card showing `email_subject` and `email_body` from the live `ScoringResult`. These come from the backend scoring endpoint which generates them in Indonesian. This needs the language selector so the displayed text can be rebuilt from the `ScoringResult`'s i18n fields (`message_i18n`, `conclusion_i18n`, `marketing_budget_i18n`, `closing_message_i18n`, `email_subject_i18n`).

The primary recommendation is to build a shared `EmailLanguageSelector` component and a `buildI18nEmailBody()` utility function, then integrate them into all three dialogs. R017 (locale hardcode cleanup of `IDR` → `{{currency}}`) is also owned by this slice and is a prerequisite for correct currency display in rebuilt email bodies.

## Recommendation

1. **First**: Fix the 6 hardcoded `IDR` locale keys across all 3 locale files (R017). This is a prerequisite — without it, rebuilt email bodies will show "IDR" for THB marketplace evaluations.

2. **Second**: Create the `EmailLanguageSelector` component — a simple dropdown reusing the language list from `LanguageToggle.tsx` (currently unexported — extract the `LANGUAGES` constant to a shared location like `lib/languages.ts`).

3. **Third**: Create `buildI18nEmailBody()` utility that mirrors the backend's `_assemble_email_body` structure but uses `i18n.getFixedT(lang)` to render each `message_i18n` TranslatableText. This function consumes `score_breakdown` (with `_i18n` fields) plus `scoring_summary` and produces a plain-text email body.

4. **Fourth**: Integrate into all three dialogs, wiring the language selector to control the body rendering.

## Implementation Landscape

### Key Files

- `frontend/src/components/layout/LanguageToggle.tsx` — Contains the `LANGUAGES` array (unexported). Extract to shared location.
- `frontend/src/components/evaluations/SendMailDialog.tsx` — History page mailto dialog. Receives `emailOutput: string` (pre-rendered Indonesian). Needs language selector + dynamic body rebuild from `score_breakdown` and `scoring_summary`.
- `frontend/src/components/evaluations/sendMailUtils.ts` — `buildSubject()` and `buildBody()` functions. `buildSubject` needs to accept a `TFunction` for i18n. `buildBody` needs overhaul to accept i18n-rebuilt body text.
- `frontend/src/components/dashboard/SendEmailDialog.tsx` — Dashboard SMTP dialog. Already passes `language: i18n.language`. Needs only the UI language selector dropdown + wiring the selected language to the mutation payload and preview endpoint.
- `frontend/src/components/evaluation/scoring/EmailOutput.tsx` — Evaluation page copy-paste card. Receives `subject` and `body` strings. Needs language selector to rebuild both from `ScoringResult` i18n fields.
- `frontend/src/components/evaluation/scoring/ScoringSection.tsx` — Parent of `EmailOutput`, passes `scoringResult.email_subject` and `scoringResult.email_body`. Must pass full `scoringResult` (or extracted i18n data) down so `EmailOutput` can rebuild.
- `frontend/src/hooks/useScoring.ts` — `ScoringResult` type with `email_subject`, `email_body`, and i18n companion fields (`conclusion_i18n`, `marketing_budget_i18n`, `closing_message_i18n`, `email_subject_i18n`).
- `frontend/src/hooks/useEvaluationDetail.ts` — `EvaluationDetail` type. Provides `email_output`, `score_breakdown`, `calculator_results`.
- `frontend/src/pages/EvaluationDetailPage.tsx` — Renders `EmailOutputSection` and `SendMailDialog`. Must pass `score_breakdown` and `calculator_results` to `SendMailDialog` for i18n body assembly.
- `frontend/src/utils/renderTranslatable.ts` — `renderTranslatable()` function and `TranslatableText` type. Reusable for email body assembly.
- `frontend/src/i18n.ts` — i18next setup. `i18n.getFixedT(lang)` returns a `TFunction` bound to a specific language without changing the global UI language.
- `frontend/src/locales/id.json`, `en.json`, `th.json` — 6 keys with hardcoded "IDR" need `{{currency}}` (R017).
- `backend/app/calculators/scoring/computations.py` — `_assemble_email_body()` — the reference implementation for email body structure. The frontend `buildI18nEmailBody()` mirrors its section ordering (operational → business → visitors → promo → products → ads → campaign → competition → conclusion → marketing → budget → closing).
- `backend/app/calculators/scoring/models.py` — `ScoringResult` dataclass with `email_body`, i18n companions.
- `frontend/src/lib/categoryMap.ts` — `CATEGORY_MAP` array. Needed by `buildI18nEmailBody()` for section headers (translate Indonesian category names to email language).

### Build Order

1. **R017 locale fix** (6 keys × 3 files) — prerequisite, trivial, no dependencies. Unblocks correct currency display in all rebuilt email bodies.

2. **Extract `LANGUAGES` to `frontend/src/lib/languages.ts`** — Shared constant for both `LanguageToggle` and `EmailLanguageSelector`. Import from new location in `LanguageToggle.tsx`.

3. **Create `EmailLanguageSelector` component** (`frontend/src/components/shared/EmailLanguageSelector.tsx`) — Dropdown that accepts `value: string`, `onChange: (lang: string) => void`, defaults to `i18n.language`. Uses `LANGUAGES` from shared location.

4. **Create `buildI18nEmailBody()` utility** (`frontend/src/utils/buildI18nEmailBody.ts`) — Takes `score_breakdown` (with `_i18n` fields), `scoring_summary`, and a `TFunction` (from `i18n.getFixedT(lang)`). Produces plain-text email body mirroring `_assemble_email_body` structure. Also export `buildI18nEmailSubject()` for subject line.

5. **Wire `SendEmailDialog` (dashboard)** — Add `EmailLanguageSelector`, wire selected language to `mutate()` payload's `language` field and to the preview endpoint URL query param. Simplest integration — backend already handles language.

6. **Wire `EmailOutput` (evaluation page)** — Add `EmailLanguageSelector`, pass `scoringResult` (or its i18n fields), rebuild `subject`/`body` via `buildI18nEmailSubject`/`buildI18nEmailBody` with `i18n.getFixedT(selectedLang)`. Update `ScoringSection` to pass scoring data through.

7. **Wire `SendMailDialog` (history page)** — Add `EmailLanguageSelector`, accept `score_breakdown` and `calculator_results` as new props, use `buildI18nEmailBody()` to rebuild body in selected language. Update `sendMailUtils.ts` to accept a `TFunction` parameter. Update `EvaluationDetailPage` to pass `score_breakdown` and `calculator_results` to `SendMailDialog`.

### Verification Approach

**Unit tests:**
- `buildI18nEmailBody.test.ts` — Given mock `score_breakdown` with `_i18n` fields and `scoring_summary`, verify body contains translated messages when `t()` returns locale-specific strings. Verify fallback to raw messages when `_i18n` is missing.
- `EmailLanguageSelector.test.tsx` — Renders dropdown with 3 languages, calls `onChange` on selection.
- Updated `SendMailDialog.test.tsx` — Verify language selector renders, verify body updates when language changes.
- Updated `SendEmailDialog.test.tsx` — Verify language selector renders, verify mutation payload includes selected language.
- Updated `EmailOutput.test.tsx` — Verify language selector renders, verify displayed body changes with language.

**Regression:**
```bash
cd frontend && npx vitest run --reporter=verbose 2>&1 | tail -5
```
All 556+ existing tests must pass.

**Manual verification:**
- Open evaluation detail → email dialog → switch language → body preview changes language
- Open dashboard → send email dialog → switch language → preview updates via backend
- Open evaluation page → score → email output card → switch language → subject/body update

## Constraints

- `SendMailDialog` uses `mailto:` links — the body is plain text with URL encoding limits (~2000 chars in some mail clients). The rebuilt body must stay within this. The existing `_assemble_email_body` output is typically 1-2KB, well within limits.
- `i18n.getFixedT(lang)` creates a TFunction for a specific language without changing the global UI language. This is the prescribed approach (D020).
- `EmailOutput` component currently receives only `subject: string` and `body: string`. Changing its interface to accept scoring data is a breaking API change requiring `ScoringSection` updates.
- `LANGUAGES` array is not exported from `LanguageToggle.tsx` — must be extracted to a shared module.

## Common Pitfalls

- **`buildI18nEmailBody` section ordering must match backend** — The backend `_assemble_email_body` has a specific section order with specific row filters (e.g., business rows 13 & 20 only, visitor rows 28 & 29 only). The frontend function must replicate this ordering exactly or emails will look different. Reference `backend/app/calculators/scoring/computations.py:328-440`.
- **Pre-i18n evaluations in `SendMailDialog`** — Old evaluations have `score_breakdown` without `_i18n` fields. The `buildI18nEmailBody()` function must fall back to raw `message` strings, which are always Indonesian. When `_i18n` is absent, the email language selector effectively does nothing (the body will be Indonesian regardless). This is correct behavior — it matches the `renderTranslatable()` fallback pattern.
- **`EmailOutput` on evaluation page uses live `ScoringResult`** — The data shape is slightly different from stored evaluations. `ScoringResult` has top-level `conclusion_i18n`, `marketing_budget_i18n`, `closing_message_i18n`, while stored evaluations have these nested in `calculator_results.scoring_summary`. The `buildI18nEmailBody` function needs to accept both shapes, or callers normalize the data before passing it.
- **Preview endpoint in `SendEmailDialog` doesn't accept language parameter** — The `GET /api/v1/email/preview/{evaluation_id}` uses `current_user.get("language", "id")` from the auth token, not a query param. To preview in a different language, need to add a `language` query param to the preview endpoint.

## Open Risks

- **Backend preview endpoint language param** — The dashboard's `SendEmailDialog` fetches HTML preview from `GET /api/v1/email/preview/{evaluation_id}`. Currently uses user's stored language from auth token. If the email language selector picks a different language than the UI, the preview won't match. Fix: add optional `language` query param to the preview endpoint. This is a small backend change not originally scoped to S03 — but without it, the preview feature in `SendEmailDialog` will show the wrong language.
- **`sendMailUtils.buildBody` hardcodes Indonesian structure** — The `buildBody` function constructs `Kepada Pimpinan {{brandName}} (Bapak/Ibu {{picName}})` from locale keys `sendMailUtils.salutation` and `sendMailUtils.intro`. These already exist in all 3 locales, so `buildBody` just needs to use `i18n.getFixedT(lang)` instead of the global `i18n.t()`. This is straightforward but easy to miss.
