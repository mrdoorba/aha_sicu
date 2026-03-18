---
id: S03
parent: M004
milestone: M004
provides:
  - Zero hardcoded Indonesian UI text in non-test, non-locale source (R031 validated)
  - All 612 frontend tests pass after i18n extraction (R032 validated)
  - 22 new locale keys added in S03 (16 from T01 + 6 from T02 SectionNav fix) — total 720 keys per locale file
  - benchmarkKey/unitKey pattern on FieldDefinition for resolving field-level i18n
  - metric_i18n.key-based comparisons in DetailedEvaluation with row.metric fallback
  - SectionNav section labels extracted to i18n keys
  - Complete milestone DoD verification with all 6 success criteria passing
requires:
  - slice: S01
    provides: lib/localeMap.ts getIntlLocale(), ~40 locale keys, vi.mock('react-i18next') test pattern
  - slice: S02
    provides: FieldDefinition with labelKey, ~60 locale keys, GENERIC_LABELS i18n'd, 8 date sites using getIntlLocale()
affects: []
key_files:
  - frontend/src/components/evaluation/forms/types.ts
  - frontend/src/components/evaluation/forms/fields.ts
  - frontend/src/components/evaluation/forms/PromoToolsForm.tsx
  - frontend/src/components/evaluation/forms/OperationalForm.tsx
  - frontend/src/components/evaluation/EvaluationHeader.tsx
  - frontend/src/components/evaluation/SectionNav.tsx
  - frontend/src/App.tsx
  - frontend/src/pages/LoginPage.tsx
  - frontend/src/components/dashboard/DetailedEvaluation.tsx
  - frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx
  - frontend/src/components/evaluation/SectionNav.test.tsx
  - frontend/src/locales/id.json
  - frontend/src/locales/en.json
  - frontend/src/locales/th.json
key_decisions:
  - "D033: benchmarkKey/unitKey on FieldDefinition — optional i18n key resolved via t() with fallback to original value"
  - "D034: DetailedEvaluation metric comparisons use metric_i18n.key || row.metric fallback for pre-M002 backward compatibility"
  - SectionNav labels use labelKey pattern consistent with fields.ts labelKey approach (D031)
patterns_established:
  - "benchmarkKey/unitKey pattern: extend FieldDefinition with optional i18n key, resolve via t() in form component with fallback to hardcoded value"
  - "getFieldLabel() pattern: component-local function for translating display values where object keys must remain stable (backend matchers)"
observability_surfaces:
  - "Locale key sync: python3 -c \"import json; fs=['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']; cs=[len(json.load(open(f))) for f in fs]; print(cs); assert len(set(cs))==1\" — verifies all 3 locale files have identical key counts (720)"
  - "Indonesian text sweep: rg 'dari penjualan|Akses ditolak|Garansi Omzet|kesehatan operasional' frontend/src --glob '!*.test.*' --glob '!locales/*' — zero rendered-string hits confirms all Indonesian UI text extracted"
  - "id-ID sweep: rg 'id-ID' frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src | grep -v test | grep -v locale | grep -v localeMap — zero hits confirms no hardcoded locale codes"
  - "Type safety gate: cd frontend && npx tsc --noEmit — catches FieldDefinition schema drift in benchmarkKey/unitKey additions"
  - "Test suite: cd frontend && npm run test:run — 612/612 tests pass across 68 test files"
drill_down_paths:
  - .gsd/milestones/M004/slices/S03/tasks/T01-SUMMARY.md
  - .gsd/milestones/M004/slices/S03/tasks/T02-SUMMARY.md
duration: 43m
verification_result: passed
completed_at: 2026-03-18
---

# S03: Verification sweep and test hardening

**Zero hardcoded Indonesian rendered strings in non-test/non-locale source. All 612 tests pass. 720 locale keys in sync across 3 languages. All 6 milestone success criteria verified. R031 and R032 validated.**

## What Happened

**T01** extracted 15 residual hardcoded Indonesian strings from 5 source files (App.tsx, LoginPage.tsx, EvaluationHeader.tsx, PromoToolsForm.tsx, OperationalForm.tsx) to i18n locale keys. Added `benchmarkKey` and `unitKey` optional properties to `FieldDefinition` type, populated `benchmarkKey` on 10 PROMO_TOOLS_FIELDS entries and `unitKey: 'common.days'` on preparationTime. Fixed DetailedEvaluation metric comparisons to use `row.metric_i18n?.key` with `row.metric` string fallback for pre-M002 evaluations. Added 16 new locale keys (698 → 714).

**T02** ran the full Indonesian word `rg` sweep (55 patterns) and discovered 6 additional rendered-string hits in SectionNav.tsx — hardcoded section navigation labels. Fixed immediately by extracting to `sectionNav.*` locale keys and updating the component to use `useTranslation()`. Updated SectionNav.test.tsx with i18n mock and key-based assertions. Added 6 keys (714 → 720). Re-verified all 5 checks pass. Updated R031 and R032 to validated.

## Verification

All 5 slice-level verification checks pass:

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | `npx tsc --noEmit` | ✅ zero errors | exit 0 |
| 2 | `npm run test:run` | ✅ 612/612 pass, 68 files | exit 0 |
| 3 | Locale sync (id/en/th) | ✅ [720, 720, 720] | assertion pass |
| 4 | `rg "id-ID"` (non-test/non-locale) | ✅ zero hits | exit 1 (no match) |
| 5 | Indonesian text sweep (55 patterns) | ✅ zero rendered-string hits | all hits classified as inert/comment/backend-matcher |

All 6 milestone success criteria verified:

| # | Criterion | Status |
|---|-----------|--------|
| 1 | TH renders zero Indonesian strings | ✅ rg sweep + 720 TH locale keys |
| 2 | EN renders zero Indonesian strings | ✅ rg sweep + 720 EN locale keys |
| 3 | rg for Indonesian words → zero hits | ✅ with justified exceptions (inert props, comments, backend matchers) |
| 4 | rg "id-ID" → zero hits | ✅ |
| 5 | All frontend tests pass (602+ baseline) | ✅ 612/612 |
| 6 | Translator edits one JSON file | ✅ 720 keys in sync, zero rendered hardcoded strings |

## Requirements Advanced

- R031 — Completed: extracted all remaining rendered Indonesian from source (21 strings across 7 files in S03)
- R032 — Completed: all test assertions updated in lockstep (PromoToolsForm.test, SectionNav.test)

## Requirements Validated

- R031 — Full rg sweep for 55 common Indonesian words across all non-test, non-locale .tsx/.ts source returns zero rendered-string hits. 720 locale keys in sync across 3 languages. A translator edits only their one locale JSON file.
- R032 — 612/612 frontend tests pass across 68 test files. Test assertions updated using vi.mock('react-i18next') pattern where mock t() returns key as-is.

## New Requirements Surfaced

- none

## Requirements Invalidated or Re-scoped

- none

## Deviations

T02 discovered 6 rendered Indonesian strings in SectionNav.tsx not caught by T01. These were section navigation labels ("Brand Info & Kesehatan Operasional", etc.) that the T01 plan did not identify as targets. Fixed immediately during the T02 verification sweep, adding 6 locale keys (714 → 720).

## Known Limitations

- **Inert Indonesian in fields.ts:** ~47 `label` properties, ~10 `benchmark` properties, and ~6 `displayName` properties retain hardcoded Indonesian text. These are never rendered (resolved via `labelKey`/`benchmarkKey`/`displayNameKey` at render time) and serve as human-readable code documentation. Removing them would require updating all references across the codebase with no user-facing benefit.
- **Backend matchers:** ~15 source locations match Indonesian strings from the API (category names, metric strings). These are correct — the backend sends Indonesian category names. If the backend is ever i18n'd, these matchers need updating.
- **Pre-M002 evaluation fallback:** DetailedEvaluation uses `row.metric` string comparison fallback for evaluations without `metric_i18n`. Old evaluation dashboards still display Indonesian metric names for those specific entries.
- **Duplicate section keys:** `evaluationSections.step1-6` keys (with "Step N." prefix) coexist with new `sectionNav.*` label-only keys. Both are used in different contexts.

## Follow-ups

- none — this is the final slice of M004. All milestone DoD criteria are satisfied.

## Files Created/Modified

- `frontend/src/components/evaluation/forms/types.ts` — Added `benchmarkKey?: string` and `unitKey?: string` to FieldDefinition
- `frontend/src/components/evaluation/forms/fields.ts` — Added `benchmarkKey` to 10 PROMO_TOOLS_FIELDS, `unitKey` to preparationTime
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx` — Resolve benchmarkKey via t() when present
- `frontend/src/components/evaluation/forms/OperationalForm.tsx` — Resolve unitKey via t() when present
- `frontend/src/components/evaluation/EvaluationHeader.tsx` — Replaced static FIELD_LABELS with getFieldLabel() using t()
- `frontend/src/components/evaluation/SectionNav.tsx` — Changed `label` to `labelKey`, added useTranslation() + t()
- `frontend/src/App.tsx` — Extracted accessDeniedMessage to t('auth.accessDeniedAccounts')
- `frontend/src/pages/LoginPage.tsx` — Extracted banner alt text to t('login.bannerAlt')
- `frontend/src/components/dashboard/DetailedEvaluation.tsx` — Fixed metric comparisons to use metric_i18n.key with fallback
- `frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx` — Updated benchmark assertions to key strings
- `frontend/src/components/evaluation/SectionNav.test.tsx` — Added vi.mock('react-i18next'), key-based assertions
- `frontend/src/locales/id.json` — Added 22 keys (698 → 720)
- `frontend/src/locales/en.json` — Added 22 keys (698 → 720)
- `frontend/src/locales/th.json` — Added 22 keys (698 → 720)

## Forward Intelligence

### What the next slice should know
- M004 is the final milestone in the i18n series. There is no next slice — this is milestone closure. The app has 720 locale keys across 3 languages (id/en/th), all in sync. Every rendered UI string resolves through `t()` + locale files.
- Adding a new language requires only: (1) create `{lang}.json` with 720 keys, (2) add import to `i18n.ts`, (3) add to `LANGUAGES` array and backend `STRINGS`/`CATEGORY_MAP`. No schema changes, no migrations, no component changes.

### What's fragile
- **fields.ts dual-property pattern** — `label` + `labelKey`, `benchmark` + `benchmarkKey`, `displayName` + `displayNameKey` coexist on FieldDefinition. The hardcoded properties are never rendered but could confuse future developers who might use `field.label` directly instead of `t(field.labelKey!)`. Any new form component must resolve the `*Key` variant.
- **Backend matcher strings** — ~15 locations match Indonesian strings from the API. If the backend ever returns i18n'd category/metric names, these matchers will break silently (no match = missing data, not an error).

### Authoritative diagnostics
- **Locale key sync check:** `python3 -c "import json; fs=['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']; cs=[len(json.load(open(f))) for f in fs]; print(cs); assert len(set(cs))==1"` — if this fails, a locale file is missing keys. The count should be 720+ (may increase with future features). This is the single fastest signal for i18n drift.
- **Indonesian rendered-text sweep:** `rg -i "dari penjualan|akses ditolak|garansi omzet" frontend/src --glob '!*.test.*' --glob '!locales/*'` — should return only `fields.ts` inert properties. Any hit in a `.tsx` component render path indicates a missed extraction.
- **Full test suite:** `cd frontend && npm run test:run` — 612 tests across 68 files. Test failures after i18n changes usually mean an assertion still expects a hardcoded Indonesian string instead of an i18n key.
- **Type check:** `cd frontend && npx tsc --noEmit` — catches FieldDefinition type mismatches (e.g. missing benchmarkKey on a new field that needs one).

### What assumptions changed
- **Original:** T01 plan identified 15 residual strings across 5 files. **Actual:** T02 sweep found 6 additional strings in SectionNav.tsx, bringing the total to 21 across 7 files. The T01 scope was incomplete — full `rg` sweep was essential for catching all remaining strings.
- **Original:** 714 locale keys expected after T01. **Actual:** 720 after T02 SectionNav fix.
