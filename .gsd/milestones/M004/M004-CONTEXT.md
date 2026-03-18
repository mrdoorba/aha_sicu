# M004: Frontend i18n Completion — Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

## Project Description

Complete i18n extraction for the entire frontend. The History page (and 3 other components) render hardcoded Indonesian text regardless of language selection. Additionally, 8 files use hardcoded `id-ID` date formatting, and `fields.ts` has 51 Indonesian form labels. After this milestone, every visible UI string routes through locale files, and a translator only edits their single `{lang}.json` file.

## Why This Milestone

M002 internationalized the evaluation detail page and email output, but left the "chrome" — history table, form labels, dialogs, date formatting — in hardcoded Indonesian. Thai users see a mix of Thai (from M002's work) and Indonesian (from un-extracted strings). This makes the app feel half-translated and unprofessional.

## User-Visible Outcome

### When this milestone is complete, the user can:

- Switch to TH or EN and see every page fully translated — no stray Indonesian text anywhere
- Hand a translator one JSON file per language and get full app localization without touching source code

### Entry point / environment

- Entry point: Browser at localhost (dev) or deployed URL
- Environment: local dev / browser
- Live dependencies involved: none

## Completion Class

- Contract complete means: `rg` sweep for hardcoded Indonesian in source returns zero hits; all tests pass
- Integration complete means: language toggle changes every visible string on every page
- Operational complete means: none

## Final Integrated Acceptance

To call this milestone complete, we must prove:

- Switching to TH renders zero Indonesian strings across History page, evaluation forms, dialogs, dates, and calculator results
- Switching to EN renders zero Indonesian strings across the same surfaces
- `rg` for common Indonesian words and `id-ID` in non-test, non-locale `.tsx`/`.ts` returns zero hits
- All frontend tests pass (602+ baseline)

## Risks and Unknowns

- `fields.ts` labels are consumed by 8 form components — changing the label mechanism requires touching all of them
- `GENERIC_LABELS` is used as fallback when `salesStartMonth` is null — must not break that fallback path
- Test count is high (602) — some tests assert hardcoded Indonesian strings and will break during extraction

## Existing Codebase / Prior Art

- `frontend/src/locales/{id,en,th}.json` — 590 keys each, well-structured, already the pattern for all i18n
- `frontend/src/i18n.ts` — i18next config, imports all 3 locale files
- `frontend/src/lib/languages.ts` — `LANGUAGES` array and `LanguageCode` type
- `frontend/src/components/evaluation/forms/fields.ts` — 51 field labels, `INDO_MONTHS`, `GENERIC_LABELS`
- `frontend/src/components/evaluation/forms/formUtils.ts` — `generateMonthLabels()` consumes `INDO_MONTHS` and `GENERIC_LABELS`
- `frontend/src/components/evaluation/forms/BusinessForm.tsx` — already uses `t()` for some labels but falls through to `field.label` for others
- Established mock pattern: `vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key) => key }) }))`

> See `.gsd/DECISIONS.md` for all architectural and pattern decisions — it is an append-only register; read it during planning, append to it during execution.

## Relevant Requirements

- R027 — Extract hardcoded strings from 4 un-i18n'd components
- R028 — Locale-aware date formatting across 8 files
- R029 — Extract 51 field labels and GENERIC_LABELS from fields.ts
- R030 — Replace INDO_MONTHS with English month abbreviations
- R031 — Single-file-per-language translator workflow (zero Indonesian in source)
- R032 — All tests pass after extraction

## Scope

### In Scope

- Extract all hardcoded Indonesian UI text from components/pages into locale files
- Add corresponding keys to all 3 locale files (id.json, en.json, th.json)
- Create locale mapping utility (i18next code → Intl locale: id→id-ID, en→en-US, th→th-TH)
- Fix all hardcoded `id-ID` date formatting to use active locale
- Replace `INDO_MONTHS` with English month abbreviations
- Extract `GENERIC_LABELS` to i18n keys
- Change `fields.ts` labels from hardcoded Indonesian to i18n keys resolved at render time
- Update all affected tests
- Update `DiscountResults.tsx` hardcoded labels

### Out of Scope / Non-Goals

- Backend i18n changes (backend already has full i18n support)
- New language additions (that's a separate effort)
- Changing the locale file format (JSON flat keys is the established pattern)
- Translating content that comes from the database (scoring messages already handled by M002)

## Technical Constraints

- Must preserve the `field.label` → form component rendering pipeline — change the data shape, not the rendering architecture
- `GENERIC_LABELS` fallback must still work when `salesStartMonth` is null
- Tests must use the established `t: (key) => key` mock pattern
- Locale files must stay in sync (same keys across all 3 files)

## Integration Points

- react-i18next `useTranslation` hook — already used in most components, needs adding to 4 more
- `Intl.DateTimeFormat` — needs locale parameter from i18n context
- `fields.ts` → 8 form components — label resolution mechanism changes

## Open Questions

- None — scope is clear and mechanical
