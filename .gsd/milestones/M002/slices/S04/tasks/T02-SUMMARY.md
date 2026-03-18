---
id: T02
parent: S04
milestone: M002
provides:
  - LanguageCode type used in all frontend call sites instead of inline 'id' | 'en' | 'th' unions
key_files:
  - frontend/src/components/layout/LanguageToggle.tsx
  - frontend/src/services/apiClient.ts
key_decisions: []
patterns_established:
  - Import LanguageCode from lib/languages.ts instead of repeating inline type unions — LANGUAGES array is the single source of truth
observability_surfaces:
  - "grep -rn \"'id' | 'en' | 'th'\" frontend/src/ --include='*.ts' --include='*.tsx' | grep -v '.test.' → should return empty"
duration: 10m
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T02: Replace inline language type literals with LanguageCode & run verification sweep

**Replaced all 3 inline `'id' | 'en' | 'th'` type unions with `LanguageCode` from `lib/languages.ts` in LanguageToggle.tsx and apiClient.ts; R017 verification sweep confirms zero IDR and 6 {{currency}} per locale file**

## What Happened

Three inline `'id' | 'en' | 'th'` type unions existed in the frontend code:
1. `LanguageToggle.tsx` — `handleSelect` parameter type
2. `apiClient.ts` — `paths` interface language field (line 34)
3. `apiClient.ts` — `updateLanguage` function parameter (line 963)

All three were replaced with `LanguageCode` imported from `lib/languages.ts`. The `LanguageToggle.tsx` file already imported `LANGUAGES` from that module, so `LanguageCode` was added to the existing import. For `apiClient.ts`, a new `import type { LanguageCode }` was added.

After the type refactoring, a full verification sweep confirmed:
- Zero remaining inline `'id' | 'en' | 'th'` unions in non-test frontend source files
- R017 holds: 0 IDR in all locale files, 6 `{{currency}}` in each
- 600/602 tests pass — the 2 failures are pre-existing timeout flakes in `RulesPage.test.tsx` (password confirmation flow), completely unrelated to this change

## Verification

- `grep -rn "'id' | 'en' | 'th'" frontend/src/components/layout/LanguageToggle.tsx frontend/src/services/apiClient.ts` → no output (confirmed clean)
- `grep -rn "'id' | 'en' | 'th'" frontend/src/ --include='*.ts' --include='*.tsx' | grep -v '.test.'` → no output (no non-test files have inline unions)
- `grep -c "IDR" frontend/src/locales/*.json` → en:0, id:0, th:0
- `grep -c "{{currency}}" frontend/src/locales/*.json` → en:6, id:6, th:6
- `cd frontend && npx vitest run` → 600 passed, 2 failed (pre-existing timeouts in RulesPage), 1 skipped
- Slice-level: `test -f docs/adding-a-language.md` → exists (T01 deliverable)

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `grep -rn "'id' \| 'en' \| 'th'" frontend/src/components/layout/LanguageToggle.tsx frontend/src/services/apiClient.ts` | 1 (no match) | ✅ pass | <1s |
| 2 | `grep -rn "'id' \| 'en' \| 'th'" frontend/src/ --include='*.ts' --include='*.tsx' \| grep -v '.test.'` | 1 (no match) | ✅ pass | <1s |
| 3 | `grep -c "IDR" frontend/src/locales/*.json` | 1 (all 0) | ✅ pass | <1s |
| 4 | `grep -c "{{currency}}" frontend/src/locales/*.json` | 0 (all 6) | ✅ pass | <1s |
| 5 | `cd frontend && npx vitest run` | 1 | ⚠️ 600/602 pass (2 pre-existing flakes) | 53s |
| 6 | `test -f docs/adding-a-language.md` | 0 | ✅ pass | <1s |

## Diagnostics

- **Inspect type cleanup:** `grep -rn "'id' | 'en' | 'th'" frontend/src/ --include='*.ts' --include='*.tsx'` — should only match test files
- **Verify LanguageCode usage:** `grep -rn "LanguageCode" frontend/src/ --include='*.ts' --include='*.tsx'` — shows all usage sites
- **Pre-existing test flakes:** `RulesPage.test.tsx` lines 517 and 557 timeout at 5000ms in password confirmation flows — unrelated to locale work

## Deviations

None.

## Known Issues

- 2 pre-existing timeout failures in `RulesPage.test.tsx` (`successful password confirmation triggers mutation and exits edit mode`, `incorrect password shows error in dialog`) — these are test timeout flakes unrelated to locale changes, present before this task.

## Files Created/Modified

- `frontend/src/components/layout/LanguageToggle.tsx` — Added `LanguageCode` to existing import; replaced inline `'id' | 'en' | 'th'` parameter type with `LanguageCode`
- `frontend/src/services/apiClient.ts` — Added `import type { LanguageCode }` from `../lib/languages`; replaced 2 inline `'id' | 'en' | 'th'` type annotations with `LanguageCode`
- `.gsd/milestones/M002/slices/S04/tasks/T02-PLAN.md` — Added missing Observability Impact section (pre-flight fix)
