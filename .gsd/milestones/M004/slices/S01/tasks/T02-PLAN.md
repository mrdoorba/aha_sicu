---
estimated_steps: 5
estimated_files: 5
---

# T02: Extract strings from DeleteEvaluationDialog

**Slice:** S01 — Extract hardcoded strings from un-i18n'd components
**Milestone:** M004

## Description

DeleteEvaluationDialog contains 8 hardcoded Indonesian strings: title, description (two sentences — keep as one key), confirmation prompt, placeholder, button labels, toast message, and aria-labels. The existing test file has ~12 assertions against these hardcoded strings that must be updated to check i18n keys instead. This follows the exact same pattern established in T01.

Relevant skill: `test` — for test update patterns.

## Steps

1. **Read the component and test file** to understand the current structure:
   - `frontend/src/components/evaluations/DeleteEvaluationDialog.tsx`
   - `frontend/src/components/evaluations/DeleteEvaluationDialog.test.tsx`

2. **Update `DeleteEvaluationDialog.tsx`**:
   - Add `import { useTranslation } from 'react-i18next';`
   - Inside the component, add `const { t } = useTranslation();`
   - Replace all hardcoded strings with `t()` calls:
     - `"Hapus Evaluasi"` → `t('deleteDialog.title')`
     - The description text (two Indonesian sentences about permanent deletion) → `t('deleteDialog.description')` — keep as ONE key, do not split
     - `"Ketik nama brand untuk konfirmasi:"` → `t('deleteDialog.confirmPrompt')`
     - `"Ketik nama brand di sini..."` → `t('deleteDialog.placeholder')`
     - `"Batal"` → `t('common.cancel')` (reuse existing key)
     - `"Hapus"` → `t('common.delete')` (added in T01) OR `t('deleteDialog.confirmButton')` if a more specific key is appropriate
     - `"Gagal menyalin nama brand"` → `t('deleteDialog.toast.copyFailed')`
     - `aria-label="Konfirmasi nama brand"` → `aria-label={t('deleteDialog.aria.confirmInput')}`
     - `aria-label="Salin nama brand"` → `aria-label={t('deleteDialog.aria.copyBrand')}`
   - Check for any other hardcoded strings in the component that the research may have missed.

3. **Add `deleteDialog.*` keys to all 3 locale JSON files** (`id.json`, `en.json`, `th.json`):
   - `"deleteDialog.title"`: `"Hapus Evaluasi"` / `"Delete Evaluation"` / `"ลบการประเมิน"`
   - `"deleteDialog.description"`: Full Indonesian description text / English equivalent / Thai equivalent
   - `"deleteDialog.confirmPrompt"`: `"Ketik nama brand untuk konfirmasi:"` / `"Type brand name to confirm:"` / `"พิมพ์ชื่อแบรนด์เพื่อยืนยัน:"`
   - `"deleteDialog.placeholder"`: `"Ketik nama brand di sini..."` / `"Type brand name here..."` / `"พิมพ์ชื่อแบรนด์ที่นี่..."`
   - `"deleteDialog.aria.confirmInput"`: `"Konfirmasi nama brand"` / `"Confirm brand name"` / `"ยืนยันชื่อแบรนด์"`
   - `"deleteDialog.aria.copyBrand"`: `"Salin nama brand"` / `"Copy brand name"` / `"คัดลอกชื่อแบรนด์"`
   - `"deleteDialog.toast.copyFailed"`: `"Gagal menyalin nama brand"` / `"Failed to copy brand name"` / `"คัดลอกชื่อแบรนด์ไม่สำเร็จ"`
   - Add any other keys found during step 2
   - IMPORTANT: Use **flat dot-notation keys** — `"deleteDialog.title"` not nested objects.

4. **Update `DeleteEvaluationDialog.test.tsx`**:
   - Add `vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key, i18n: { language: 'id', changeLanguage: vi.fn() } }) }))` at the **top level** (hoisted, not inside describe). Match the exact pattern used in T01's SelectField.test.tsx changes.
   - Update all ~12 assertions that check for hardcoded Indonesian text → change to the i18n key:
     - `getByText('Hapus Evaluasi')` → `getByText('deleteDialog.title')`
     - `getByText('Batal')` → `getByText('common.cancel')`
     - Any `getByRole('button', { name: 'Hapus' })` → `getByRole('button', { name: 'common.delete' })` or similar
     - `getByPlaceholderText('Ketik nama brand di sini...')` → `getByPlaceholderText('deleteDialog.placeholder')`
     - `toHaveAttribute('aria-label', 'Konfirmasi nama brand')` → `toHaveAttribute('aria-label', 'deleteDialog.aria.confirmInput')`
     - `toHaveAttribute('aria-label', 'Salin nama brand')` → `toHaveAttribute('aria-label', 'deleteDialog.aria.copyBrand')`
   - Read the test file carefully — there may be more assertions than listed above.

5. **Run tests** to verify:
   ```bash
   cd frontend && npm run test:run -- DeleteEvaluationDialog --reporter=verbose
   ```

## Must-Haves

- [ ] DeleteEvaluationDialog uses `t()` for all 8+ visible strings
- [ ] `common.cancel` reused (not duplicated)
- [ ] Description text is a single key (`deleteDialog.description`), not split
- [ ] All ~12 test assertions updated from Indonesian text to i18n keys
- [ ] `vi.mock('react-i18next')` added at top level of test file
- [ ] All `deleteDialog.*` keys added to id.json, en.json, th.json
- [ ] All DeleteEvaluationDialog tests pass

## Verification

- `cd frontend && npm run test:run -- DeleteEvaluationDialog --reporter=verbose` — all tests pass
- `rg "Hapus Evaluasi" frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` — returns no hits
- `rg "Ketik nama" frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` — returns no hits

## Inputs

- `frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` — component with 8 hardcoded strings
- `frontend/src/components/evaluations/DeleteEvaluationDialog.test.tsx` — existing test with ~12 assertions against Indonesian text
- `frontend/src/locales/id.json`, `en.json`, `th.json` — locale files (already extended in T01 with `common.select`, `common.delete`, `downtime.*`)
- T01 output: the `vi.mock('react-i18next')` pattern used in SelectField.test.tsx — match it exactly

## Expected Output

- `frontend/src/components/evaluations/DeleteEvaluationDialog.tsx` — modified, all strings use `t()`
- `frontend/src/components/evaluations/DeleteEvaluationDialog.test.tsx` — modified, mocks i18next, ~12 assertions updated
- `frontend/src/locales/id.json` — ~7 new `deleteDialog.*` keys
- `frontend/src/locales/en.json` — ~7 new `deleteDialog.*` keys
- `frontend/src/locales/th.json` — ~7 new `deleteDialog.*` keys

## Observability Impact

- **Runtime signal:** When language is switched via `LanguageToggle`, DeleteEvaluationDialog re-renders with translated text. The `useTranslation()` hook triggers re-render on `i18n.language` change.
- **Missing key visibility:** If a `deleteDialog.*` key is absent from a locale file, i18next renders the raw key string (e.g., `"deleteDialog.title"` appears literally on screen). This is by design — no silent failure.
- **Test observability:** The `vi.mock('react-i18next')` mock returns keys as-is, so test assertions directly verify key wiring. If a key name changes in the component but not the test, the test fails immediately.
- **Toast error path:** `deleteDialog.toast.copyFailed` is only triggered when clipboard API throws — inspect via Sonner toast UI or `toast.error` mock in tests.
