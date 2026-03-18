---
estimated_steps: 5
estimated_files: 2
---

# T02: Replace inline language type literals with LanguageCode & run verification sweep

**Slice:** S04 — Locale hardcode cleanup & future-proofing
**Milestone:** M002

## Description

Replace scattered `'id' | 'en' | 'th'` inline type unions in frontend code with the `LanguageCode` type from `lib/languages.ts`. This ensures the `LANGUAGES` array in `lib/languages.ts` is the single source of truth for supported language codes — adding a new language only requires updating that one array, and the type system propagates the change everywhere.

Three locations need updating:
- `LanguageToggle.tsx` line 32: `const handleSelect = async (code: 'id' | 'en' | 'th') => {`
- `apiClient.ts` line 34: `language: 'id' | 'en' | 'th';` (inside `paths` type)
- `apiClient.ts` line 963: `export const updateLanguage = async (language: 'id' | 'en' | 'th') => {`

After the type cleanup, run a final verification sweep confirming R017 still holds (no hardcoded IDR in locale files) and the full test suite passes.

## Steps

1. **Update `LanguageToggle.tsx`:**
   - Add import: `import { LanguageCode } from '../../lib/languages';` (or adjust relative path as needed — the file is at `frontend/src/components/layout/LanguageToggle.tsx`, languages at `frontend/src/lib/languages.ts`)
   - Line 32: change `(code: 'id' | 'en' | 'th')` → `(code: LanguageCode)`
   - Note: `LanguageToggle.tsx` already imports `LANGUAGES` from `../../lib/languages` — check if it does, and if so, just add `LanguageCode` to the existing import.

2. **Update `apiClient.ts`:**
   - Add import: `import type { LanguageCode } from '../lib/languages';` (file is at `frontend/src/services/apiClient.ts`)
   - Line 34: change `language: 'id' | 'en' | 'th';` → `language: LanguageCode;`
   - Line 963: change `(language: 'id' | 'en' | 'th')` → `(language: LanguageCode)`

3. **Verify no remaining inline unions:**
   ```bash
   grep -rn "'id' | 'en' | 'th'" frontend/src/ --include='*.ts' --include='*.tsx' | grep -v '.test.'
   ```
   Should return empty (zero matches in non-test files).

4. **Run R017 verification sweep:**
   ```bash
   grep -c "IDR" frontend/src/locales/*.json
   ```
   All files must return 0.
   ```bash
   grep -c "{{currency}}" frontend/src/locales/*.json
   ```
   All files must return 6.

5. **Run full frontend test suite:**
   ```bash
   cd frontend && npx vitest run
   ```
   All tests must pass with zero failures.

## Must-Haves

- [ ] `LanguageToggle.tsx` uses `LanguageCode` instead of inline `'id' | 'en' | 'th'`
- [ ] `apiClient.ts` uses `LanguageCode` instead of inline `'id' | 'en' | 'th'` (both line 34 and line 963)
- [ ] No remaining `'id' | 'en' | 'th'` inline unions in non-test frontend source files
- [ ] R017 verified: 0 IDR in locale files, 6 `{{currency}}` per file
- [ ] Full frontend test suite passes with zero regressions

## Verification

- `grep -rn "'id' | 'en' | 'th'" frontend/src/components/layout/LanguageToggle.tsx frontend/src/services/apiClient.ts` → no output
- `grep -c "IDR" frontend/src/locales/*.json` → all return 0
- `grep -c "{{currency}}" frontend/src/locales/*.json` → all return 6
- `cd frontend && npx vitest run` → all tests pass

## Inputs

- `frontend/src/lib/languages.ts` — defines `LanguageCode` type: `export type LanguageCode = (typeof LANGUAGES)[number]['code'];` which currently resolves to `'id' | 'en' | 'th'`
- `frontend/src/components/layout/LanguageToggle.tsx` — line 32 has inline `'id' | 'en' | 'th'`; may already import `LANGUAGES` from `../../lib/languages`
- `frontend/src/services/apiClient.ts` — lines 34 and 963 have inline `'id' | 'en' | 'th'`

## Observability Impact

- **Signals changed:** None at runtime — this is a pure type-level refactoring. No new logs, metrics, or endpoints.
- **Inspection:** `grep -rn "'id' | 'en' | 'th'" frontend/src/ --include='*.ts' --include='*.tsx' | grep -v '.test.'` should return empty after this task completes. TypeScript compiler (`npx tsc --noEmit`) confirms type compatibility.
- **Failure visibility:** If `LanguageCode` type is widened (new language added to `LANGUAGES` array), all call sites automatically accept the new code without edits. If narrowed (language removed), TypeScript will surface compile errors at every usage site.

## Expected Output

- `frontend/src/components/layout/LanguageToggle.tsx` — imports `LanguageCode`, uses it on `handleSelect` parameter
- `frontend/src/services/apiClient.ts` — imports `LanguageCode`, uses it on `paths` type and `updateLanguage` parameter
- Green test suite confirming type changes are compatible
