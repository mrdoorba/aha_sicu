# S04: Locale hardcode cleanup & future-proofing — UAT

**Milestone:** M002
**Written:** 2026-03-18

## UAT Type

- UAT mode: artifact-driven
- Why this mode is sufficient: This slice produced documentation and type-level refactoring — no runtime behavior changed. Verification is entirely via file existence, grep checks, and test suite results.

## Preconditions

- Working checkout of the M002 branch with S04 changes applied
- Node.js and npm available for running frontend tests
- Access to terminal for running grep/file inspection commands

## Smoke Test

Run `test -f docs/adding-a-language.md && grep -c "IDR" frontend/src/locales/*.json` — doc should exist and all locale files should return 0 for IDR count.

## Test Cases

### 1. Documentation completeness

1. Open `docs/adding-a-language.md`
2. Verify 7 touch points are documented with file paths:
   - `frontend/src/locales/<code>.json` (new locale file)
   - `frontend/src/i18n.ts` (import + resources entry)
   - `frontend/src/lib/languages.ts` (LANGUAGES array entry)
   - `backend/app/modules/auth/schemas.py` (Literal union)
   - `backend/app/modules/email/schemas.py` (regex pattern)
   - `backend/app/modules/email/template.py` (STRINGS + CATEGORY_MAP dicts)
   - `LanguageCode` type (auto-derived — documented as no-change)
3. Verify each entry has: file path, location within file, and code snippet
4. Verify a "What You Do NOT Need to Change" section exists
5. Verify verification commands are included at the end
6. **Expected:** All 7 touch points present with actionable instructions. Document is 250+ lines of substantive content.

### 2. No hardcoded IDR in locale files (R017)

1. Run `grep -c "IDR" frontend/src/locales/en.json frontend/src/locales/id.json frontend/src/locales/th.json`
2. **Expected:** All three return 0.

### 3. Currency interpolation variable present (R017)

1. Run `grep -c "{{currency}}" frontend/src/locales/en.json frontend/src/locales/id.json frontend/src/locales/th.json`
2. **Expected:** All three return 6.

### 4. No inline language type unions in production code

1. Run `grep -rn "'id' | 'en' | 'th'" frontend/src/components/layout/LanguageToggle.tsx frontend/src/services/apiClient.ts`
2. **Expected:** No output (exit code 1).

### 5. LanguageCode imported and used in LanguageToggle.tsx

1. Run `grep -n "LanguageCode" frontend/src/components/layout/LanguageToggle.tsx`
2. **Expected:** Shows import on line 8 and usage in `handleSelect` parameter type.

### 6. LanguageCode imported and used in apiClient.ts

1. Run `grep -n "LanguageCode" frontend/src/services/apiClient.ts`
2. **Expected:** Shows import line, `paths` interface usage, and `updateLanguage` parameter usage — 3 matches.

### 7. Full test suite regression

1. Run `cd frontend && npx vitest run`
2. **Expected:** 600+ tests pass. Zero failures (2 may intermittently fail due to pre-existing RulesPage flakiness — not related to S04 changes). 1 test may be skipped.

### 8. Broader sweep — no inline unions in non-test files

1. Run `grep -rn "'id' | 'en' | 'th'" frontend/src/ --include='*.ts' --include='*.tsx' | grep -v '.test.'`
2. **Expected:** No output. Only test files may contain inline unions (for test data).

## Edge Cases

### Line number drift in documentation

1. Open `docs/adding-a-language.md`
2. Cross-reference 2-3 file paths and line numbers against actual source files
3. **Expected:** Line numbers should be close to (within ~5 lines of) the referenced locations. The document notes line numbers are approximate.

### LanguageCode type derivation

1. Open `frontend/src/lib/languages.ts`
2. Verify `LanguageCode` is derived from the LANGUAGES array (e.g., `type LanguageCode = (typeof LANGUAGES)[number]['code']`)
3. Verify LANGUAGES contains entries for 'id', 'en', 'th'
4. **Expected:** LanguageCode is auto-derived, not manually maintained. Adding an entry to LANGUAGES automatically extends the type.

## Failure Signals

- `grep -c "IDR"` returns non-zero for any locale file → R017 regression
- `grep -rn "'id' | 'en' | 'th'"` matches non-test files → inline type unions not cleaned up
- `docs/adding-a-language.md` missing or under 100 lines → documentation incomplete
- Test suite has new failures beyond the 2 known RulesPage flakes → regression introduced
- `LanguageCode` not imported in LanguageToggle.tsx or apiClient.ts → type cleanup incomplete

## Requirements Proved By This UAT

- R020 — Adding a 4th language requires only locale JSON + config changes. Documentation checklist covers all touch points. LanguageCode type is centralized. No schema changes, migrations, or new components needed.
- R017 — All locale files use `{{currency}}` interpolation, zero hardcoded IDR.

## Not Proven By This UAT

- R014, R015, R016, R018, R019 — These were validated by earlier slices (S01-S03). S04 does not test runtime i18n rendering or email language selection.
- Actually adding a 4th language end-to-end — the documentation is verified as complete, but the process has not been executed. This is acceptable per R020's scope ("documented checklist confirms").

## Notes for Tester

- This is a documentation + type-hygiene slice. There are no UI changes to visually verify.
- The 2 RulesPage test flakes (`successful password confirmation triggers mutation and exits edit mode`, `incorrect password shows error in dialog`) are pre-existing timeout issues that may or may not appear in any given test run. They are unrelated to locale work.
- `fields.ts` still contains `unit: 'IDR'` on ~16 field definitions. This is intentional (M001 decision D014) — the render layer overrides via currency props. Do not flag this as a locale hardcode.
