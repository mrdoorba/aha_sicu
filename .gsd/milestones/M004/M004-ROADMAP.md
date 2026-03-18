# M004: Frontend i18n Completion

**Vision:** Every visible UI string routes through locale files. Switching language changes everything. A translator edits one JSON file per language — nothing else.

## Success Criteria

- Switching to TH renders zero Indonesian strings on any page
- Switching to EN renders zero Indonesian strings on any page
- `rg` for common Indonesian words in non-test, non-locale source returns zero hits
- `rg "id-ID"` in non-test, non-locale source returns zero hits
- All frontend tests pass (602+ baseline)
- A translator only needs to edit their `{lang}.json` to fully localize the app

## Key Risks / Unknowns

- `fields.ts` label mechanism change touches 8 form components — any missed update breaks a form
- Test assertions on hardcoded Indonesian text will break during extraction — must update in lockstep

## Proof Strategy

- fields.ts mechanism risk → retire in S02 by proving all 8 forms render translated labels and tests pass
- test breakage risk → retire in S01/S02 by updating tests per-slice as strings are extracted

## Verification Classes

- Contract verification: `rg` sweep for hardcoded Indonesian, `rg "id-ID"` sweep, test suite pass
- Integration verification: none (purely frontend)
- Operational verification: none
- UAT / human verification: switch language and visually confirm no stray Indonesian text

## Milestone Definition of Done

This milestone is complete only when all are true:

- All 4 un-i18n'd components use `t()` for every visible string
- All 8 date formatting sites use the active i18n locale
- All 51 field labels resolve through locale files
- `INDO_MONTHS` is replaced with English abbreviations
- `GENERIC_LABELS` uses i18n keys
- `rg` sweep confirms zero hardcoded Indonesian in source
- All frontend tests pass
- Success criteria re-checked against live behavior

## Requirement Coverage

- Covers: R027, R028, R029, R030, R031, R032
- Partially covers: none
- Leaves for later: none
- Orphan risks: none

## Slices

- [ ] **S01: Extract hardcoded strings from un-i18n'd components** `risk:medium` `depends:[]`
  > After this: Switch to TH → History table, Delete dialog, Downtime dialog, SelectField all render in Thai. Tests updated and passing.

- [ ] **S02: Locale-aware dates, field labels, and month constants** `risk:medium` `depends:[S01]`
  > After this: Switch to TH → dates show Thai locale formatting, all evaluation form field labels render in Thai, month abbreviations are English. Tests updated and passing.

- [ ] **S03: Verification sweep and test hardening** `risk:low` `depends:[S01,S02]`
  > After this: `rg` sweep for Indonesian text in source returns zero. All frontend tests pass. Translator can edit one JSON file per language to fully localize the app.

## Boundary Map

### S01 → S02

Produces:
- Locale mapping utility `lib/localeMap.ts` — `getIntlLocale(i18nLang)` function mapping i18next codes to Intl locale codes (id→id-ID, en→en-US, th→th-TH)
- ~40 new locale keys in `history.*`, `deleteDialog.*`, `downtime.*`, `common.select` across all 3 JSON files
- Established pattern for extracting hardcoded strings to locale files with test updates

Consumes:
- nothing (first slice)

### S01 → S03

Produces:
- Same as S01 → S02

Consumes:
- nothing (first slice)

### S02 → S03

Produces:
- ~60 new locale keys in `fields.*`, `generic.*`, `discount.*` across all 3 JSON files
- `MONTHS` constant (renamed from `INDO_MONTHS`) with English abbreviations
- `fields.ts` uses `labelKey` (i18n key) instead of `label` (hardcoded string)
- All 8 date formatting sites use `getIntlLocale()` from S01's locale mapping utility
- `GENERIC_LABELS` replaced with i18n keys

Consumes from S01:
- `lib/localeMap.ts` → `getIntlLocale()` for date formatting
- Pattern for locale key naming and test mock updates
