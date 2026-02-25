## Context

Frontend Store ICU menggunakan hardcoded string langsung di ~15 komponen React. Teks campuran Inggris dan Indonesia tersebar di seluruh UI. Tidak ada mekanisme terpusat untuk mengelola terjemahan.

## Goals / Non-Goals

**Goals:**
- Setup `react-i18next` sebagai library i18n
- Satu file terjemahan Bahasa Indonesia (`id.json`) berisi semua string UI
- Migrasi semua hardcoded string ke `t()` calls
- UI konsisten dalam Bahasa Indonesia (istilah teknis umum tetap Inggris)

**Non-Goals:**
- Multi-language support (hanya Bahasa Indonesia untuk sekarang)
- Server-side i18n / backend translations
- Dynamic language switching UI

## Decisions

### 1. Library: `react-i18next` + `i18next`
**Rationale**: Paling populer, API simpel (`t('key')`), ekosistem besar, docs lengkap.
**Alternatives considered**: `react-intl` (API lebih verbose), `LinguiJS` (perlu build step tambahan).

### 2. Struktur file terjemahan: flat JSON dengan dot-notation keys
**Rationale**: Simpel dan mudah dicari. Satu file `id.json` cukup untuk skala aplikasi ini.

```
frontend/src/locales/id.json
```

Key naming convention — berdasarkan lokasi komponen:
```json
{
  "login.title": "Login Store ICU",
  "login.loggingIn": "Sedang masuk...",
  "header.logout": "Keluar",
  "brands.search": "Cari brand...",
  "evaluation.finalScore": "Skor Akhir"
}
```

### 3. i18n config: file terpisah, import di main.tsx
**Rationale**: Pattern standar react-i18next. Config di `frontend/src/i18n.ts`, di-import sebelum app render.

```
frontend/src/i18n.ts          — konfigurasi i18next
frontend/src/locales/id.json  — terjemahan Indonesia
```

### 4. Bahasa default: `id` (Indonesia), tanpa fallback language
**Rationale**: Aplikasi single-language. Tidak perlu fallback ke Inggris.

### 5. Istilah teknis yang tetap Inggris
Kata-kata yang sudah umum dipakai dan tidak perlu diterjemahkan:
- Dashboard, Email, Brand, Score, Login, Password
- WhatsApp, CSV, SKU
- Nama produk, nama brand (data dari backend)

## Risks / Trade-offs

- **[Bundle size +~15KB]** → Acceptable untuk manfaat maintainability yang didapat
- **[Migrasi banyak file sekaligus]** → Mitigasi: migrasi per komponen secara atomic, test setelah setiap perubahan
- **[Key typo tidak terdeteksi saat compile]** → Mitigasi: react-i18next menampilkan key sebagai fallback, mudah terlihat saat testing
