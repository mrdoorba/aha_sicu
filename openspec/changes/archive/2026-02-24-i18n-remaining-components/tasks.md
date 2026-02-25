## 1. Form Evaluasi — Section Headers & Save

- [x] 1.1 Migrasi `EvaluationSections.tsx` — step headers (Step 1-6), category labels, save buttons, error messages
- [x] 1.2 Migrasi `SaveIndicator.tsx` — saving/saved/error messages, retry button

## 2. Form Evaluasi — Individual Forms

- [x] 2.1 Migrasi `OperationalForm.tsx` — section title, aria labels
- [x] 2.2 Migrasi `BusinessForm.tsx` — section title, start month selector, average label, aria labels
- [x] 2.3 Migrasi `VisitorsForm.tsx` — section title, returning visitors label, aria labels
- [x] 2.4 Migrasi `ContentForm.tsx` — section title
- [x] 2.5 Migrasi `PromoToolsForm.tsx` — section title, usage/effectiveness labels, aria labels
- [x] 2.6 Migrasi `AdsForm.tsx` — section title, ROAS label, ratio labels, aria labels
- [x] 2.7 Migrasi `CampaignForm.tsx` — section title, participation label, aria labels
- [x] 2.8 Migrasi `CompetitionForm.tsx` — section title, field labels, competitive/not competitive text
- [x] 2.9 Migrasi `ProductsStatusForm.tsx` — section title, aria labels

## 3. File Upload & Calculator

- [x] 3.1 Migrasi `FileUploadSection.tsx` — file slot names, format labels, calculator descriptions, toast messages
- [x] 3.2 Migrasi `CalculatorResultsSection.tsx` — section title, calculator labels, button text, status/error messages

## 4. Halaman Akun

- [x] 4.1 Migrasi `AccountsPage.tsx` — heading, table headers, dialogs (create/reset/delete), button labels, toast messages

## 5. Rules Configuration

- [x] 5.1 Migrasi `RulesCategoryCard.tsx` — table headers, badge text, point labels, store status labels
- [x] 5.2 Migrasi `PasswordConfirmDialog.tsx` — dialog title/description, button text, error messages

## 6. Translation Keys

- [x] 6.1 Tambahkan semua key baru ke `locales/id.json` — pastikan setiap `t()` call yang baru punya value

## 7. Verifikasi

- [x] 7.1 Update test assertions yang terpengaruh — ganti hardcoded string di test files
- [x] 7.2 Jalankan `vitest run` — pastikan semua test pass
- [x] 7.3 Jalankan `tsc --noEmit` dan `npm run lint` — pastikan tidak ada error
- [x] 7.4 Build production (`npm run build`) — pastikan berhasil
