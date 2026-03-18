---
id: T02
parent: S02
milestone: M004
provides:
  - labelKey property on all 47 FieldDefinition instances
  - displayNameKey property on all 8 CategoryDefinition instances
  - 55 new locale keys (fields.* and categories.*) in all 3 JSON files (id, en, th)
key_files:
  - frontend/src/components/evaluation/forms/types.ts
  - frontend/src/components/evaluation/forms/fields.ts
  - frontend/src/locales/id.json
  - frontend/src/locales/en.json
  - frontend/src/locales/th.json
key_decisions:
  - labelKey naming convention is fields.<category>.<camelCaseKey> with dot-separated nesting for competition products (e.g. fields.competition.product1.productName)
  - Indonesian locale values preserve exact hardcoded label text from fields.ts for zero-diff when T03 wires t()
patterns_established:
  - i18n key naming for form fields follows fields.<category>.<fieldKey> convention
  - Category display name keys follow categories.<categoryKey> convention
observability_surfaces:
  - grep -c "labelKey" fields.ts should return 47; grep -c "displayNameKey" fields.ts should return 8
  - All 3 locale files have equal key counts (685 each after this task)
  - Missing locale key renders as raw key string in UI (e.g. "fields.operational.unfulfilledOrderRate") — primary failure signal
duration: 10m
verification_result: passed
completed_at: 2026-03-18
blocker_discovered: false
---

# T02: Add labelKey to all 47 field definitions and displayNameKey to all 8 categories

**Added labelKey/displayNameKey properties to FieldDefinition and CategoryDefinition types, populated them across all field arrays and categories, and added 55 locale keys to all 3 JSON files**

## What Happened

Extended `FieldDefinition` with optional `labelKey?: string` and `CategoryDefinition` with optional `displayNameKey?: string` in `types.ts`. Populated `labelKey` on all 47 field definitions across 8 field arrays (OPERATIONAL_FIELDS through COMPETITION_FIELDS) and `displayNameKey` on all 8 entries in MANUAL_DATA_FIELDS. Added 55 corresponding locale keys to `id.json`, `en.json`, and `th.json` — Indonesian values match the existing hardcoded `label`/`displayName` strings exactly, English and Thai are professional translations. Total key count per file went from 630 to 685.

The plan estimated 51 field definitions, but the actual codebase has 47 (5+7+3+11+2+2+2+15). The discrepancy is in the plan's approximation — all actual field definitions have `labelKey` populated.

## Verification

- TypeScript check (`npx tsc --noEmit`) — zero errors
- All 612 tests pass (`npm run test:run`) — additive change, nothing broken
- `grep -c "labelKey" fields.ts` = 47 (all field definitions)
- `grep -c "displayNameKey" fields.ts` = 8 (all categories)
- All 3 locale files have 685 keys each (equal counts)
- `rg "INDO_MONTHS" frontend/src` — zero hits (T01 rename preserved)

## Verification Evidence

| # | Command | Exit Code | Verdict | Duration |
|---|---------|-----------|---------|----------|
| 1 | `cd frontend && npm run test:run` | 0 | ✅ pass | 21s |
| 2 | `rg "INDO_MONTHS" frontend/src -t src` | 1 (no match) | ✅ pass | <1s |
| 3 | `rg "Bulan Ini\|Bulan -1" frontend/src -t src \| grep -v test \| grep -v locale` | 0 | ⚠️ expected (fields.ts still has hardcoded label — T03 will resolve) | <1s |
| 5 | `rg hardcoded strings in .tsx` | 0 | ⚠️ expected (T03 pending) | <1s |
| 6 | locale file key counts | 0 | ✅ pass (685 each) | <1s |
| 7 | `cd frontend && npx tsc --noEmit` | 0 | ✅ pass | 21s |
| 8 | locale key count equality check | 0 | ✅ pass | <1s |

## Diagnostics

- `grep -c "labelKey" frontend/src/components/evaluation/forms/fields.ts` — should return 47
- `grep -c "displayNameKey" frontend/src/components/evaluation/forms/fields.ts` — should return 8
- `python3 -c "import json; [print(f'{f}: {len(json.load(open(f)))}') for f in ['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']]"` — all should show 685
- If a `fields.*` or `categories.*` key is missing from a locale file, the UI renders the raw key string (e.g. `"fields.operational.unfulfilledOrderRate"`) after T03 wires the keys

## Deviations

- Plan estimated 51 field definitions; actual codebase has 47. All existing field definitions have `labelKey` — no fields were missed.
- Plan estimated ~59 new keys per file; actual is 55 (47 fields + 8 categories). The 4-key gap was the plan's overcounting.

## Known Issues

None.

## Files Created/Modified

- `frontend/src/components/evaluation/forms/types.ts` — Added `labelKey?: string` to FieldDefinition and `displayNameKey?: string` to CategoryDefinition
- `frontend/src/components/evaluation/forms/fields.ts` — Added labelKey to all 47 field definitions and displayNameKey to all 8 category definitions
- `frontend/src/locales/id.json` — Added 55 new keys (fields.* and categories.* namespaces) with Indonesian translations
- `frontend/src/locales/en.json` — Added 55 new keys with English translations
- `frontend/src/locales/th.json` — Added 55 new keys with Thai translations
