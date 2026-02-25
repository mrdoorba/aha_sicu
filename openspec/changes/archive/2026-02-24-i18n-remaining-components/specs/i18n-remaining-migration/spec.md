## ADDED Requirements

### Requirement: Semua form evaluasi menggunakan t()
Semua komponen form evaluasi SHALL menggunakan `t()` dari react-i18next untuk string UI. Ini mencakup: EvaluationSections, SaveIndicator, OperationalForm, BusinessForm, VisitorsForm, ContentForm, PromoToolsForm, AdsForm, CampaignForm, CompetitionForm, ProductsStatusForm.

#### Scenario: Section headers menggunakan terjemahan
- **WHEN** pengguna membuka halaman evaluasi
- **THEN** semua step headers (Step 1-6) dan section titles ditampilkan via `t()` calls, bukan hardcoded string

#### Scenario: Save indicator menggunakan terjemahan
- **WHEN** status save berubah (saving, saved, error)
- **THEN** pesan status ditampilkan dalam Bahasa Indonesia via `t()` calls

#### Scenario: Aria labels untuk external links menggunakan terjemahan
- **WHEN** form menampilkan link ke Shopee Seller Center
- **THEN** aria-label menggunakan shared key `t('common.aria.openSellerCenter')` — tidak ada duplikasi hardcoded string

### Requirement: File upload section menggunakan t()
FileUploadSection dan CalculatorResultsSection SHALL menggunakan `t()` untuk semua label, status messages, dan button text.

#### Scenario: File upload labels menggunakan terjemahan
- **WHEN** pengguna melihat bagian file upload
- **THEN** nama file slot (Iklan Check Up V2A, Order Export, dll), calculator labels, dan toast messages ditampilkan via `t()`

#### Scenario: Calculator results menggunakan terjemahan
- **WHEN** pengguna melihat calculator results
- **THEN** section title, button text (Calculate, Recalculate All), status messages, dan error text ditampilkan via `t()`

### Requirement: Halaman akun menggunakan t()
AccountsPage SHALL menggunakan `t()` untuk semua string UI termasuk heading, table headers, dialog text, button labels, dan toast messages.

#### Scenario: Account management UI dalam Bahasa Indonesia
- **WHEN** pengguna membuka halaman manajemen akun
- **THEN** semua heading, tabel, dialog, button, dan toast message ditampilkan dalam Bahasa Indonesia via `t()`

### Requirement: Konfigurasi rules menggunakan t()
RulesCategoryCard dan PasswordConfirmDialog SHALL menggunakan `t()` untuk semua string UI termasuk label dictionary, table headers, badge text, dan dialog text.

#### Scenario: Rules card labels menggunakan terjemahan
- **WHEN** pengguna melihat scoring rules configuration
- **THEN** table headers (Metrik, Ambang Batas, Poin), badge text, dan status labels ditampilkan via `t()`

#### Scenario: Password confirm dialog menggunakan terjemahan
- **WHEN** pengguna diminta konfirmasi password untuk save rules
- **THEN** dialog title, description, button text, dan error messages ditampilkan dalam Bahasa Indonesia via `t()`

### Requirement: Translation keys ditambahkan ke id.json
Semua key baru SHALL ditambahkan ke file `locales/id.json` yang sudah ada, mengikuti konvensi dot-notation yang sudah established.

#### Scenario: Tidak ada missing keys
- **WHEN** developer menjalankan aplikasi setelah migrasi
- **THEN** tidak ada translation key yang missing — semua `t('key')` calls memiliki value di `id.json`

### Requirement: Test assertions diupdate
Semua test yang assert hardcoded string yang berubah SHALL diupdate untuk menggunakan string Bahasa Indonesia yang baru.

#### Scenario: Semua test pass setelah migrasi
- **WHEN** developer menjalankan `vitest run`
- **THEN** semua test pass tanpa failure
