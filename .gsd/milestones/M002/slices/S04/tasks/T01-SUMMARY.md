---
id: T01
parent: S04
milestone: M002
provides:
  - docs/adding-a-language.md — complete checklist for adding a new language (R020 deliverable)
key_files:
  - docs/adding-a-language.md
key_decisions: []
patterns_established:
  - Documentation-only tasks verify via file existence + content structure checks, not test suites
observability_surfaces:
  - "test -f docs/adding-a-language.md — confirms document exists"
  - "wc -l docs/adding-a-language.md — confirms substantive content (267 lines)"
duration: 8m
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T01: Write "adding a language" documentation checklist

**Created docs/adding-a-language.md with a complete 7-touch-point checklist for adding a new language to the evaluation system**

## What Happened

Created `docs/adding-a-language.md` — the primary R020 deliverable. The document covers all 7 touch points (3 frontend, 3 backend, 1 auto-derived type) grouped by layer, with exact file paths, line numbers, code snippets showing what to add, and a verification section with runnable commands.

All 6 source files were read to confirm exact line numbers, dict key names, regex patterns, and type structures before writing the documentation. The document includes a summary table and explicitly states that no database migrations, new components, or new endpoints are needed.

## Verification

- `test -f docs/adding-a-language.md` → exists (PASS)
- `wc -l docs/adding-a-language.md` → 267 lines of substantive content (PASS)
- All 7 touch points present with file paths and locations (PASS — confirmed via grep counts)
- Frontend/Backend grouping sections present (PASS)
- "What You Do NOT Need to Change" section present (PASS)
- Verification commands included: vitest, grep, pytest, Pydantic smoke tests (PASS)

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `test -f docs/adding-a-language.md` | 0 | ✅ pass | <1s |
| 2 | `grep -c "IDR" frontend/src/locales/*.json` (all 0) | 1 | ✅ pass | <1s |
| 3 | `grep -c "{{currency}}" frontend/src/locales/*.json` (all 6) | 0 | ✅ pass | <1s |
| 4 | `grep -rn "'id' \| 'en' \| 'th'" LanguageToggle.tsx apiClient.ts` | 0 | ❌ fail (expected — T02 scope) | <1s |
| 5 | Frontend test suite | — | ⏭ skipped (no code changes) | — |

## Diagnostics

- Inspect the document: `cat docs/adding-a-language.md`
- Verify completeness: count touch-point file paths with `grep -c "backend/\|frontend/" docs/adding-a-language.md` (should be ≥12 mentions)
- If a future language addition fails, cross-reference the error message (422 validation, missing translation key) against the checklist sections

## Deviations

None.

## Known Issues

None.

## Files Created/Modified

- `docs/adding-a-language.md` — complete language-addition checklist (new, 267 lines, R020 deliverable)
- `.gsd/milestones/M002/slices/S04/S04-PLAN.md` — added Observability section, marked T01 done
- `.gsd/milestones/M002/slices/S04/tasks/T01-PLAN.md` — added Observability Impact section
