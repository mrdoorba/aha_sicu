---
estimated_steps: 6
estimated_files: 5
---

# T02: Create buildI18nEmailBody utility + wire SendEmailDialog language selector

**Slice:** S03 — Email language selector & i18n body rebuild
**Milestone:** M002

## Description

This task builds the core email body assembly function that mirrors the backend's `_assemble_email_body` and wires the language selector into the dashboard's `SendEmailDialog` (the simplest of the three dialogs, since its backend already handles language). Also adds an optional `language` query param to the backend preview endpoint so the dashboard preview renders in the selected email language.

**Relevant installed skill:** `test` — for generating unit tests.

## Steps

1. **Create `frontend/src/utils/buildI18nEmailBody.ts`** — Export two functions:

   **`buildI18nEmailSubject(brandName: string, period: string, t: TFunction): string`**
   - Returns `t('sendMailUtils.subject', { brandName, period })` using the provided `t` function (which will be `i18n.getFixedT(selectedLang)`)

   **`buildI18nEmailBody(categoryScores: CategoryScore[], scoringSummary: ScoringConclusionData | null, t: TFunction): string`**
   
   Where `ScoringConclusionData` is a type for the scoring_summary shape:
   ```ts
   interface ScoringConclusionData {
     conclusion: string;
     conclusion_i18n?: TranslatableText[];
     marketing_estimation?: string;
     marketing_estimation_i18n?: TranslatableText;
     marketing_percentage?: string;
     marketing_budget?: string;
     marketing_budget_i18n?: TranslatableText;
     closing_message?: string;
     closing_message_i18n?: TranslatableText;
   }
   ```
   
   The function must mirror `_assemble_email_body` from `backend/app/calculators/scoring/computations.py` (lines ~328-440). **Critical section ordering:**
   
   1. 📊 Operational — category `"Kesehatan Operasional Toko"`, all rows
   2. 📈 Business/Sales — category `"Bisnis Analisis"`, rows 13 & 20 only
   3. 👥 Visitors — category `"Tinjauan Pengunjung"`, rows 28 & 29 only
   4. 🏷️ Promo Tools — category `"Promo Toko"`, rows 34-41 + rows 42 & 43
   5. 📦 Products & Status — category `"Jumlah Produk & Status Toko"`, all rows
   6. 📣 Ads — category `"Data Iklan"`, rows 50, 51, 52, 53 only
   7. 🎯 Campaign — category `"Partisipasi Campaign"`, row 57 only
   8. 🏆 Competition — category `"Kompetisi TOP Produk"`, all rows
   9. 📋 Conclusion — from `scoringSummary.conclusion_i18n` (array of TranslatableText), fallback to `scoringSummary.conclusion` raw string
   10. 📌 Marketing estimation — from `scoringSummary.marketing_estimation_i18n`, fallback to raw
   11. Marketing budget — from `scoringSummary.marketing_budget_i18n`, fallback to raw
   12. Closing message — from `scoringSummary.closing_message_i18n`, fallback to raw
   
   For each row message, use `renderTranslatable(row.message, row.message_i18n, t)` from `utils/renderTranslatable.ts`.
   For section headers, use `CATEGORY_MAP` to find the i18n label key, then `t(labelKey)`. Prefix with the emoji. Fall back to the Indonesian backend category name if not in CATEGORY_MAP.
   
   **Important: The `CATEGORY_MAP` section header lookup maps backend Indonesian category names to i18n keys. The emoji prefixes are hardcoded constants in the function (matching the backend exactly).**

   Also handle the case where `scoringSummary` is null (pre-i18n evaluations) — just return row messages without conclusion/marketing/closing sections.

2. **Also export a helper type** `ScoringConclusionData` from the same file, since `EmailOutput` and `SendMailDialog` will both need it.

3. **Write `frontend/src/utils/buildI18nEmailBody.test.ts`** — Comprehensive unit tests:
   - Test with mock `categoryScores` containing `_i18n` fields → body contains translated messages (use a mock `t` that returns `"[translated: {key}]"`)
   - Test fallback: `categoryScores` without `_i18n` fields → body contains raw `message` strings
   - Test section ordering: verify sections appear in the correct order
   - Test row filtering: business section only includes rows 13 & 20, visitors only 28 & 29, etc.
   - Test with `scoringSummary` containing conclusion_i18n → conclusion section appears translated
   - Test with null `scoringSummary` → no conclusion/marketing/closing sections
   - Test `buildI18nEmailSubject` returns translated subject

4. **Wire `SendEmailDialog` with language selector** — In `frontend/src/components/dashboard/SendEmailDialog.tsx`:
   - Import `EmailLanguageSelector` from `../shared/EmailLanguageSelector`
   - Add `const [emailLanguage, setEmailLanguage] = useState(i18n.language)`
   - Render `<EmailLanguageSelector value={emailLanguage} onChange={setEmailLanguage} />` in the dialog (above the note section or between brand summary and note)
   - Update `handleSend` to pass `language: emailLanguage` instead of `language: i18n.language` in the mutation payload
   - Update `fetchPreview` to append `language=${emailLanguage}` to the preview URL query params (alongside existing `note` param)
   - Reset `emailLanguage` to `i18n.language` in `handleClose`

5. **Add `language` query param to backend preview endpoint** — In `backend/app/modules/email/router.py`, function `preview_email_endpoint`:
   - Add `language: str | None = Query(default=None)` parameter
   - Change the language resolution line to: `lang = language or current_user.get("language", "id")`
   - Use `lang` instead of `language` in the `render_email_html` call

6. **Update `frontend/src/components/dashboard/SendEmailDialog.test.tsx`** — Add tests:
   - Language selector renders in the dialog
   - Mutation payload includes the selected language
   - When language is changed, the preview URL includes the language param

## Must-Haves

- [ ] `buildI18nEmailBody` produces correct section-ordered body matching backend `_assemble_email_body`
- [ ] `buildI18nEmailBody` falls back to raw messages when `_i18n` fields are absent
- [ ] `buildI18nEmailSubject` returns translated subject using provided `t` function
- [ ] `SendEmailDialog` renders `EmailLanguageSelector`
- [ ] Selected email language flows to mutation payload and preview URL
- [ ] Backend preview endpoint accepts optional `language` query param
- [ ] All unit tests pass; full regression passes

## Verification

- `cd frontend && npx vitest run src/utils/buildI18nEmailBody.test.ts --reporter=verbose` — all unit tests pass
- `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx --reporter=verbose` — existing + new tests pass
- `cd frontend && npx vitest run --reporter=verbose 2>&1 | tail -5` — full regression: 0 failures
- Verify backend change compiles: `PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -c "from app.modules.email.router import preview_email_endpoint; print('OK')"`

## Inputs

- T01 output: `EmailLanguageSelector` component in `frontend/src/components/shared/EmailLanguageSelector.tsx`; `LANGUAGES` in `frontend/src/lib/languages.ts`; locale files with `{{currency}}` instead of IDR
- `frontend/src/utils/renderTranslatable.ts` — `renderTranslatable()` function and `TranslatableText` type
- `frontend/src/lib/categoryMap.ts` — `CATEGORY_MAP` for section header translation
- `frontend/src/hooks/useScoring.ts` — `CategoryScore`, `RowScore`, `ScoringResult` types
- `backend/app/calculators/scoring/computations.py` lines 328-440 — reference `_assemble_email_body` implementation for section ordering and row filters
- `frontend/src/components/dashboard/SendEmailDialog.tsx` — current dialog to wire
- `backend/app/modules/email/router.py` — preview endpoint to add language param

## Expected Output

- `frontend/src/utils/buildI18nEmailBody.ts` — new file with `buildI18nEmailBody`, `buildI18nEmailSubject`, `ScoringConclusionData` type
- `frontend/src/utils/buildI18nEmailBody.test.ts` — new comprehensive test file
- `frontend/src/components/dashboard/SendEmailDialog.tsx` — modified with language selector
- `frontend/src/components/dashboard/SendEmailDialog.test.tsx` — updated with new tests
- `backend/app/modules/email/router.py` — modified with optional `language` query param

## Observability Impact

- **SendEmailDialog language selector:** The `data-testid="email-language-select"` dropdown is visible in the dashboard email dialog; its value flows to both the mutation `language` field and the preview endpoint `?language=` query param.
- **Backend preview endpoint:** Accepts `?language=th|en|id` query param. If the param is missing, falls back to user profile language. Inspect with: `curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/email/preview/123?language=th"`.
- **buildI18nEmailBody:** Pure function — no runtime signals. Test coverage verifies section ordering, row filtering, and i18n fallback. Run `npx vitest run src/utils/buildI18nEmailBody.test.ts` to validate.
- **Failure visibility:** If the email body renders in the wrong language, the preview iframe in SendEmailDialog will show mismatched content immediately. Missing `_i18n` fields cause graceful fallback to Indonesian raw strings (visible but not broken).
