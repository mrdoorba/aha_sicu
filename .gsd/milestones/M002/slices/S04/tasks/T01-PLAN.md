---
estimated_steps: 3
estimated_files: 1
---

# T01: Write "adding a language" documentation checklist

**Slice:** S04 — Locale hardcode cleanup & future-proofing
**Milestone:** M002

## Description

Create `docs/adding-a-language.md` — the primary R020 deliverable. This documents every file that must be modified when adding a 4th (or Nth) language to the system. The checklist should be concrete enough that a developer can follow it mechanically without grepping the codebase.

The research identified 7 touch points grouped into frontend (3) and backend (3), plus one auto-derived type. The documentation must cover all of them with specific file paths, the section within each file to edit, and exactly what to add.

**Key constraint:** Do NOT modify any code files. This task is documentation only.

## Steps

1. Create the `docs/` directory if it doesn't exist (it doesn't currently).

2. Write `docs/adding-a-language.md` with the following structure:
   - **Title & purpose** — explain this is the checklist for adding a new language to the evaluation system
   - **Prerequisites** — what you need before starting (translated locale strings, translated backend email strings/category names)
   - **Frontend changes** (3 files):
     - `frontend/src/locales/<code>.json` — copy an existing locale file (e.g., `en.json`) and translate all values. Keep the same key structure. All `{{currency}}` interpolation variables must be preserved as-is.
     - `frontend/src/i18n.ts` — add `import <code> from './locales/<code>.json';` and add `<code>: { translation: <code> }` to the `resources` object.
     - `frontend/src/lib/languages.ts` — add an entry to the `LANGUAGES` array: `{ code: '<code>' as const, flag: '<emoji>', label: '<CODE>' }`. This automatically extends the `LanguageCode` type used throughout the frontend.
   - **Backend changes** (3 files):
     - `backend/app/modules/auth/schemas.py` — add the new code to the `Literal["id", "en", "th"]` union on `UpdateLanguageRequest.language` (line ~22).
     - `backend/app/modules/email/schemas.py` — add the new code to the regex pattern `"^(id|en|th)$"` on `SendEmailRequest.language` (line ~16).
     - `backend/app/modules/email/template.py` — add a new language key to both the `STRINGS` dict (email template strings — subject, greeting, headers, etc.) and the `CATEGORY_MAP` dict (translated category names for email body).
   - **What you do NOT need to change** — emphasize: no database migrations, no schema changes, no new components, no new API endpoints. All changes are config-level additions to existing arrays/dicts/unions.
   - **Verification** — list the commands to confirm the new language works: run frontend tests (`cd frontend && npx vitest run`), run backend tests, check locale file has no hardcoded currency (`grep -c "IDR" frontend/src/locales/<code>.json` → 0).

3. Verify the file exists and is well-structured: `test -f docs/adding-a-language.md`.

## Must-Haves

- [ ] `docs/adding-a-language.md` exists
- [ ] All 7 touch points are documented with specific file paths and locations
- [ ] Grouped by frontend vs backend
- [ ] Explicitly states no migrations, no schema changes, no new components needed
- [ ] Includes verification commands

## Verification

- `test -f docs/adding-a-language.md` — file exists
- Manual review: all 7 touch points listed with file paths, locations, and what to add
- Document includes the "what you do NOT need to change" section

## Inputs

- Research findings: 7 touch points identified (3 frontend, 3 backend, 1 auto-derived type)
- `frontend/src/lib/languages.ts` — defines `LANGUAGES` array and `LanguageCode` type
- `frontend/src/i18n.ts` — configures i18next with locale imports
- `backend/app/modules/auth/schemas.py` — `Literal["id", "en", "th"]` on line ~22
- `backend/app/modules/email/schemas.py` — regex `"^(id|en|th)$"` on line ~16
- `backend/app/modules/email/template.py` — `STRINGS` dict (line ~37) and `CATEGORY_MAP` dict (line ~133)

## Observability Impact

- **Signals changed:** None — this task creates documentation only, no runtime code changes.
- **Inspection surface:** `test -f docs/adding-a-language.md` and `wc -l docs/adding-a-language.md` to confirm existence and substantive content (should be 100+ lines).
- **Failure visibility:** If the document is missing or incomplete, a developer adding a new language will miss touch points, causing: (a) 422 validation errors on backend language fields, (b) untranslated UI strings falling back to Indonesian, (c) missing email template translations.
- **Future agent inspection:** Read `docs/adding-a-language.md` and verify it lists all 7 touch points with file paths, section locations, and code snippets.

## Expected Output

- `docs/adding-a-language.md` — complete, structured checklist for adding a new language, satisfying R020's documentation requirement
