# M002: Evaluation Results i18n

**Vision:** Make evaluation results fully translatable — the history detail page and email output render in the selected language, with an independent email language selector. Old evaluations fall back gracefully to Indonesian.

## Success Criteria

- Switching language toggle to EN/TH on the history detail page shows all scoring text in that language
- Email send dialogs across all pages have a language selector that defaults to UI language
- Email body renders in the chosen email language without changing the UI language
- Pre-i18n evaluations display Indonesian text correctly — no errors or blank fields
- Adding a 4th language requires only a locale JSON file and config additions

## Key Risks / Unknowns

- History page email (SendMailDialog) uses mailto: links — email body must be assembled entirely on frontend from i18n keys, unlike the dashboard's backend-rendered SMTP flow
- Pre-i18n evaluations may lack _i18n fields — fallback path must be verified with real data shapes

## Proof Strategy

- mailto email body assembly → retire in S02 by proving the frontend can rebuild a complete email body from stored i18n keys matching the backend's `_assemble_email_body` output
- Pre-i18n fallback → retire in S01 by proving evaluations without _i18n fields render correctly with raw Indonesian text

## Verification Classes

- Contract verification: existing frontend tests pass; new component tests for i18n rendering
- Integration verification: evaluation detail API returns marketplace; email body renders correctly in all 3 languages
- Operational verification: none
- UAT / human verification: visual check — switch language, view evaluation, verify text changes

## Milestone Definition of Done

This milestone is complete only when all are true:

- EvaluationDetailPage renders all scoring text through i18n with language reactivity
- All 3 email dialogs have language selector with correct defaults
- Email body reconstructs from i18n keys in the selected language
- Locale files contain no hardcoded currency codes
- Frontend types explicitly declare i18n fields
- All existing tests pass with zero regressions
- A documented checklist confirms adding a new language is locale-file-only

## Requirement Coverage

- Covers: R014, R015, R016, R017, R018, R019, R020, R021, R022
- Partially covers: none
- Leaves for later: none
- Orphan risks: none

## Slices

- [ ] **S01: EvaluationDetailPage i18n rendering** `risk:medium` `depends:[]`
  > After this: switch language to EN → open any evaluation in history → all scoring messages, category names, conclusions, closing messages render in English. Old evaluations without i18n keys show Indonesian text.

- [ ] **S02: Email language selector & i18n body rebuild** `risk:medium` `depends:[S01]`
  > After this: open any email send dialog (history, dashboard, evaluation page) → pick TH from language dropdown → email body preview renders in Thai while UI stays in current language.

- [ ] **S03: Locale hardcode cleanup & future-proofing** `risk:low` `depends:[S01]`
  > After this: all locale files use {{currency}} variable; a documented checklist confirms adding a 4th language requires only locale JSON + config changes; no hardcoded language assumptions remain.

## Boundary Map

### S01 → S02

Produces:
- `renderTranslatable()` usage pattern established in EvaluationDetailPage — all scoring text renders through i18n
- Frontend types (`RowScore`, `CategoryScore`, `EvaluationDetail`) with explicit `_i18n` fields
- Backend evaluation detail API returning `marketplace` field
- Proven fallback behavior for pre-i18n evaluations

Consumes:
- nothing (first slice)

### S01 → S03

Produces:
- EvaluationDetailPage using `renderTranslatable()` — depends on locale keys being correct
- Frontend types with i18n fields

Consumes:
- nothing (first slice)

### S02

Produces:
- `EmailLanguageSelector` component (reusable language dropdown for email dialogs)
- `buildI18nEmailBody(scoringData, t)` function that assembles email body from i18n keys
- Language selector integrated into SendMailDialog (history), SendEmailDialog (dashboard), EmailOutput (evaluation page)

Consumes from S01:
- Frontend types with explicit `_i18n` fields
- `renderTranslatable()` pattern for rendering i18n text
- `marketplace` field available in evaluation detail data

### S03

Produces:
- Fixed locale files (6 keys updated from hardcoded IDR to {{currency}})
- Documentation: "How to add a new language" checklist
- Verification that no hardcoded language assumptions remain

Consumes from S01:
- EvaluationDetailPage rendering through i18n (to verify currency variable works end-to-end)
