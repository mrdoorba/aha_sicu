## Why

UI Store ICU saat ini menggunakan bahasa campuran (Inggris dan Indonesia) secara tidak konsisten di seluruh komponen frontend. Ini membingungkan pengguna dan memberikan kesan aplikasi belum selesai. Perlu standarisasi ke Bahasa Indonesia menggunakan library i18n agar konsisten dan mudah di-maintain.

## What Changes

- Install dan setup `react-i18next` + `i18next` sebagai library internasionalisasi
- Buat file terjemahan Bahasa Indonesia (`locales/id.json`) berisi semua string UI
- Migrasi semua hardcoded string di ~15 komponen frontend ke `t()` function calls
- Terjemahkan semua string Inggris ke Bahasa Indonesia (istilah teknis umum seperti "Dashboard", "Email", "Brand" tetap Inggris)

## Capabilities

### New Capabilities
- `i18n-setup`: Setup react-i18next library, konfigurasi i18n, dan file terjemahan Bahasa Indonesia

### Modified Capabilities
<!-- Tidak ada perubahan requirement di level spec — ini murni perubahan presentasi/UI -->

## Impact

- **Frontend**: Semua file komponen yang mengandung hardcoded string (~15 file) akan dimodifikasi
- **Dependencies**: Tambah `react-i18next`, `i18next` ke package.json frontend
- **Backend**: Tidak ada perubahan
- **Breaking changes**: Tidak ada — perubahan murni kosmetik/presentasi
