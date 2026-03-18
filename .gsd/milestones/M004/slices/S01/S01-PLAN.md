# S01: Extract hardcoded strings from un-i18n'd components

**Goal:** Every visible string in EvaluationHistoryTable, DeleteEvaluationDialog, DowntimeWarningDialog, and SelectField routes through `t()` with keys from locale files. A `localeMap.ts` utility maps i18next language codes to Intl locale codes for downstream use.

**Demo:** Switch to TH → History table, Delete dialog, Downtime dialog, SelectField all render Thai text (translation keys in test mode). Switch to EN → same components render English keys. All frontend tests pass.

## Must-Haves

- All 4 target components use `useTranslation()` + `t('key')` for every visible string
- ~40 new locale keys added to `id.json`, `en.json`, `th.json` in lockstep
- `lib/localeMap.ts` exports `getIntlLocale(lang)` mapping id→id-ID, en→en-US, th→th-TH
- EvaluationHistoryTable's `dateFormatter` uses dynamic locale from `localeMap.ts` (not hardcoded `'id-ID'`)
- New DowntimeWarningDialog test file proves the component renders i18n keys
- All existing test assertions updated from hardcoded Indonesian text to i18n key patterns
- Existing keys reused where applicable: `common.cancel`, `common.retry`, `common.previous`, `common.next`, `common.pageOf`

## Verification

- `cd frontend && npm run test:run -- --reporter=verbose 2>&1 | tail -30` — all tests pass (602+ baseline)
- `rg "Pilih\.\.\." frontend/src --type-add 'src:*.tsx' --type-add 'src:*.ts' -t src | grep -v test | grep -v locale` returns no hits
- `rg "Gagal memuat" frontend/src/components/evaluations/EvaluationHistoryTable.tsx` returns no hits
- `rg "Hapus Evaluasi" frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` returns no hits
- `rg "Sistem Tidak" frontend/src/components/DowntimeWarningDialog.tsx` returns no hits
- `rg "id-ID" frontend/src/components/evaluations/EvaluationHistoryTable.tsx` returns no hits

## Integration Closure

- Upstream surfaces consumed: existing `useTranslation` pattern from 10+ components, existing `common.*` locale keys
- New wiring introduced in this slice: `lib/localeMap.ts` (`getIntlLocale()` function) — consumed by S02 for date formatting across 8 files
- What remains before the milestone is truly usable end-to-end: S02 (date formatting + field labels + month constants), S03 (verification sweep)

## Tasks

- [x] **T01: Extract strings from SelectField and DowntimeWarningDialog, create localeMap.ts** `est:45m`
  - Why: Proves the i18n extraction pattern on the two smallest components. Creates the `localeMap.ts` boundary deliverable needed by S02 and by T03's dateFormatter fix. Adds a new DowntimeWarningDialog test (none exists today).
  - Files: `frontend/src/components/evaluation/forms/SelectField.tsx`, `frontend/src/components/evaluation/forms/SelectField.test.tsx`, `frontend/src/components/DowntimeWarningDialog.tsx`, `frontend/src/components/DowntimeWarningDialog.test.tsx` (new), `frontend/src/lib/localeMap.ts` (new), `frontend/src/lib/localeMap.test.ts` (new), `frontend/src/locales/id.json`, `frontend/src/locales/en.json`, `frontend/src/locales/th.json`
  - Do: (1) Create `lib/localeMap.ts` with `getIntlLocale(lang)` — 3 mappings + id-ID fallback. Write unit test. (2) In SelectField.tsx add `useTranslation()`, replace `"Pilih..."` placeholder with `t('common.select')`. Update SelectField.test.tsx: add `vi.mock('react-i18next')` at top level (follow existing mock pattern in codebase), update assertion for placeholder from `'Pilih...'` to `'common.select'`. (3) In DowntimeWarningDialog.tsx add `useTranslation()`, extract 5 strings to `downtime.*` keys: title, description (use interpolation for time range), dismiss button. Add `downtime.*` keys to all 3 locale files. (4) Create DowntimeWarningDialog.test.tsx — basic render test verifying i18n keys render, following established test mock pattern. (5) Add `common.select` and `common.delete` keys to all 3 locale files. Skill: `test` for test generation patterns.
  - Verify: `cd frontend && npm run test:run -- SelectField DowntimeWarningDialog localeMap --reporter=verbose`
  - Done when: SelectField and DowntimeWarningDialog have zero hardcoded Indonesian, DowntimeWarningDialog has a passing test, localeMap.ts has a passing unit test, all 3 locale files have the new keys.

- [x] **T02: Extract strings from DeleteEvaluationDialog** `est:30m`
  - Why: Medium-complexity component with 8 hardcoded strings and ~12 test assertion changes. Self-contained extraction following the pattern proven in T01.
  - Files: `frontend/src/components/evaluations/DeleteEvaluationDialog.tsx`, `frontend/src/components/evaluations/DeleteEvaluationDialog.test.tsx`, `frontend/src/locales/id.json`, `frontend/src/locales/en.json`, `frontend/src/locales/th.json`
  - Do: (1) In DeleteEvaluationDialog.tsx add `useTranslation()`, replace all 8 hardcoded strings with `t()` calls using `deleteDialog.*` keys. Reuse `common.cancel` for "Batal". The description text (two Indonesian sentences) goes in a single `deleteDialog.description` key. (2) Add all `deleteDialog.*` keys to all 3 locale files. (3) Update DeleteEvaluationDialog.test.tsx: add `vi.mock('react-i18next')` at top level, update ~12 assertions from Indonesian text to i18n keys. Check both `getByText`/`queryByText` assertions and `aria-label` attribute assertions. Skill: `test` for test update patterns.
  - Verify: `cd frontend && npm run test:run -- DeleteEvaluationDialog --reporter=verbose`
  - Done when: DeleteEvaluationDialog has zero hardcoded Indonesian, all DeleteEvaluationDialog tests pass with key-based assertions.

- [x] **T03: Extract strings from EvaluationHistoryTable and wire dynamic dateFormatter** `est:1h`
  - Why: Largest component (~25 strings, ~20 test assertions). The `dateFormatter` is a module-level `const` using hardcoded `'id-ID'` — it must become dynamic using `localeMap.ts` from T01. This is the riskiest piece in the slice.
  - Files: `frontend/src/components/evaluations/EvaluationHistoryTable.tsx`, `frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx`, `frontend/src/locales/id.json`, `frontend/src/locales/en.json`, `frontend/src/locales/th.json`
  - Do: (1) In EvaluationHistoryTable.tsx add `useTranslation()`. (2) Move the `dateFormatter` from a module-level const into the component body — use `useMemo` keyed on `i18n.language` to create `new Intl.DateTimeFormat(getIntlLocale(i18n.language), ...)`. Import `getIntlLocale` from `lib/localeMap`. The `BrandAccordionRow` sub-component also uses `dateFormatter` — pass it as a prop or move the sub-component inside the parent's scope so it accesses the memoized value. (3) Replace all ~25 hardcoded strings with `t()` calls using `history.table.*` keys. Reuse existing keys: `common.previous`, `common.next`, `common.pageOf` (pass `{ page, totalPages: pages }` to match existing key signature), `common.retry`. (4) Add all `history.table.*` keys to all 3 locale files. (5) Update EvaluationHistoryTable.test.tsx: add `vi.mock('react-i18next')` at top level, update ~20 assertions from Indonesian text to i18n keys. Also mock or handle the `localeMap` import in tests. Skill: `test` for test update patterns.
  - Verify: `cd frontend && npm run test:run -- EvaluationHistoryTable --reporter=verbose` and `rg "id-ID" frontend/src/components/evaluations/EvaluationHistoryTable.tsx` returns no hits
  - Done when: EvaluationHistoryTable has zero hardcoded Indonesian, `dateFormatter` uses dynamic locale from localeMap.ts, all EvaluationHistoryTable tests pass with key-based assertions.

## Observability / Diagnostics

- **Runtime signal:** When language is switched via `LanguageToggle`, all 4 target components re-render with translated text from locale JSON. The `useTranslation()` hook triggers re-render on `i18n.language` change — no manual subscription needed.
- **Inspection surface:** Open React DevTools → filter by component name → inspect `t` function calls in props/render output. Or switch browser language and visually confirm text changes.
- **Failure visibility:** Missing i18n keys render as the raw key string (e.g., `"downtime.title"` appears literally on screen). This is by i18next design — `t()` returns the key when no translation exists. Tests validate keys resolve correctly via mocked `t` that returns keys.
- **localeMap diagnostic:** `getIntlLocale('xx')` for unknown codes returns `'id-ID'` (default fallback). No error thrown — fallback is intentional.
- **Redaction:** No secrets or PII in locale files. All strings are user-facing UI text.

## Files Likely Touched

- `frontend/src/lib/localeMap.ts` (new)
- `frontend/src/lib/localeMap.test.ts` (new)
- `frontend/src/components/evaluation/forms/SelectField.tsx`
- `frontend/src/components/evaluation/forms/SelectField.test.tsx`
- `frontend/src/components/DowntimeWarningDialog.tsx`
- `frontend/src/components/DowntimeWarningDialog.test.tsx` (new)
- `frontend/src/components/evaluations/DeleteEvaluationDialog.tsx`
- `frontend/src/components/evaluations/DeleteEvaluationDialog.test.tsx`
- `frontend/src/components/evaluations/EvaluationHistoryTable.tsx`
- `frontend/src/components/evaluations/EvaluationHistoryTable.test.tsx`
- `frontend/src/locales/id.json`
- `frontend/src/locales/en.json`
- `frontend/src/locales/th.json`
