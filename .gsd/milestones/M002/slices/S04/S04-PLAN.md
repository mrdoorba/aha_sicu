# S04: Locale hardcode cleanup & future-proofing

**Goal:** All locale files use `{{currency}}` variable (already done in S03 — verify it holds); a documented checklist confirms adding a 4th language requires only locale JSON + config changes; no hardcoded language type literals remain in frontend code.
**Demo:** `docs/adding-a-language.md` exists with a complete step-by-step checklist covering all 7+ touch points. Frontend inline `'id' | 'en' | 'th'` type unions are replaced with `LanguageCode` from `lib/languages.ts`. Full test suite passes with zero regressions.

## Must-Haves

- `docs/adding-a-language.md` with step-by-step checklist for adding a new language, covering all frontend and backend touch points (R020)
- Frontend inline `'id' | 'en' | 'th'` type literals in `LanguageToggle.tsx` and `apiClient.ts` replaced with `LanguageCode` import (R020 cleanup)
- R017 still holds: `grep -c "IDR" frontend/src/locales/*.json` returns 0 for all files
- Full frontend test suite passes with zero regressions

## Verification

- `test -f docs/adding-a-language.md` — documentation file exists
- `grep -c "IDR" frontend/src/locales/*.json` → all return 0 (R017 still valid)
- `grep -c "{{currency}}" frontend/src/locales/*.json` → all return 6 (R017 still valid)
- `grep -rn "'id' | 'en' | 'th'" frontend/src/components/layout/LanguageToggle.tsx frontend/src/services/apiClient.ts` → no matches (type cleanup done)
- `cd frontend && npx vitest run` → all tests pass, zero failures

## Tasks

- [x] **T01: Write "adding a language" documentation checklist** `est:25m`
  - Why: Primary R020 deliverable — documents every file that needs modification when adding a 4th language. Without this, future developers must grep the codebase to find touch points.
  - Files: `docs/adding-a-language.md` (new)
  - Do: Create `docs/adding-a-language.md` with a structured checklist covering all touch points grouped by frontend vs backend. Each entry specifies the file path, the specific section/line to edit, and what to add. Include: (1) `frontend/src/locales/<code>.json` — new file, (2) `frontend/src/i18n.ts` — import + resources entry, (3) `frontend/src/lib/languages.ts` — LANGUAGES array entry (this auto-updates `LanguageCode` type), (4) `backend/app/modules/auth/schemas.py` — add code to `Literal` union, (5) `backend/app/modules/email/schemas.py` — add code to regex pattern, (6) `backend/app/modules/email/template.py` — add entries to STRINGS and CATEGORY_MAP dicts. Emphasize that no schema migrations, no new components, and no structural changes are needed.
  - Verify: `test -f docs/adding-a-language.md` and manual review of completeness
  - Done when: `docs/adding-a-language.md` exists with all 7+ touch points documented, each with file path, location within file, and what to add

- [x] **T02: Replace inline language type literals with LanguageCode & run verification sweep** `est:20m`
  - Why: Eliminates hardcoded `'id' | 'en' | 'th'` unions in frontend code so adding a new language only requires updating the `LANGUAGES` array in `lib/languages.ts` (the single source of truth). Also runs the final R017 verification sweep.
  - Files: `frontend/src/components/layout/LanguageToggle.tsx`, `frontend/src/services/apiClient.ts`
  - Do: (1) In `LanguageToggle.tsx` line 32, replace `'id' | 'en' | 'th'` with `LanguageCode` and add import from `../../lib/languages`. (2) In `apiClient.ts` line 34, replace the inline `'id' | 'en' | 'th'` in the `paths` type with `LanguageCode` and add import from `../lib/languages`. (3) In `apiClient.ts` line 963, replace `'id' | 'en' | 'th'` parameter type with `LanguageCode` and ensure the import is present. (4) Run `grep -rn "'id' | 'en' | 'th'" frontend/src/ --include='*.ts' --include='*.tsx'` to confirm no remaining inline unions (test files excluded). (5) Run R017 verification: `grep -c "IDR" frontend/src/locales/*.json` returns 0 for all. (6) Run full test suite: `cd frontend && npx vitest run`.
  - Verify: `grep -rn "'id' | 'en' | 'th'" frontend/src/components/layout/LanguageToggle.tsx frontend/src/services/apiClient.ts` → no matches; `cd frontend && npx vitest run` → all pass
  - Done when: Zero inline `'id' | 'en' | 'th'` unions in `LanguageToggle.tsx` and `apiClient.ts`; full test suite green; R017 grep checks pass

## Observability / Diagnostics

- **Runtime signals:** No new runtime signals — this slice is documentation + type-level refactoring. Changes are verified at build/test time, not runtime.
- **Inspection surfaces:** `test -f docs/adding-a-language.md` confirms the doc exists. `grep -rn "'id' | 'en' | 'th'" frontend/src/` confirms no stale inline type literals remain.
- **Failure visibility:** If a new language is added without following the checklist, the system will fail at: (a) frontend — missing locale file → i18next fallback to `id`, (b) backend — Pydantic `Literal`/regex validation rejects unknown language code with 422 error, (c) email — `STRINGS`/`CATEGORY_MAP` dict lookup falls back to Indonesian silently.
- **Redaction constraints:** None — no secrets or PII in this slice.

## Files Likely Touched

- `docs/adding-a-language.md` (new)
- `frontend/src/components/layout/LanguageToggle.tsx`
- `frontend/src/services/apiClient.ts`
