## Why

Change sebelumnya (`i18n-bahasa-indonesia`) berhasil migrasi ~15 komponen utama ke react-i18next, tapi ~16 komponen lain masih menggunakan hardcoded string (~150 string). Ini termasuk form evaluasi, halaman akun, konfigurasi rules, file upload, dan calculator results. UI masih inkonsisten — sebagian menggunakan `t()`, sebagian hardcoded.

## What Changes

- Migrasi ~16 komponen yang tersisa ke `t()` calls dari react-i18next
- Tambahkan ~150 translation key baru ke `locales/id.json`
- Komponen target:
  - **Evaluation forms**: EvaluationSections, SaveIndicator, OperationalForm, BusinessForm, VisitorsForm, ContentForm, PromoToolsForm, AdsForm, CampaignForm, CompetitionForm, ProductsStatusForm
  - **File upload & calculators**: FileUploadSection, CalculatorResultsSection
  - **Account management**: AccountsPage
  - **Rules**: RulesCategoryCard, PasswordConfirmDialog

## Capabilities

### New Capabilities
- `i18n-remaining-migration`: Migrasi sisa komponen hardcoded ke react-i18next — form evaluasi, halaman akun, rules config, file upload, dan calculator results

### Modified Capabilities
<!-- Tidak ada — react-i18next sudah terpasang dari change sebelumnya -->

## Impact

- **Frontend**: ~16 file komponen dimodifikasi, `id.json` bertambah ~150 key
- **Dependencies**: Tidak ada — react-i18next sudah terinstall
- **Backend**: Tidak ada perubahan
- **Tests**: Test files yang assert hardcoded string perlu diupdate
- **Breaking changes**: Tidak ada — perubahan murni presentasi
