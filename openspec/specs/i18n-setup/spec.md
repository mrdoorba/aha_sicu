## ADDED Requirements

### Requirement: i18n library terinstall dan terkonfigurasi
Aplikasi frontend SHALL menggunakan `react-i18next` dan `i18next` sebagai library internasionalisasi. Konfigurasi i18n SHALL di-inisialisasi sebelum aplikasi di-render.

#### Scenario: Inisialisasi i18n saat app start
- **WHEN** aplikasi frontend dimuat
- **THEN** i18next ter-inisialisasi dengan bahasa default `id` (Indonesia)

#### Scenario: Konfigurasi i18n tersedia
- **WHEN** developer melihat `frontend/src/i18n.ts`
- **THEN** file berisi konfigurasi i18next dengan `lng: 'id'` dan resource terjemahan Indonesia

### Requirement: File terjemahan Bahasa Indonesia tersedia
Aplikasi SHALL memiliki file terjemahan `frontend/src/locales/id.json` yang berisi semua string UI dalam Bahasa Indonesia.

#### Scenario: Semua string UI ada di file terjemahan
- **WHEN** developer memeriksa `id.json`
- **THEN** file berisi semua string UI yang digunakan di komponen, dengan key menggunakan dot-notation berdasarkan lokasi komponen (e.g., `login.title`, `header.logout`)

### Requirement: Semua hardcoded string dimigrasikan ke t()
Semua string UI yang hardcoded di komponen React SHALL diganti dengan pemanggilan fungsi `t()` dari `react-i18next`.

#### Scenario: Komponen menggunakan t() untuk teks
- **WHEN** developer memeriksa komponen React manapun
- **THEN** tidak ada hardcoded string UI — semua menggunakan `t('key')` atau `useTranslation()` hook

#### Scenario: Teks ditampilkan dalam Bahasa Indonesia
- **WHEN** pengguna membuka halaman manapun di aplikasi
- **THEN** semua teks UI tampil dalam Bahasa Indonesia (kecuali istilah teknis umum seperti Dashboard, Email, Brand, Score, Login, Password, WhatsApp, CSV, SKU)

### Requirement: Istilah teknis umum tetap dalam Inggris
Istilah teknis yang sudah umum dipakai di Indonesia SHALL tetap dalam bahasa Inggris untuk naturalness.

#### Scenario: Istilah teknis tidak diterjemahkan
- **WHEN** pengguna melihat UI
- **THEN** kata seperti "Dashboard", "Email", "Brand", "Score", "Login", "Password", "WhatsApp", "CSV", "SKU" tetap dalam Inggris
