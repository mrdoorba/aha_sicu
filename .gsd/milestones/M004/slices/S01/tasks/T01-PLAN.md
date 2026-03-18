---
estimated_steps: 8
estimated_files: 9
---

# T01: Extract strings from SelectField and DowntimeWarningDialog, create localeMap.ts

**Slice:** S01 — Extract hardcoded strings from un-i18n'd components
**Milestone:** M004

## Description

This task proves the i18n extraction pattern on the two smallest target components and creates the `localeMap.ts` boundary deliverable that S02 needs for date formatting. SelectField has exactly 1 hardcoded string (`"Pilih..."`). DowntimeWarningDialog has 5 hardcoded strings and no existing test file — a new test must be created. `localeMap.ts` is a trivial 3-mapping utility but is a key boundary contract for downstream work.

Relevant skill: `test` — for test generation patterns and verification.

## Steps

1. **Create `frontend/src/lib/localeMap.ts`** — Export a `getIntlLocale(lang: string): string` function that maps `id` → `id-ID`, `en` → `en-US`, `th` → `th-TH`, with `id-ID` as the default fallback. This should be ~10 lines.

2. **Create `frontend/src/lib/localeMap.test.ts`** — Test all 3 mappings plus the fallback case. Follow the existing vitest patterns in the project (import from vitest, `describe`/`it`/`expect`).

3. **Update `frontend/src/components/evaluation/forms/SelectField.tsx`**:
   - Add `import { useTranslation } from 'react-i18next';`
   - Inside the component, add `const { t } = useTranslation();`
   - Replace the hardcoded placeholder `"Pilih..."` with `t('common.select')`
   - The `label` prop is NOT this task's concern (that's S02 scope) — only change the placeholder.

4. **Update `frontend/src/components/evaluation/forms/SelectField.test.tsx`**:
   - Add `vi.mock('react-i18next')` at the **top level** of the file (hoisted, not inside describe). Use the mock pattern: `vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key, i18n: { language: 'id', changeLanguage: vi.fn() } }) }))`.
   - Find the existing mock patterns in the codebase first — check files like `EvaluationHistoryTable.test.tsx` or other test files that already mock `react-i18next` — and match that exact pattern.
   - Update the assertion on line ~25 that checks for placeholder `'Pilih...'` → change expected value to `'common.select'`.
   - The test checks `label` text `'Status Toko'` — this comes from the test's own prop, NOT from the component, so do NOT change it.

5. **Update `frontend/src/components/DowntimeWarningDialog.tsx`**:
   - Add `import { useTranslation } from 'react-i18next';`
   - Inside the component, add `const { t } = useTranslation();`
   - Extract these strings to i18n keys:
     - Title: `"Sistem Tidak Tersedia"` → `t('downtime.title')`
     - Description text: The description contains embedded bold text with the time range "00:00 - 08:00 WIB (UTC+7)". Use `t('downtime.description')` for the text, using `Trans` component from react-i18next if the description has inline JSX formatting, OR use `t()` with interpolation `{{timeRange}}` if the bold text can be restructured. Check the actual JSX structure of the component to decide the right approach. If it's simple text with a `<strong>` tag inside, prefer the `Trans` component pattern. If it's plain text, use `t()` with interpolation.
     - Dismiss button: `"Mengerti"` → `t('downtime.dismiss')`
   - Any other visible strings in the component should also be extracted.

6. **Create `frontend/src/components/DowntimeWarningDialog.test.tsx`**:
   - Follow the established test file pattern from `DeleteEvaluationDialog.test.tsx` (structure, imports, render approach).
   - Mock `react-i18next` at top level (same pattern as step 4).
   - Write tests:
     - `should render downtime title when open` — render with open=true, assert `downtime.title` is visible
     - `should render dismiss button when open` — assert `downtime.dismiss` button is visible
     - `should call onClose when dismiss button clicked` — click dismiss, verify `onClose` callback fires
     - `should not render when closed` — render with open=false, assert title is not visible
   - Check the component's props interface to understand what props are needed (likely `open: boolean` and `onClose: () => void`).

7. **Add locale keys to all 3 JSON files** (`frontend/src/locales/id.json`, `en.json`, `th.json`):
   - `"common.select"`: `"Pilih..."` / `"Select..."` / `"เลือก..."`
   - `"common.delete"`: `"Hapus"` / `"Delete"` / `"ลบ"`
   - `"downtime.title"`: `"Sistem Tidak Tersedia"` / `"System Unavailable"` / `"ระบบไม่พร้อมใช้งาน"`
   - `"downtime.description"`: Indonesian description text / English equivalent / Thai equivalent (preserve any interpolation variables)
   - `"downtime.dismiss"`: `"Mengerti"` / `"Understood"` / `"เข้าใจแล้ว"`
   - IMPORTANT: Locale files use **flat dot-notation keys** (not nested objects). Add keys as `"downtime.title": "..."` not as `{ "downtime": { "title": "..." } }`.

8. **Run tests** to verify everything passes:
   ```bash
   cd frontend && npm run test:run -- SelectField DowntimeWarningDialog localeMap --reporter=verbose
   ```

## Must-Haves

- [ ] `localeMap.ts` exports `getIntlLocale()` with 3 mappings + fallback, with passing test
- [ ] SelectField uses `t('common.select')` instead of `"Pilih..."`
- [ ] SelectField.test.tsx has `vi.mock('react-i18next')` and updated assertion
- [ ] DowntimeWarningDialog uses `t()` for all 5 visible strings
- [ ] DowntimeWarningDialog.test.tsx exists with passing tests covering open/closed/dismiss
- [ ] All new keys added to id.json, en.json, th.json with correct translations
- [ ] All tests pass

## Verification

- `cd frontend && npm run test:run -- SelectField --reporter=verbose` — SelectField tests pass
- `cd frontend && npm run test:run -- DowntimeWarningDialog --reporter=verbose` — DowntimeWarningDialog tests pass
- `cd frontend && npm run test:run -- localeMap --reporter=verbose` — localeMap tests pass
- `rg "Pilih\.\.\." frontend/src/components/evaluation/forms/SelectField.tsx` — returns no hits
- `rg "Sistem Tidak" frontend/src/components/DowntimeWarningDialog.tsx` — returns no hits

## Observability Impact

- **New signal:** `localeMap.ts` is a pure utility — no runtime logging, no side effects. Observable only via Intl.DateTimeFormat output using the mapped locale.
- **Inspection:** To verify i18n wiring, switch language in the app and observe SelectField placeholder and DowntimeWarningDialog strings change. Missing keys render as literal key strings (e.g., `"common.select"` visible in UI = locale JSON missing the key).
- **Failure state:** If `react-i18next` is misconfigured, `t()` returns the key as-is. Tests catch this by asserting key strings appear (mocked `t` returns keys). If `localeMap.ts` receives an unknown language code, it returns `'id-ID'` (safe default, no crash).
- **Test observability:** New test file `DowntimeWarningDialog.test.tsx` covers open/closed/dismiss states. `localeMap.test.ts` covers all 3 mappings + fallback. SelectField tests updated for i18n key assertion.

## Inputs

- `frontend/src/components/evaluation/forms/SelectField.tsx` — component with 1 hardcoded string
- `frontend/src/components/evaluation/forms/SelectField.test.tsx` — existing test with placeholder assertion
- `frontend/src/components/DowntimeWarningDialog.tsx` — component with 5 hardcoded strings, no test
- `frontend/src/locales/id.json`, `en.json`, `th.json` — existing locale files to extend
- Existing `vi.mock('react-i18next')` pattern from other test files (e.g., search for files that already mock it)

## Expected Output

- `frontend/src/lib/localeMap.ts` — new file, ~10 lines, exports `getIntlLocale()`
- `frontend/src/lib/localeMap.test.ts` — new file, tests 3 mappings + fallback
- `frontend/src/components/evaluation/forms/SelectField.tsx` — modified, uses `t('common.select')`
- `frontend/src/components/evaluation/forms/SelectField.test.tsx` — modified, mocks i18next, updated assertion
- `frontend/src/components/DowntimeWarningDialog.tsx` — modified, uses `t()` for all strings
- `frontend/src/components/DowntimeWarningDialog.test.tsx` — new file, 4 tests covering render/dismiss/closed
- `frontend/src/locales/id.json` — ~7 new keys added
- `frontend/src/locales/en.json` — ~7 new keys added
- `frontend/src/locales/th.json` — ~7 new keys added
