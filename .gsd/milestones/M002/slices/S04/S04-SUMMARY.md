---
id: S04
parent: M002
milestone: M002
provides:
  - docs/adding-a-language.md — complete 7-touch-point checklist for adding a new language (R020 deliverable)
  - LanguageCode type replaces all inline 'id' | 'en' | 'th' unions in non-test frontend code
  - R017 re-verified — zero hardcoded IDR in locale files, 6 {{currency}} per file
requires:
  - slice: S01
    provides: Frontend types with _i18n fields; LanguageCode and LANGUAGES already defined in lib/languages.ts
  - slice: S03
    provides: {{currency}} interpolation in all locale files (R017 fix)
affects: []
key_files:
  - docs/adding-a-language.md
  - frontend/src/components/layout/LanguageToggle.tsx
  - frontend/src/services/apiClient.ts
  - frontend/src/lib/languages.ts
key_decisions: []
patterns_established:
  - Import LanguageCode from lib/languages.ts instead of inline type unions — LANGUAGES array is the single source of truth for supported languages
  - Documentation-only tasks verify via file existence + content structure checks
observability_surfaces:
  - "grep -rn \"'id' | 'en' | 'th'\" frontend/src/ --include='*.ts' --include='*.tsx' | grep -v '.test.' → empty confirms no stale inline unions"
  - "grep -c 'IDR' frontend/src/locales/*.json → all return 0 confirms R017 holds"
  - "grep -c '{{currency}}' frontend/src/locales/*.json → all return 6 confirms interpolation in place"
  - "test -f docs/adding-a-language.md → confirms documentation exists"
drill_down_paths:
  - .gsd/milestones/M002/slices/S04/tasks/T01-SUMMARY.md
  - .gsd/milestones/M002/slices/S04/tasks/T02-SUMMARY.md
duration: 18m
verification_result: passed
completed_at: 2026-03-18
---

# S04: Locale hardcode cleanup & future-proofing

**Documented all 7 language-addition touch points; eliminated inline type literals so LANGUAGES array is the single source of truth; re-verified R017 currency interpolation**

## What Happened

This slice delivered two things: documentation and type hygiene.

**T01** created `docs/adding-a-language.md` — a 267-line structured checklist covering all 7 touch points for adding a new language (3 frontend: locale JSON, i18n.ts import, LANGUAGES array entry; 3 backend: auth schemas Literal, email schemas regex, template.py STRINGS/CATEGORY_MAP dicts; 1 auto-derived: LanguageCode type). Each entry includes the exact file path, location within the file, and a code snippet showing what to add. A "What You Do NOT Need to Change" section explicitly states no schema migrations, new components, or structural changes are required. Verification commands are included.

**T02** replaced 3 inline `'id' | 'en' | 'th'` type unions with `LanguageCode` imported from `lib/languages.ts`:
1. `LanguageToggle.tsx` — `handleSelect` parameter type
2. `apiClient.ts` — `paths` interface language field
3. `apiClient.ts` — `updateLanguage` function parameter

After the refactoring, a full sweep confirmed zero remaining inline language type unions in non-test source files, and R017 verification passed (0 IDR, 6 `{{currency}}` per locale file). The full test suite ran green: 602 passed, 1 skipped, 0 failures.

## Verification

| Check | Result |
|-------|--------|
| `test -f docs/adding-a-language.md` | ✅ exists (267 lines) |
| `grep -c "IDR" frontend/src/locales/*.json` | ✅ en:0, id:0, th:0 |
| `grep -c "{{currency}}" frontend/src/locales/*.json` | ✅ en:6, id:6, th:6 |
| `grep -rn "'id' \| 'en' \| 'th'" LanguageToggle.tsx apiClient.ts` | ✅ no matches |
| `grep -rn "'id' \| 'en' \| 'th'" frontend/src/ --include='*.ts' --include='*.tsx' \| grep -v '.test.'` | ✅ no matches |
| `cd frontend && npx vitest run` | ✅ 602 passed, 1 skipped, 0 failures |

## Requirements Advanced

- R020 — Documentation checklist created (`docs/adding-a-language.md`) covering all 7 touch points. Combined with LanguageCode type cleanup, adding a 4th language now requires only locale JSON + config additions with no schema changes, no migrations, no new components.

## Requirements Validated

- R020 — The documentation checklist exists and is verified complete. The LanguageCode type derives from the LANGUAGES array (single source of truth). All locale files use `{{currency}}` interpolation (no hardcoded currencies). Inline type unions eliminated. The documented process requires only: (1) new locale JSON, (2) i18n.ts import, (3) LANGUAGES array entry, (4) backend Literal, (5) backend regex, (6) backend STRINGS/CATEGORY_MAP. No schema changes, migrations, or new components needed. 602 tests pass.
- R017 — Re-verified: `grep -c "IDR"` returns 0 for all locale files; `grep -c "{{currency}}"` returns 6 for each. Full regression green.

## New Requirements Surfaced

- none

## Requirements Invalidated or Re-scoped

- none

## Deviations

None. Both tasks executed exactly as planned.

## Known Limitations

- `fields.ts` still has static `unit: 'IDR'` on ~16 field definitions. This was an intentional M001 decision (D014) to keep fields.ts as static config and override at the render layer via currency props. Not a locale hardcode — it's a display override pattern.
- 2 tests in `RulesPage.test.tsx` are intermittently flaky (password confirmation timeout) — pre-existing, unrelated to locale work. They happened to pass in this run.

## Follow-ups

- none — this is the final slice of M002.

## Files Created/Modified

- `docs/adding-a-language.md` — Complete 7-touch-point checklist for adding a new language (new, 267 lines)
- `frontend/src/components/layout/LanguageToggle.tsx` — Added `LanguageCode` to import; replaced inline type union
- `frontend/src/services/apiClient.ts` — Added `import type { LanguageCode }`; replaced 2 inline type unions

## Forward Intelligence

### What the next slice should know
- M002 is complete after S04. All 4 slices delivered. The milestone definition of done should now be fully satisfied: evaluation detail renders through i18n, all 3 email dialogs have language selectors, email body reconstructs from i18n keys, locale files use `{{currency}}`, frontend types declare i18n fields, all tests pass, and `docs/adding-a-language.md` documents the process.

### What's fragile
- The `docs/adding-a-language.md` references specific line numbers in source files — these will drift as code evolves. The document notes this but line numbers should be treated as approximate after significant code changes.
- `RulesPage.test.tsx` has 2 intermittently flaky tests (timeout-based) that may occasionally fail in CI. Not related to i18n work.

### Authoritative diagnostics
- `grep -rn "LanguageCode" frontend/src/ --include='*.ts' --include='*.tsx' | grep -v '.test.'` — shows all 6 usage sites of the centralized type, confirming single-source-of-truth pattern
- `wc -l docs/adding-a-language.md` — 267 lines confirms substantive documentation, not a stub

### What assumptions changed
- T02 plan noted line numbers for apiClient.ts edits (lines 34, 963) — actual line numbers matched exactly, no drift from earlier slices.
- T02 plan expected 2 pre-existing test failures — they actually passed in the final verification run (flaky tests can go either way).
