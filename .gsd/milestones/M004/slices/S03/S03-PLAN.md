# S03: Verification sweep and test hardening

**Goal:** Zero hardcoded Indonesian UI text in non-test, non-locale source. All frontend tests pass. Milestone DoD fully satisfied.
**Demo:** `rg` sweep for common Indonesian words in `.tsx`/`.ts` source returns zero rendered-string hits (only inert `label` property, code comments, and backend column matchers). `npm run test:run` shows 612+ pass. Locale files stay at 698+ keys in sync across all 3 languages.

## Must-Haves

- All residual rendered Indonesian strings extracted to locale keys: App.tsx access denied message, LoginPage banner alt, EvaluationHeader field labels (3), PromoToolsForm benchmark strings (10 `dari penjualan`), OperationalForm unit `hari`
- DetailedEvaluation.tsx metric comparisons use `metric_i18n.key` with `row.metric` fallback for old evaluations
- `benchmarkKey` added to `FieldDefinition` type and populated on 10 PROMO_TOOLS_FIELDS entries
- PromoToolsForm resolves `benchmarkKey` via `t()` when present
- All test assertions updated in lockstep (PromoToolsForm.test.tsx benchmark assertions)
- Full `rg` sweep for Indonesian text returns zero rendered-string hits
- All 612+ frontend tests pass
- All 3 locale files remain in sync (same key count)
- `npx tsc --noEmit` passes with zero type errors

## Proof Level

- This slice proves: final-assembly
- Real runtime required: no
- Human/UAT required: yes (switch language and visually confirm no stray Indonesian — documented as milestone DoD, not gated here)

## Verification

- `cd frontend && npx tsc --noEmit` — zero type errors
- `cd frontend && npm run test:run` — 612+ tests pass
- `python3 -c "import json; fs=['frontend/src/locales/id.json','frontend/src/locales/en.json','frontend/src/locales/th.json']; cs=[len(json.load(open(f))) for f in fs]; print(cs); assert len(set(cs))==1"` — all 3 files have equal key count
- `rg "id-ID" frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src | grep -v test | grep -v locale | grep -v localeMap` — zero hits
- Indonesian text sweep (command in T02) returns zero rendered-string hits after filtering out inert `label` property, code comments, backend column matchers, and `labelKey`/`displayNameKey` references

## Integration Closure

- Upstream surfaces consumed: `lib/localeMap.ts` → `getIntlLocale()` from S01; `types.ts` `FieldDefinition` with `labelKey` from S02; established `vi.mock('react-i18next')` test pattern from S01/S02
- New wiring introduced in this slice: `benchmarkKey` on FieldDefinition resolved via `t()` in PromoToolsForm; `unitKey` on FieldDefinition resolved via `t()` in OperationalForm; `metric_i18n.key` comparisons in DetailedEvaluation
- What remains before the milestone is truly usable end-to-end: nothing — this is the final slice

## Tasks

- [x] **T01: Extract residual hardcoded Indonesian from source and fix metric comparisons** `est:35m`
  - Why: S01/S02 covered the bulk of i18n extraction but left ~15 rendered Indonesian strings across 5 source files plus Indonesian-string-based metric comparisons in DetailedEvaluation. These must be extracted to complete R031.
  - Files: `frontend/src/App.tsx`, `frontend/src/pages/LoginPage.tsx`, `frontend/src/components/evaluation/EvaluationHeader.tsx`, `frontend/src/components/evaluation/forms/fields.ts`, `frontend/src/components/evaluation/forms/types.ts`, `frontend/src/components/evaluation/forms/PromoToolsForm.tsx`, `frontend/src/components/evaluation/forms/OperationalForm.tsx`, `frontend/src/components/dashboard/DetailedEvaluation.tsx`, `frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx`, `frontend/src/locales/id.json`, `frontend/src/locales/en.json`, `frontend/src/locales/th.json`
  - Do: (1) Add `benchmarkKey?: string` and `unitKey?: string` to FieldDefinition in types.ts. (2) Add `benchmarkKey` to 10 PROMO_TOOLS_FIELDS entries and `unitKey: 'common.days'` to preparationTime in fields.ts. (3) Update PromoToolsForm to pass `benchmark={field.benchmarkKey ? t(field.benchmarkKey) : field.benchmark}`. (4) Update OperationalForm to pass `unit={field.unitKey ? t(field.unitKey) : field.unit}`. (5) Replace FIELD_LABELS in EvaluationHeader with t() calls for 3 display values. (6) Extract App.tsx accessDeniedMessage to t('auth.accessDeniedAccounts'). (7) Extract LoginPage alt text to t('login.bannerAlt'). (8) Fix DetailedEvaluation metric comparisons to use `row.metric_i18n?.key` with `row.metric` fallback. (9) Add ~18 locale keys to all 3 JSON files. (10) Update PromoToolsForm.test.tsx benchmark assertions to expect key strings. Constraints: VP_DISPLAY_FIELDS keys must NOT change (backend matchers). Inert `label` property must NOT be removed. DetailedEvaluation must keep `row.metric` fallback for old evaluations.
  - Verify: `npx tsc --noEmit` passes; `npm run test:run` passes 612+; locale sync check passes; `rg "dari penjualan" frontend/src/components/evaluation/forms/PromoToolsForm.tsx` returns zero
  - Done when: All 5 source files have zero rendered hardcoded Indonesian; type check, tests, and locale sync all pass

- [x] **T02: Run milestone DoD verification gate and document results** `est:15m`
  - Why: Final verification that the entire M004 milestone Definition of Done is satisfied. Documents known exceptions with justification and updates requirement statuses.
  - Files: `.gsd/milestones/M004/slices/S03/S03-SUMMARY.md` (created)
  - Do: (1) Run full `rg` sweep for common Indonesian words in non-test/non-locale source — filter out inert `label` property, code comments, backend column matchers. Document every remaining hit with justification. (2) Run `rg "id-ID"` sweep. (3) Run full test suite. (4) Run locale sync check. (5) Run `npx tsc --noEmit`. (6) Re-check every milestone success criterion. (7) Update R031 and R032 status to validated via `gsd_update_requirement`. (8) Write S03 summary.
  - Verify: All 6 milestone success criteria pass. R031 and R032 status updated to validated.
  - Done when: All DoD checks documented with pass status; known exceptions justified; requirements validated

## Observability / Diagnostics

- **Locale key sync:** `python3 -c "import json; ..."` — verifies all 3 locale files have identical key counts. Any mismatch is a build-time signal of incomplete extraction.
- **Residual Indonesian sweep:** `rg "dari penjualan|Akses ditolak|Garansi Omzet" frontend/src --glob '!*.test.*' --glob '!locales/*'` — zero hits confirms all rendered Indonesian strings are extracted.
- **Runtime i18n fallback:** When `metric_i18n.key` is absent (pre-M002 evaluations), DetailedEvaluation falls back to `row.metric` string comparison. This is observable via browser DevTools Network tab: old evaluations will have `metric_i18n: null` in the API response, and the dashboard should still render correctly.
- **Type safety gate:** `npx tsc --noEmit` catches any FieldDefinition mismatches immediately. This is the primary signal for schema drift in `benchmarkKey`/`unitKey` additions.

## Files Likely Touched

- `frontend/src/App.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/components/evaluation/EvaluationHeader.tsx`
- `frontend/src/components/evaluation/forms/types.ts`
- `frontend/src/components/evaluation/forms/fields.ts`
- `frontend/src/components/evaluation/forms/PromoToolsForm.tsx`
- `frontend/src/components/evaluation/forms/OperationalForm.tsx`
- `frontend/src/components/dashboard/DetailedEvaluation.tsx`
- `frontend/src/components/evaluation/forms/PromoToolsForm.test.tsx`
- `frontend/src/locales/id.json`
- `frontend/src/locales/en.json`
- `frontend/src/locales/th.json`
