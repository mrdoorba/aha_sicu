---
estimated_steps: 5
estimated_files: 7
---

# T01: Fix R017 locale hardcodes + create EmailLanguageSelector component

**Slice:** S03 — Email language selector & i18n body rebuild
**Milestone:** M002

## Description

This task delivers two foundational pieces that all subsequent S03 tasks depend on:

1. **R017 locale fix**: Replace 6 hardcoded `IDR` strings with `{{currency}}` interpolation variable across all 3 locale files. The backend already provides `currency` in i18n vars, so these keys will render the correct currency code (IDR or THB) based on marketplace.

2. **Shared LANGUAGES constant + EmailLanguageSelector component**: Extract the `LANGUAGES` array from `LanguageToggle.tsx` into a shared `lib/languages.ts` module, then build a reusable `EmailLanguageSelector` dropdown component that the next two tasks will integrate into all email dialogs.

**Relevant installed skill:** `test` — for generating and running component tests.

## Steps

1. **Fix R017 locale keys** — In each of `frontend/src/locales/id.json`, `en.json`, `th.json`, find and replace `IDR` with `{{currency}}` in these 6 keys:
   - `scoring.monthlySales.pass` — replace all `IDR` occurrences (2 per key)
   - `scoring.monthlySales.fail` — replace all `IDR` occurrences (2 per key)
   - `scoring.competitionProduct.pass` — replace `IDR` (1 occurrence)
   - `scoring.competitionProduct.fail` — replace `IDR` (2 occurrences)
   - `forms.competition.competitive` — replace `IDR` (1 occurrence)
   - `forms.competition.notCompetitive` — replace `IDR` (2 occurrences)
   
   **Exact replacements per key** (each file):
   - `IDR {{price}}` → `{{currency}} {{price}}`
   - `IDR {{marketPrice}}` → `{{currency}} {{marketPrice}}`
   - `IDR {{sellingPrice}}` → `{{currency}} {{sellingPrice}}`
   - `IDR {{value}}` → `{{currency}} {{value}}`
   - `IDR {{avg}}` → `{{currency}} {{avg}}`

2. **Create `frontend/src/lib/languages.ts`** — Export the `LANGUAGES` array:
   ```ts
   export const LANGUAGES = [
     { code: 'id' as const, flag: '🇮🇩', label: 'ID' },
     { code: 'en' as const, flag: '🇬🇧', label: 'EN' },
     { code: 'th' as const, flag: '🇹🇭', label: 'TH' },
   ];
   export type LanguageCode = (typeof LANGUAGES)[number]['code'];
   ```

3. **Update `frontend/src/components/layout/LanguageToggle.tsx`** — Remove the local `LANGUAGES` constant and import it from `../../lib/languages`. No other changes. Run existing tests to confirm no regressions.

4. **Create `frontend/src/components/shared/EmailLanguageSelector.tsx`** — A dropdown component:
   - Props: `value: string`, `onChange: (lang: string) => void`, optional `className?: string`
   - Renders a `<select>` (or styled dropdown) with the 3 languages from `LANGUAGES`
   - Each option shows `flag + label` (e.g. "🇮🇩 ID", "🇬🇧 EN", "🇹🇭 TH")
   - Include a label (use `useTranslation` for `t('emailLanguageSelector.label')` or similar — add the key to all 3 locale files: e.g. "Email Language" / "Bahasa Email" / "ภาษาอีเมล")
   - Use project's existing UI components (shadcn `Select` or plain `<select>` matching existing patterns)

5. **Write `frontend/src/components/shared/EmailLanguageSelector.test.tsx`** — Tests:
   - Renders a dropdown with 3 language options
   - Displays the current value as selected
   - Calls `onChange` with the new language code when user selects a different option
   - Defaults work correctly (renders without errors when value is 'id', 'en', or 'th')

## Must-Haves

- [ ] All 6 locale keys × 3 files have `{{currency}}` instead of hardcoded `IDR`
- [ ] `LANGUAGES` array exported from `frontend/src/lib/languages.ts`
- [ ] `LanguageToggle.tsx` imports `LANGUAGES` from shared location (no local copy)
- [ ] `EmailLanguageSelector` component renders and fires onChange
- [ ] Component test file exists and passes
- [ ] No existing tests broken

## Verification

- `cd frontend && npx vitest run src/components/shared/EmailLanguageSelector.test.tsx --reporter=verbose` — new tests pass
- `cd frontend && npx vitest run --reporter=verbose 2>&1 | tail -5` — full regression: 0 failures
- `grep -c "IDR" frontend/src/locales/id.json frontend/src/locales/en.json frontend/src/locales/th.json` — should return 0 for each file (all IDR occurrences replaced)

## Inputs

- `frontend/src/locales/id.json`, `en.json`, `th.json` — current locale files with hardcoded IDR in 6 keys
- `frontend/src/components/layout/LanguageToggle.tsx` — contains the `LANGUAGES` array to extract
- Existing UI component patterns (shadcn) for building the dropdown

## Expected Output

- `frontend/src/locales/id.json` — 6 keys updated: IDR → {{currency}}
- `frontend/src/locales/en.json` — 6 keys updated: IDR → {{currency}}
- `frontend/src/locales/th.json` — 6 keys updated: IDR → {{currency}}
- `frontend/src/lib/languages.ts` — new file exporting `LANGUAGES` and `LanguageCode`
- `frontend/src/components/layout/LanguageToggle.tsx` — modified to import LANGUAGES from shared
- `frontend/src/components/shared/EmailLanguageSelector.tsx` — new reusable dropdown component
- `frontend/src/components/shared/EmailLanguageSelector.test.tsx` — new test file

## Observability Impact

- **Signals changed:** 6 locale keys per file now use `{{currency}}` interpolation variable instead of hardcoded `IDR`. Any runtime rendering of these keys that doesn't pass a `currency` variable will show `{{currency}}` literally — this is immediately visible in scoring messages and competition analysis text.
- **Inspection surfaces:** `grep -c "IDR" frontend/src/locales/*.json` returns 0 for all files. `EmailLanguageSelector` renders with `data-testid="email-language-select"` for test/automation targeting. The shared `LANGUAGES` constant in `lib/languages.ts` is the single source of truth — any language addition only needs one change.
- **Failure visibility:** If `currency` is not passed as an i18n interpolation variable, the literal string `{{currency}}` appears in rendered output (visible to users). If `EmailLanguageSelector` receives an invalid `value` prop, the native `<select>` will default to the first option (ID) — no crash, just incorrect selection.
- **Redaction constraints:** None.
