# S03: Email language selector & i18n body rebuild — UAT

**Milestone:** M002
**Written:** 2026-03-18

## UAT Type

- UAT mode: mixed (artifact-driven unit/component tests + human visual verification)
- Why this mode is sufficient: Unit tests prove email body assembly correctness and section ordering. Component tests prove language selector rendering and state management across all 3 dialogs. Human visual verification confirms the assembled email body looks correct in each language and the language selector UX is intuitive.

## Preconditions

- Frontend dev server running: `cd frontend && npm run dev`
- Backend API server running with a database containing at least one evaluation with i18n data (post-M001 evaluation) and one pre-i18n evaluation (no `_i18n` fields in score_breakdown)
- User is logged in
- Browser has access to all 3 pages: evaluation scoring page, evaluation history detail page, dashboard

## Smoke Test

Open the evaluation history detail page for any post-M001 evaluation → click "Send Email" → verify a language dropdown appears in the dialog with 3 options (ID, EN, TH) → switch to TH → verify the email body text changes to Thai.

## Test Cases

### 1. Dashboard SendEmailDialog — language selector controls email preview

1. Navigate to the dashboard page
2. Select a brand and trigger the email send dialog
3. Verify `EmailLanguageSelector` dropdown appears with current UI language pre-selected
4. Switch to "English (EN)"
5. Toggle "Preview" on
6. **Expected:** Email preview renders in English. The UI language (menus, buttons, labels) remains unchanged.

### 2. Dashboard SendEmailDialog — language flows to mutation payload

1. Open the dashboard email send dialog
2. Switch language to "ภาษาไทย (TH)"
3. Fill in recipients and click Send
4. **Expected:** The network request payload includes `"language": "th"`. Verify via browser DevTools Network tab.

### 3. History SendMailDialog — language selector rebuilds mailto body

1. Navigate to evaluation history, open a post-M001 evaluation detail page
2. Click the "Send Email" button to open SendMailDialog
3. Verify `EmailLanguageSelector` dropdown appears
4. Switch to "English (EN)"
5. **Expected:** The email body preview in the dialog changes to English text. Section headers show English translations (e.g. "🏥 Store Operational Performance" instead of Indonesian).

### 4. History SendMailDialog — subject updates with language

1. Open SendMailDialog on a post-M001 evaluation
2. Note the subject line
3. Switch language to "ภาษาไทย (TH)"
4. **Expected:** The subject line updates to Thai text (e.g. "รายงานสุขภาพร้าน" pattern). The "Kepada" field and dialog chrome remain in the UI language.

### 5. Evaluation page EmailOutput — language selector in scoring card

1. Navigate to the evaluation page (new evaluation flow)
2. Complete a scoring evaluation (or load one in progress that has reached the scoring result stage)
3. Scroll down to the "Email Output" card in the scoring section
4. Verify language selector dropdown appears next to the card header
5. Switch to "English (EN)"
6. **Expected:** Email subject and body text in the card update to English. The scoring tables and UI above remain in the current UI language.

### 6. EmailOutput — copy copies translated text

1. On the evaluation page EmailOutput card, switch language to TH
2. Click the "Salin" (Copy) button
3. Paste into a text editor
4. **Expected:** The pasted text is in Thai, matching what was displayed — not the original Indonesian text.

### 7. Currency interpolation in translated text

1. Open any evaluation for a THB marketplace brand
2. Navigate to the history detail page
3. Switch UI language to English
4. Look at scoring messages that reference currency (monthly sales pass/fail, competition product pass/fail)
5. **Expected:** Messages show "THB" (not "IDR") as the currency code. For example: "Monthly sales above THB 150,000" rather than "Monthly sales above IDR 150,000".

### 8. Locale files have no hardcoded IDR

1. In the terminal, run: `grep -c "IDR" frontend/src/locales/id.json frontend/src/locales/en.json frontend/src/locales/th.json`
2. **Expected:** All 3 files return `0`.

## Edge Cases

### Pre-i18n evaluation — SendMailDialog graceful fallback

1. Open a pre-i18n evaluation (created before M001/i18n, no `_i18n` fields in score_breakdown)
2. Open SendMailDialog
3. Language selector is visible
4. Switch to TH
5. **Expected:** Email body remains in Indonesian (raw original text). No errors, no blank fields. The language selector has no visible effect because there's no i18n data to translate.

### Pre-i18n evaluation — EmailOutput hides language selector

1. On the evaluation page, if viewing results for a pre-i18n dataset (scoringResult is null/absent)
2. Scroll to EmailOutput card
3. **Expected:** No language selector dropdown appears. Subject and body show the original Indonesian text.

### Dialog close resets language

1. Open any email dialog
2. Switch language to TH
3. Close the dialog (Cancel or X)
4. Re-open the same dialog
5. **Expected:** Language selector resets to the current UI language, not TH.

### Backend preview with language param

1. In the browser or via curl, request the preview endpoint with a language param: `GET /api/v1/email/preview/{evaluation_id}?language=th`
2. **Expected:** The preview HTML renders in Thai. Without the `?language=th` param, it defaults to the user's profile language.

## Failure Signals

- Language selector missing from any of the 3 email dialogs
- Switching language doesn't update the email body preview text
- Email body shows mixed languages (some sections translated, others not)
- "{{currency}}" appears literally in any rendered text (means interpolation variable not being passed)
- "IDR" appears in locale file grep results
- Pre-i18n evaluations show blank/empty email body instead of original Indonesian text
- Copy button copies original Indonesian text even after switching to another language
- Console errors when switching languages in any dialog
- Full test regression shows failures (expect 602 pass, 0 fail)

## Requirements Proved By This UAT

- R015 — All email send dialogs include a language dropdown that lets the user choose the email language independently of the UI language
- R016 — Email body content is reconstructed from stored i18n structured data at render time in the chosen language
- R017 — All locale translation strings that reference currency use {{currency}} interpolation variable instead of hardcoded "IDR"
- R019 (partial) — Pre-i18n evaluations display original Indonesian text in email dialogs — no errors or blank fields

## Not Proven By This UAT

- R020 — Adding a 4th language requires only locale-file-only changes (deferred to S04 documentation and verification)
- Backend email HTML rendering in the selected language (preview endpoint language param is pass-through; full render path verification requires backend integration testing)
- Cross-browser compatibility of the native `<select>` dropdown
- Performance under large score_breakdown payloads (not expected to be an issue given typical data sizes)

## Notes for Tester

- The `EmailLanguageSelector` uses a native `<select>` element, not a custom dropdown. It looks like a standard browser dropdown.
- The "Salin" button label is Indonesian for "Copy" — this is the expected label when UI is in Indonesian.
- DialogContent accessibility warnings about missing `Description` may appear in browser console — these are pre-existing and not related to S03 changes.
- When testing currency interpolation (test case 7), you need a THB marketplace evaluation. If only IDR evaluations exist, the currency will correctly show "IDR" via interpolation — the key proof is that `{{currency}}` doesn't appear literally.
- The backend preview endpoint test (edge case 4) requires the backend server to be running and a valid evaluation ID. Use an evaluation ID from the database.
